"""
FastAPI backend for EntryDesk
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
import os
import tempfile

from database import get_db, Athlete, Coach, get_next_unique_id, init_db
from excel_utils import process_excel_file

app = FastAPI(title="EntryDesk API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_bool(s):
    """
    Parse a string to a boolean value.
    Accepts: true/false, 1/0, yes/no, y/n, on/off (case-insensitive).
    
    Args:
        s: String or value to parse
        
    Returns:
        True if the value represents a truthy value, False otherwise
    """
    return str(s).strip().lower() in {"1", "true", "yes", "y", "on"}


# Write lock configuration
ENTRYDESK_WRITES_ENABLED = parse_bool(os.getenv("ENTRYDESK_WRITES_ENABLED", "true"))


# Pydantic models
class AthleteCreate(BaseModel):
    name: str
    dob: date
    dojo: str
    belt: str
    day: str


class AthleteResponse(BaseModel):
    id: int
    unique_id: int
    name: str
    dob: date
    dojo: str
    belt: str
    day: str
    created_at: datetime

    class Config:
        from_attributes = True


class CoachResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    accepted: int
    rejected: int
    errors: List[str]
    athletes: List[AthleteResponse]


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


# API Endpoints
@app.get("/")
def root():
    return {"message": "EntryDesk API is running"}


@app.get("/api/athletes/{coach_id}", response_model=List[AthleteResponse])
def get_athletes(coach_id: int, db: Session = Depends(get_db)):
    """Get all athletes for a coach"""
    athletes = db.query(Athlete).filter(Athlete.coach_id == coach_id).all()
    return athletes


@app.post("/api/athletes/{coach_id}", response_model=AthleteResponse)
def create_athlete(coach_id: int, athlete: AthleteCreate, db: Session = Depends(get_db)):
    """Create a new athlete"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        raise HTTPException(status_code=403, detail="Registrations are closed")
    
    # Verify coach exists
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    # Generate unique ID
    unique_id = get_next_unique_id(db)
    
    # Create athlete
    db_athlete = Athlete(
        unique_id=unique_id,
        name=athlete.name,
        dob=athlete.dob,
        dojo=athlete.dojo,
        belt=athlete.belt,
        day=athlete.day,
        coach_id=coach_id
    )
    db.add(db_athlete)
    db.commit()
    db.refresh(db_athlete)
    
    return db_athlete


@app.post("/api/upload/{coach_id}", response_model=UploadResponse)
async def upload_excel(
    coach_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload Excel file with athletes"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        raise HTTPException(status_code=403, detail="Registrations are closed")
    
    # Verify coach exists
    coach = db.query(Coach).filter(Coach.id == coach_id).first()
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Process Excel file
        df, errors = process_excel_file(tmp_file_path)
        
        accepted = 0
        rejected = len(errors)
        created_athletes = []
        
        # Add valid athletes to database
        for _, row in df.iterrows():
            try:
                # Check for duplicate
                from database import check_duplicate_athlete
                athlete_name = str(row['name']).strip()
                athlete_dob = row['dob'].date() if hasattr(row['dob'], 'date') else row['dob']
                athlete_dojo = str(row['dojo']).strip()
                
                existing = check_duplicate_athlete(db, athlete_name, athlete_dob, athlete_dojo, coach_id)
                if existing:
                    errors.append(f"Row skipped: Duplicate athlete '{athlete_name}' (ID: {existing.unique_id})")
                    rejected += 1
                    continue
                
                unique_id = get_next_unique_id(db)
                
                # Get gender (now required, already validated and normalized)
                athlete_gender = str(row['gender']).strip()
                
                db_athlete = Athlete(
                    unique_id=unique_id,
                    name=athlete_name,
                    dob=athlete_dob,
                    dojo=athlete_dojo,
                    belt=str(row['belt']).strip(),
                    day=str(row['day']).strip(),
                    gender=athlete_gender,
                    coach_id=coach_id
                )
                db.add(db_athlete)
                db.commit()
                db.refresh(db_athlete)
                created_athletes.append(db_athlete)
                accepted += 1
            except Exception as e:
                db.rollback()
                errors.append(f"Error adding {row.get('name', 'unknown')}: {str(e)}")
                rejected += 1
        
        return UploadResponse(
            accepted=accepted,
            rejected=rejected,
            errors=errors,
            athletes=created_athletes
        )
    
    finally:
        # Clean up temp file
        os.unlink(tmp_file_path)


@app.delete("/api/athletes/{athlete_id}")
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    """Delete an athlete"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        raise HTTPException(status_code=403, detail="Registrations are closed")
    
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    db.delete(athlete)
    db.commit()
    return {"message": "Athlete deleted successfully"}


@app.get("/api/stats/{coach_id}")
def get_stats(coach_id: int, db: Session = Depends(get_db)):
    """Get statistics for a coach"""
    athletes = db.query(Athlete).filter(Athlete.coach_id == coach_id).all()
    
    total = len(athletes)
    saturday = sum(1 for a in athletes if a.day == 'Saturday')
    sunday = sum(1 for a in athletes if a.day == 'Sunday')
    
    belts = {}
    for athlete in athletes:
        belts[athlete.belt] = belts.get(athlete.belt, 0) + 1
    
    return {
        "total_athletes": total,
        "saturday": saturday,
        "sunday": sunday,
        "by_belt": belts
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
