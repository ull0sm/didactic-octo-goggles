#!/usr/bin/env python3
"""
Demo script - Shows how to interact with EntryDesk programmatically
This can be useful for bulk operations or integrations
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, Coach, Athlete, get_next_unique_id, init_db
from excel_utils import process_excel_file, create_template_excel
from datetime import date
import pandas as pd

def demo_database_operations():
    """Demonstrate database operations"""
    print("\n" + "="*60)
    print("DEMO: Database Operations")
    print("="*60)
    
    # Initialize database
    init_db()
    db = next(get_db())
    
    # Create or get coach
    coach = db.query(Coach).filter(Coach.email == "demo@example.com").first()
    if not coach:
        coach = Coach(
            email="demo@example.com",
            name="Demo Coach",
            google_id="demo_123"
        )
        db.add(coach)
        db.commit()
        db.refresh(coach)
        print(f"✅ Created coach: {coach.name} (ID: {coach.id})")
    else:
        print(f"✅ Found existing coach: {coach.name} (ID: {coach.id})")
    
    # Add athletes (check if they exist first)
    athletes_data = [
        ("Alice Johnson", date(2010, 5, 15), "Main Dojo", "Yellow", "Saturday"),
        ("Bob Smith", date(2011, 8, 22), "Main Dojo", "Green", "Sunday"),
    ]
    
    for name, dob, dojo, belt, day in athletes_data:
        # Check if athlete already exists
        existing = db.query(Athlete).filter(
            Athlete.name == name,
            Athlete.coach_id == coach.id
        ).first()
        
        if not existing:
            unique_id = get_next_unique_id(db)
            athlete = Athlete(
                unique_id=unique_id,
                name=name,
                dob=dob,
                dojo=dojo,
                belt=belt,
                day=day,
                coach_id=coach.id
            )
            db.add(athlete)
            db.commit()
            db.refresh(athlete)
            print(f"✅ Added athlete: {name} (Unique ID: {athlete.unique_id})")
        else:
            print(f"✅ Found existing athlete: {name} (Unique ID: {existing.unique_id})")
    
    # Query athletes
    athletes = db.query(Athlete).filter(Athlete.coach_id == coach.id).all()
    print(f"\n📊 Total athletes for {coach.name}: {len(athletes)}")
    
    for athlete in athletes[:5]:  # Show first 5
        print(f"  - {athlete.name} ({athlete.belt} belt, {athlete.day})")
    
    db.close()


def demo_excel_operations():
    """Demonstrate Excel operations"""
    print("\n" + "="*60)
    print("DEMO: Excel Operations")
    print("="*60)
    
    # Create template
    template = create_template_excel()
    print(f"✅ Created template with columns: {list(template.columns)}")
    
    # Create sample Excel file
    sample_data = pd.DataFrame({
        'Name': ['Test Athlete 1', 'Test Athlete 2'],
        'DOB': ['2010-01-01', '2011-02-02'],
        'Dojo': ['Test Dojo', 'Test Dojo'],
        'Belt': ['Yellow', 'Green'],
        'Day': ['Saturday', 'Sunday']
    })
    
    # Save to temp file
    temp_file = '/tmp/test_athletes.xlsx'
    sample_data.to_excel(temp_file, index=False)
    print(f"✅ Created sample Excel file: {temp_file}")
    
    # Process the file
    df, errors = process_excel_file(temp_file)
    print(f"✅ Processed file: {len(df)} valid rows, {len(errors)} errors")
    
    if len(df) > 0:
        print("\nValid data:")
        print(df.to_string(index=False))
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")


def demo_statistics():
    """Show database statistics"""
    print("\n" + "="*60)
    print("DEMO: Statistics")
    print("="*60)
    
    db = next(get_db())
    
    # Overall stats
    total_coaches = db.query(Coach).count()
    total_athletes = db.query(Athlete).count()
    saturday = db.query(Athlete).filter(Athlete.day == 'Saturday').count()
    sunday = db.query(Athlete).filter(Athlete.day == 'Sunday').count()
    
    print(f"👥 Total Coaches: {total_coaches}")
    print(f"🥋 Total Athletes: {total_athletes}")
    print(f"📅 Saturday: {saturday}")
    print(f"📅 Sunday: {sunday}")
    
    # By belt
    print("\nAthletes by Belt:")
    from sqlalchemy import func
    belts = db.query(Athlete.belt, func.count(Athlete.id)).group_by(Athlete.belt).all()
    for belt, count in belts:
        print(f"  {belt}: {count}")
    
    # By coach
    print("\nAthletes by Coach:")
    coaches = db.query(Coach).all()
    for coach in coaches[:5]:  # Show first 5
        count = db.query(Athlete).filter(Athlete.coach_id == coach.id).count()
        print(f"  {coach.name}: {count}")
    
    db.close()


def demo_search_filter():
    """Demonstrate search and filter operations"""
    print("\n" + "="*60)
    print("DEMO: Search & Filter")
    print("="*60)
    
    db = next(get_db())
    
    # Search by name
    search_term = "Test"
    athletes = db.query(Athlete).filter(Athlete.name.contains(search_term)).all()
    print(f"🔍 Search for '{search_term}': {len(athletes)} results")
    
    # Filter by day
    saturday_athletes = db.query(Athlete).filter(Athlete.day == 'Saturday').all()
    print(f"📅 Saturday athletes: {len(saturday_athletes)}")
    
    # Filter by belt
    yellow_belts = db.query(Athlete).filter(Athlete.belt == 'Yellow').all()
    print(f"🥋 Yellow belt athletes: {len(yellow_belts)}")
    
    # Combined filters
    saturday_yellow = db.query(Athlete).filter(
        Athlete.day == 'Saturday',
        Athlete.belt == 'Yellow'
    ).all()
    print(f"🔍 Saturday Yellow belts: {len(saturday_yellow)}")
    
    db.close()


def main():
    """Run all demos"""
    print("="*60)
    print("EntryDesk - Functionality Demonstration")
    print("="*60)
    print("\nThis script demonstrates the core functionality of EntryDesk")
    print("You can use these patterns in your own scripts or integrations\n")
    
    try:
        demo_database_operations()
        demo_excel_operations()
        demo_statistics()
        demo_search_filter()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60)
        print("\nYou can now:")
        print("1. Start the Streamlit app: ./start.sh")
        print("2. Use these patterns for custom integrations")
        print("3. Build your own scripts using the database module")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
