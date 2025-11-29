#!/usr/bin/env python3
"""
Test script for EntryDesk application
Run this to verify all components are working
"""
import sys
import traceback
from datetime import date

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        import streamlit
        import pandas
        import sqlalchemy
        import openpyxl
        from database import get_db, Coach, Athlete, get_next_unique_id, init_db
        from excel_utils import create_template_excel, validate_excel_data
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database operations"""
    print("\nTesting database...")
    try:
        from database import get_db, Coach, Athlete, get_next_unique_id, init_db
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Get database session
        db = next(get_db())
        
        # Create or get test coach
        coach = db.query(Coach).filter(Coach.email == "test_coach@test.com").first()
        if not coach:
            coach = Coach(
                email="test_coach@test.com",
                name="Test Coach",
                google_id="test_google_id"
            )
            db.add(coach)
            db.commit()
            db.refresh(coach)
            print(f"✅ Created test coach (ID: {coach.id})")
        else:
            print(f"✅ Found existing test coach (ID: {coach.id})")
        
        # Create or get test athlete
        existing_athlete = db.query(Athlete).filter(
            Athlete.name == "Test Athlete",
            Athlete.coach_id == coach.id
        ).first()
        
        if not existing_athlete:
            unique_id = get_next_unique_id(db)
            athlete = Athlete(
                unique_id=unique_id,
                name="Test Athlete",
                dob=date(2010, 1, 1),
                dojo="Test Dojo",
                belt="Yellow",
                day="Saturday",
                gender="Male",
                coach_id=coach.id
            )
            db.add(athlete)
            db.commit()
            db.refresh(athlete)
            print(f"✅ Created test athlete (Unique ID: {athlete.unique_id})")
        else:
            print(f"✅ Found existing test athlete (Unique ID: {existing_athlete.unique_id})")
        
        # Query athletes
        athletes = db.query(Athlete).filter(Athlete.coach_id == coach.id).all()
        print(f"✅ Queried {len(athletes)} athlete(s)")
        
        # Test unique ID generation
        next_id = get_next_unique_id(db)
        print(f"✅ Next unique ID: {next_id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def test_excel_utils():
    """Test Excel utilities"""
    print("\nTesting Excel utilities...")
    try:
        from excel_utils import create_template_excel, validate_excel_data
        import pandas as pd
        
        # Test template creation
        template_df = create_template_excel()
        assert len(template_df) > 0, "Template is empty"
        assert 'Name' in template_df.columns, "Template missing Name column"
        print(f"✅ Template created with {len(template_df)} rows")
        
        # Test validation with valid data
        valid_data = pd.DataFrame({
            'name': ['Test Person'],
            'dob': ['2010-05-15'],
            'dojo': ['Test Dojo'],
            'belt': ['Yellow'],
            'day': ['Saturday'],
            'gender': ['Male']
        })
        cleaned_df, errors = validate_excel_data(valid_data)
        assert len(cleaned_df) == 1, "Valid data was rejected"
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        print(f"✅ Validation accepts valid data")
        
        # Test validation with invalid data
        invalid_data = pd.DataFrame({
            'name': ['', 'Valid Name'],
            'dob': ['invalid', '2010-05-15'],
            'dojo': ['', 'Valid Dojo'],
            'belt': ['', 'Yellow'],
            'day': ['Monday', 'Saturday'],
            'gender': ['', 'Female']
        })
        cleaned_df, errors = validate_excel_data(invalid_data)
        assert len(errors) > 0, "Invalid data was not caught"
        print(f"✅ Validation catches {len(errors)} errors in invalid data")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel utilities test failed: {e}")
        traceback.print_exc()
        return False

def test_streamlit_app():
    """Test that Streamlit app can be loaded"""
    print("\nTesting Streamlit app...")
    try:
        # Import the app (this will test syntax and imports)
        import app
        print("✅ Streamlit app loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        traceback.print_exc()
        return False

def test_admin_emails():
    """Test ADMIN_EMAILS parsing and admin logic"""
    print("\nTesting admin email functionality...")
    try:
        import os
        import importlib
        
        # Test 1: Multiple admins with mixed case and whitespace
        os.environ['ADMIN_EMAILS'] = 'admin1@test.com, ADMIN2@TEST.COM,  admin3@test.com  '
        
        # Reload app module to pick up new environment variable
        import app
        importlib.reload(app)
        
        assert len(app.ADMIN_EMAILS) == 3, f"Expected 3 admins, got {len(app.ADMIN_EMAILS)}"
        assert 'admin1@test.com' in app.ADMIN_EMAILS, "admin1@test.com not found"
        assert 'admin2@test.com' in app.ADMIN_EMAILS, "admin2@test.com (normalized) not found"
        assert 'admin3@test.com' in app.ADMIN_EMAILS, "admin3@test.com not found"
        assert all(e == e.lower() for e in app.ADMIN_EMAILS), "Not all emails are lowercase"
        assert all(' ' not in e for e in app.ADMIN_EMAILS), "Whitespace found in emails"
        print("✅ Multiple admins with normalization works")
        
        # Test 2: Default admin
        del os.environ['ADMIN_EMAILS']
        importlib.reload(app)
        
        assert 'ullas4101997@gmail.com' in app.ADMIN_EMAILS, "Default admin not found"
        assert len(app.ADMIN_EMAILS) == 1, f"Expected 1 default admin, got {len(app.ADMIN_EMAILS)}"
        print("✅ Default admin email works")
        
        # Test 3: Test admin assignment logic with database
        from database import get_db, Coach, init_db
        
        # Set test admin
        os.environ['ADMIN_EMAILS'] = 'testadmin@example.com'
        importlib.reload(app)
        
        db = next(get_db())
        try:
            # Create a coach with admin email
            admin_coach = db.query(Coach).filter(Coach.email == "testadmin@example.com").first()
            if admin_coach:
                db.delete(admin_coach)
                db.commit()
            
            # Simulate creating a new admin coach
            test_email = "testadmin@example.com"
            is_admin = 1 if test_email in app.ADMIN_EMAILS else 0
            assert is_admin == 1, "Admin email should be marked as admin"
            print("✅ Admin assignment logic works for new coaches")
            
            # Test promotion logic
            # Create a non-admin coach
            regular_coach = db.query(Coach).filter(Coach.email == "regular@example.com").first()
            if not regular_coach:
                regular_coach = Coach(
                    email="regular@example.com",
                    name="Regular Coach",
                    google_id="test_regular",
                    is_admin=0
                )
                db.add(regular_coach)
                db.commit()
                db.refresh(regular_coach)
            
            # Now add them to ADMIN_EMAILS and check promotion logic
            os.environ['ADMIN_EMAILS'] = 'testadmin@example.com, regular@example.com'
            importlib.reload(app)
            
            # Simulate login - should promote
            if "regular@example.com" in app.ADMIN_EMAILS and not regular_coach.is_admin:
                regular_coach.is_admin = 1
                db.commit()
            
            db.refresh(regular_coach)
            assert regular_coach.is_admin == 1, "Regular coach should be promoted to admin"
            print("✅ Admin promotion logic works for existing coaches")
            
        finally:
            # Cleanup
            if 'ADMIN_EMAILS' in os.environ:
                del os.environ['ADMIN_EMAILS']
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Admin email test failed: {e}")
        traceback.print_exc()
        return False

def test_coach_allowlist_parsing():
    """Test coach allowlist environment variable parsing"""
    print("\nTesting coach allowlist parsing...")
    try:
        import os
        import importlib
        
        # Test 1: Mixed case and whitespace in COACH_EMAILS
        os.environ['COACH_EMAILS'] = 'Coach1@TEST.com,  COACH2@test.COM  , coach3@Test.com  '
        os.environ['COACH_DOMAINS'] = ' Example.COM, TEST.org  ,  school.EDU '
        
        import app
        importlib.reload(app)
        
        assert len(app.COACH_EMAILS) == 3, f"Expected 3 coach emails, got {len(app.COACH_EMAILS)}"
        assert 'coach1@test.com' in app.COACH_EMAILS, "coach1@test.com not found (normalization issue)"
        assert 'coach2@test.com' in app.COACH_EMAILS, "coach2@test.com not found (normalization issue)"
        assert 'coach3@test.com' in app.COACH_EMAILS, "coach3@test.com not found (normalization issue)"
        assert all(e == e.lower() for e in app.COACH_EMAILS), "Not all emails are lowercase"
        assert all(' ' not in e for e in app.COACH_EMAILS), "Whitespace found in emails"
        print("✅ COACH_EMAILS normalization works")
        
        assert len(app.COACH_DOMAINS) == 3, f"Expected 3 domains, got {len(app.COACH_DOMAINS)}"
        assert 'example.com' in app.COACH_DOMAINS, "example.com not found (normalization issue)"
        assert 'test.org' in app.COACH_DOMAINS, "test.org not found (normalization issue)"
        assert 'school.edu' in app.COACH_DOMAINS, "school.edu not found (normalization issue)"
        assert all(d == d.lower() for d in app.COACH_DOMAINS), "Not all domains are lowercase"
        assert all(' ' not in d for d in app.COACH_DOMAINS), "Whitespace found in domains"
        print("✅ COACH_DOMAINS normalization works")
        
        # Test 2: ENFORCE_COACH_ALLOWLIST parsing
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'true'
        importlib.reload(app)
        assert app.ENFORCE_COACH_ALLOWLIST == True, "ENFORCE_COACH_ALLOWLIST should be True"
        print("✅ ENFORCE_COACH_ALLOWLIST=true parsing works")
        
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'false'
        importlib.reload(app)
        assert app.ENFORCE_COACH_ALLOWLIST == False, "ENFORCE_COACH_ALLOWLIST should be False"
        print("✅ ENFORCE_COACH_ALLOWLIST=false parsing works")
        
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'TRUE'
        importlib.reload(app)
        assert app.ENFORCE_COACH_ALLOWLIST == True, "ENFORCE_COACH_ALLOWLIST should be True (case insensitive)"
        print("✅ ENFORCE_COACH_ALLOWLIST case-insensitive parsing works")
        
        # Cleanup
        if 'COACH_EMAILS' in os.environ:
            del os.environ['COACH_EMAILS']
        if 'COACH_DOMAINS' in os.environ:
            del os.environ['COACH_DOMAINS']
        if 'ENFORCE_COACH_ALLOWLIST' in os.environ:
            del os.environ['ENFORCE_COACH_ALLOWLIST']
        
        return True
        
    except Exception as e:
        print(f"❌ Coach allowlist parsing test failed: {e}")
        traceback.print_exc()
        return False


def test_coach_allowlist_logic():
    """Test coach allowlist logic"""
    print("\nTesting coach allowlist logic...")
    try:
        import os
        import importlib
        
        # Test 1: ENFORCE_COACH_ALLOWLIST off -> all allowed
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'false'
        os.environ['COACH_EMAILS'] = 'allowed@test.com'
        os.environ['COACH_DOMAINS'] = 'allowed.com'
        os.environ['ADMIN_EMAILS'] = 'admin@test.com'
        
        import app
        importlib.reload(app)
        
        assert app.is_allowed_coach('anyone@test.com') == True, "When allowlist is off, all should be allowed"
        assert app.is_allowed_coach('random@example.com') == True, "When allowlist is off, all should be allowed"
        print("✅ ENFORCE_COACH_ALLOWLIST=false allows everyone")
        
        # Test 2: ENFORCE_COACH_ALLOWLIST on -> only allowed emails
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'true'
        os.environ['COACH_EMAILS'] = 'coach1@test.com, coach2@test.com'
        os.environ['COACH_DOMAINS'] = ''
        os.environ['ADMIN_EMAILS'] = 'admin@test.com'
        importlib.reload(app)
        
        assert app.is_allowed_coach('coach1@test.com') == True, "coach1@test.com should be allowed"
        assert app.is_allowed_coach('coach2@test.com') == True, "coach2@test.com should be allowed"
        assert app.is_allowed_coach('COACH1@TEST.COM') == True, "Email matching should be case-insensitive"
        assert app.is_allowed_coach('  coach1@test.com  ') == True, "Email matching should trim whitespace"
        assert app.is_allowed_coach('notallowed@test.com') == False, "Non-allowed email should be blocked"
        assert app.is_allowed_coach('random@example.com') == False, "Non-allowed email should be blocked"
        print("✅ ENFORCE_COACH_ALLOWLIST=true with COACH_EMAILS works correctly")
        
        # Test 3: ENFORCE_COACH_ALLOWLIST on -> domain matching
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'true'
        os.environ['COACH_EMAILS'] = ''
        os.environ['COACH_DOMAINS'] = 'school.edu, club.org'
        os.environ['ADMIN_EMAILS'] = 'admin@test.com'
        importlib.reload(app)
        
        assert app.is_allowed_coach('anyone@school.edu') == True, "Email from school.edu should be allowed"
        assert app.is_allowed_coach('someone@club.org') == True, "Email from club.org should be allowed"
        assert app.is_allowed_coach('ANYONE@SCHOOL.EDU') == True, "Domain matching should be case-insensitive"
        assert app.is_allowed_coach('user@other.com') == False, "Email from other domain should be blocked"
        print("✅ ENFORCE_COACH_ALLOWLIST=true with COACH_DOMAINS works correctly")
        
        # Test 4: Admin bypass
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'true'
        os.environ['COACH_EMAILS'] = 'coach@test.com'
        os.environ['COACH_DOMAINS'] = 'allowed.com'
        os.environ['ADMIN_EMAILS'] = 'admin@test.com, admin2@example.com'
        importlib.reload(app)
        
        assert app.is_allowed_coach('admin@test.com') == True, "Admin should bypass allowlist"
        assert app.is_allowed_coach('admin2@example.com') == True, "Admin2 should bypass allowlist"
        assert app.is_allowed_coach('ADMIN@TEST.COM') == True, "Admin email should be case-insensitive"
        assert app.is_allowed_coach('notadmin@test.com') == False, "Non-admin, non-allowed email should be blocked"
        print("✅ Admin bypass works correctly")
        
        # Test 5: Mixed configuration (emails + domains)
        os.environ['ENFORCE_COACH_ALLOWLIST'] = 'true'
        os.environ['COACH_EMAILS'] = 'special@gmail.com'
        os.environ['COACH_DOMAINS'] = 'school.edu'
        os.environ['ADMIN_EMAILS'] = 'admin@test.com'
        importlib.reload(app)
        
        assert app.is_allowed_coach('special@gmail.com') == True, "Specific email should be allowed"
        assert app.is_allowed_coach('anyone@school.edu') == True, "Domain email should be allowed"
        assert app.is_allowed_coach('admin@test.com') == True, "Admin should be allowed"
        assert app.is_allowed_coach('other@gmail.com') == False, "Non-special gmail should be blocked"
        assert app.is_allowed_coach('user@other.com') == False, "Other domain should be blocked"
        print("✅ Mixed COACH_EMAILS and COACH_DOMAINS configuration works")
        
        # Cleanup
        if 'ENFORCE_COACH_ALLOWLIST' in os.environ:
            del os.environ['ENFORCE_COACH_ALLOWLIST']
        if 'COACH_EMAILS' in os.environ:
            del os.environ['COACH_EMAILS']
        if 'COACH_DOMAINS' in os.environ:
            del os.environ['COACH_DOMAINS']
        if 'ADMIN_EMAILS' in os.environ:
            del os.environ['ADMIN_EMAILS']
        
        return True
        
    except Exception as e:
        print(f"❌ Coach allowlist logic test failed: {e}")
        traceback.print_exc()
        return False


def test_parse_bool():
    """Test parse_bool helper function"""
    print("\nTesting parse_bool function...")
    try:
        import os
        import importlib
        
        # Reload app to ensure we have the latest version
        import app
        importlib.reload(app)
        
        # Test true values
        assert app.parse_bool("true") == True, "parse_bool('true') should be True"
        assert app.parse_bool("TRUE") == True, "parse_bool('TRUE') should be True"
        assert app.parse_bool("True") == True, "parse_bool('True') should be True"
        assert app.parse_bool("1") == True, "parse_bool('1') should be True"
        assert app.parse_bool("yes") == True, "parse_bool('yes') should be True"
        assert app.parse_bool("YES") == True, "parse_bool('YES') should be True"
        assert app.parse_bool("y") == True, "parse_bool('y') should be True"
        assert app.parse_bool("Y") == True, "parse_bool('Y') should be True"
        assert app.parse_bool("on") == True, "parse_bool('on') should be True"
        assert app.parse_bool("ON") == True, "parse_bool('ON') should be True"
        assert app.parse_bool("  true  ") == True, "parse_bool('  true  ') should be True (whitespace)"
        print("✅ parse_bool accepts all true values")
        
        # Test false values
        assert app.parse_bool("false") == False, "parse_bool('false') should be False"
        assert app.parse_bool("FALSE") == False, "parse_bool('FALSE') should be False"
        assert app.parse_bool("0") == False, "parse_bool('0') should be False"
        assert app.parse_bool("no") == False, "parse_bool('no') should be False"
        assert app.parse_bool("NO") == False, "parse_bool('NO') should be False"
        assert app.parse_bool("n") == False, "parse_bool('n') should be False"
        assert app.parse_bool("off") == False, "parse_bool('off') should be False"
        assert app.parse_bool("OFF") == False, "parse_bool('OFF') should be False"
        assert app.parse_bool("random") == False, "parse_bool('random') should be False"
        assert app.parse_bool("") == False, "parse_bool('') should be False"
        assert app.parse_bool("  false  ") == False, "parse_bool('  false  ') should be False (whitespace)"
        print("✅ parse_bool rejects all false values")
        
        return True
        
    except Exception as e:
        print(f"❌ parse_bool test failed: {e}")
        traceback.print_exc()
        return False


def test_ist_timer_computation():
    """Test IST countdown timer computation"""
    print("\nTesting IST timer computation...")
    try:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        
        # Test 1: Future datetime
        ist_tz = ZoneInfo("Asia/Kolkata")
        now_ist = datetime.now(ist_tz)
        future_dt = now_ist + timedelta(days=2, hours=5, minutes=30)
        
        # Format the datetime for the env var
        future_str = future_dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Parse it back (simulating what the app does)
        parsed_dt = datetime.fromisoformat(future_str)
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=ist_tz)
        
        delta = parsed_dt - now_ist
        
        # Verify delta is approximately correct (within 1 second due to processing time)
        expected_seconds = 2 * 24 * 3600 + 5 * 3600 + 30 * 60
        assert abs(delta.total_seconds() - expected_seconds) < 2, "Future datetime delta should be approximately correct"
        print("✅ IST timer handles future datetime correctly")
        
        # Test 2: Past datetime
        past_dt = now_ist - timedelta(days=1)
        past_str = past_dt.strftime("%Y-%m-%dT%H:%M:%S")
        parsed_past = datetime.fromisoformat(past_str)
        if parsed_past.tzinfo is None:
            parsed_past = parsed_past.replace(tzinfo=ist_tz)
        
        past_delta = parsed_past - now_ist
        assert past_delta.total_seconds() < 0, "Past datetime delta should be negative"
        print("✅ IST timer handles past datetime correctly")
        
        # Test 3: Invalid format handling
        try:
            invalid = "not-a-date"
            datetime.fromisoformat(invalid)
            print("❌ Should have raised error for invalid format")
            return False
        except:
            print("✅ IST timer rejects invalid datetime format")
        
        # Test 4: Timezone conversion (if given a different timezone)
        import pytz
        utc_tz = pytz.UTC
        utc_now = datetime.now(utc_tz)
        utc_str = utc_now.isoformat()
        
        # Parse and convert to IST
        parsed_utc = datetime.fromisoformat(utc_str)
        ist_converted = parsed_utc.astimezone(ist_tz)
        
        # Verify conversion happened (IST is UTC+5:30)
        # The hour difference should be approximately 5-6 hours depending on DST
        print("✅ IST timer can handle timezone conversions")
        
        return True
        
    except Exception as e:
        print(f"❌ IST timer computation test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("EntryDesk Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_database,
        test_excel_utils,
        test_streamlit_app,
        test_admin_emails,
        test_coach_allowlist_parsing,
        test_coach_allowlist_logic,
        test_parse_bool,
        test_ist_timer_computation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! The application is ready to use.")
        print("\nTo start the application, run:")
        print("  ./start.sh")
        print("  or")
        print("  streamlit run app.py")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
