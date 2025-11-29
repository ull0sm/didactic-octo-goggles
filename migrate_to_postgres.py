#!/usr/bin/env python3
"""
Migration script to move data from SQLite to PostgreSQL (Supabase)

This script helps you migrate existing data from a local SQLite database
to a cloud PostgreSQL database (e.g., Supabase).

Usage:
    1. Make sure your current SQLite database has data
    2. Set up your PostgreSQL database (see SUPABASE_SETUP.md)
    3. Update your .env file with the new DATABASE_URL (PostgreSQL)
    4. Run this script: python migrate_to_postgres.py
    5. The script will export from SQLite and import to PostgreSQL
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_header(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}{RESET}\n")

def get_sqlite_data():
    """Export data from SQLite database"""
    from database import Athlete, Coach
    
    # Force SQLite connection
    sqlite_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "entrydesk.db"))
    
    if not os.path.exists(sqlite_file):
        print_error(f"SQLite database not found at: {sqlite_file}")
        print_info("Make sure you have an existing database with data to migrate.")
        return None, None
    
    sqlite_url = f"sqlite:///{sqlite_file}"
    print_info(f"Reading from SQLite: {sqlite_file}")
    
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Export coaches
        coaches = db.query(Coach).all()
        coach_data = []
        for c in coaches:
            coach_data.append({
                'email': c.email,
                'name': c.name,
                'google_id': c.google_id,
                'is_admin': c.is_admin,
                'created_at': c.created_at.isoformat() if c.created_at else None
            })
        
        # Export athletes
        athletes = db.query(Athlete).all()
        athlete_data = []
        for a in athletes:
            athlete_data.append({
                'unique_id': a.unique_id,
                'name': a.name,
                'dob': a.dob.isoformat(),
                'dojo': a.dojo,
                'belt': a.belt,
                'day': a.day,
                'coach_email': a.coach.email,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'updated_at': a.updated_at.isoformat() if a.updated_at else None
            })
        
        print_success(f"Exported {len(coach_data)} coaches")
        print_success(f"Exported {len(athlete_data)} athletes")
        
        return coach_data, athlete_data
    
    except Exception as e:
        print_error(f"Error reading SQLite database: {e}")
        return None, None
    finally:
        db.close()

def save_backup(coach_data, athlete_data):
    """Save backup to JSON file"""
    backup_file = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(backup_file, 'w') as f:
            json.dump({
                'coaches': coach_data,
                'athletes': athlete_data,
                'exported_at': datetime.now().isoformat(),
                'source': 'SQLite'
            }, f, indent=2)
        
        print_success(f"Backup saved to: {backup_file}")
        return backup_file
    
    except Exception as e:
        print_error(f"Error saving backup: {e}")
        return None

def import_to_postgres(coach_data, athlete_data):
    """Import data to PostgreSQL database"""
    # Load environment to get PostgreSQL URL
    from dotenv import load_dotenv
    load_dotenv()
    
    postgres_url = os.getenv("DATABASE_URL")
    
    if not postgres_url or not postgres_url.startswith("postgresql"):
        print_error("DATABASE_URL is not set to a PostgreSQL database!")
        print_info("Please update your .env file with the PostgreSQL connection string.")
        print_info("Example: DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres")
        return False
    
    print_info(f"Connecting to PostgreSQL: {postgres_url.split('@')[1] if '@' in postgres_url else 'database'}")
    
    try:
        from database import Athlete, Coach, Base
        
        # Create engine and session for PostgreSQL
        engine = create_engine(postgres_url, pool_pre_ping=True)
        
        # Create all tables
        print_info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print_success("Tables created")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if data already exists
            existing_coaches = db.query(Coach).count()
            existing_athletes = db.query(Athlete).count()
            
            if existing_coaches > 0 or existing_athletes > 0:
                print_warning(f"Database already has data: {existing_coaches} coaches, {existing_athletes} athletes")
                response = input(f"{YELLOW}Do you want to continue? This will add more data (not replace). [y/N]: {RESET}")
                if response.lower() != 'y':
                    print_info("Migration cancelled by user")
                    return False
            
            # Import coaches
            print_info("Importing coaches...")
            coach_map = {}  # Map old email to new id
            coaches_imported = 0
            coaches_skipped = 0
            
            for c_data in coach_data:
                # Check if coach already exists
                existing = db.query(Coach).filter(Coach.email == c_data['email']).first()
                if existing:
                    coach_map[c_data['email']] = existing.id
                    coaches_skipped += 1
                    continue
                
                # Create new coach
                coach = Coach(
                    email=c_data['email'],
                    name=c_data['name'],
                    google_id=c_data['google_id'],
                    is_admin=c_data['is_admin'],
                    created_at=datetime.fromisoformat(c_data['created_at']) if c_data['created_at'] else datetime.utcnow()
                )
                db.add(coach)
                db.commit()
                db.refresh(coach)
                coach_map[c_data['email']] = coach.id
                coaches_imported += 1
            
            print_success(f"Imported {coaches_imported} coaches (skipped {coaches_skipped} existing)")
            
            # Import athletes
            print_info("Importing athletes...")
            athletes_imported = 0
            athletes_skipped = 0
            
            for a_data in athlete_data:
                # Check if athlete already exists
                existing = db.query(Athlete).filter(
                    Athlete.unique_id == a_data['unique_id']
                ).first()
                if existing:
                    athletes_skipped += 1
                    continue
                
                # Get coach_id from map
                coach_email = a_data['coach_email']
                if coach_email not in coach_map:
                    print_warning(f"Coach not found for athlete {a_data['name']}, skipping...")
                    continue
                
                # Create new athlete
                athlete = Athlete(
                    unique_id=a_data['unique_id'],
                    name=a_data['name'],
                    dob=datetime.fromisoformat(a_data['dob']).date(),
                    dojo=a_data['dojo'],
                    belt=a_data['belt'],
                    day=a_data['day'],
                    coach_id=coach_map[coach_email],
                    created_at=datetime.fromisoformat(a_data['created_at']) if a_data['created_at'] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(a_data['updated_at']) if a_data['updated_at'] else datetime.utcnow()
                )
                db.add(athlete)
                db.commit()
                athletes_imported += 1
            
            print_success(f"Imported {athletes_imported} athletes (skipped {athletes_skipped} existing)")
            
            # Verify import
            final_coaches = db.query(Coach).count()
            final_athletes = db.query(Athlete).count()
            
            print_success(f"PostgreSQL database now has: {final_coaches} coaches, {final_athletes} athletes")
            
            return True
        
        finally:
            db.close()
    
    except Exception as e:
        print_error(f"Error importing to PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print_header("EntryDesk - SQLite to PostgreSQL Migration")
    
    print("This script will help you migrate your data from SQLite to PostgreSQL (Supabase).")
    print()
    
    # Step 1: Check if SQLite database exists
    sqlite_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "entrydesk.db"))
    if not os.path.exists(sqlite_file):
        print_error("No SQLite database found!")
        print_info("This script is for migrating existing data.")
        print_info("If you're starting fresh, just configure DATABASE_URL and start the app.")
        return 1
    
    print_info(f"Found SQLite database: {sqlite_file}")
    print()
    
    # Step 2: Export from SQLite
    print_header("Step 1: Export Data from SQLite")
    coach_data, athlete_data = get_sqlite_data()
    
    if coach_data is None or athlete_data is None:
        print_error("Failed to export data from SQLite")
        return 1
    
    if len(coach_data) == 0 and len(athlete_data) == 0:
        print_warning("SQLite database is empty - nothing to migrate")
        return 0
    
    print()
    
    # Step 3: Save backup
    print_header("Step 2: Create Backup")
    backup_file = save_backup(coach_data, athlete_data)
    if not backup_file:
        print_error("Failed to create backup")
        return 1
    
    print()
    
    # Step 4: Import to PostgreSQL
    print_header("Step 3: Import to PostgreSQL")
    print_info("Make sure you have updated DATABASE_URL in your .env file!")
    print_info("It should start with: postgresql://")
    print()
    
    response = input(f"{YELLOW}Ready to import to PostgreSQL? [y/N]: {RESET}")
    if response.lower() != 'y':
        print_info("Migration cancelled")
        print_info(f"Your data backup is saved in: {backup_file}")
        return 0
    
    print()
    
    success = import_to_postgres(coach_data, athlete_data)
    
    if success:
        print()
        print_header("Migration Complete! ✅")
        print_success("Your data has been successfully migrated to PostgreSQL")
        print()
        print_info("Next steps:")
        print("  1. Test your application with the new database")
        print("  2. Verify all data is present")
        print("  3. Once confirmed, you can safely delete the old SQLite database")
        print(f"  4. Keep the backup file safe: {backup_file}")
        print()
        print_warning("Note: Your SQLite database is still intact (not deleted)")
        return 0
    else:
        print()
        print_header("Migration Failed ❌")
        print_error("Something went wrong during migration")
        print_info(f"Your backup is safe in: {backup_file}")
        print_info("Your original SQLite database is unchanged")
        print()
        print_info("Common issues:")
        print("  - DATABASE_URL not set to PostgreSQL")
        print("  - Cannot connect to PostgreSQL database")
        print("  - Incorrect credentials in connection string")
        print()
        print_info("Check the error messages above and try again")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print_warning("Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
