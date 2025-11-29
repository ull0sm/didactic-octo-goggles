# Changelog

## [Unreleased]

### Added
- **Multiple Admin Support**: Added `ADMIN_EMAILS` environment variable to support multiple administrators
  - Comma-separated list of admin email addresses (case-insensitive)
  - Automatic admin assignment for new coaches whose emails are in the list
  - Automatic promotion for existing coaches when their email is added to the list
  - No auto-demotion when emails are removed (manual database update required)
  - Example: `ADMIN_EMAILS=admin1@gmail.com, admin2@gmail.com, admin3@gmail.com`

### Changed
- Replaced single `ADMIN_EMAIL` constant with `ADMIN_EMAILS` set parsed from environment variable
- Email normalization (lowercase + trim) now applied during login for consistent admin checks
- Updated documentation (README.md, SETUP.md, DEPLOYMENT_CHECKLIST.md) with admin configuration instructions

## [2.0.0] - 2025-10-21

### Added - Production-Grade Features

#### Google OAuth Integration
- Integrated `streamlit-oauth` library for production-grade authentication
- Added Google OAuth 2.0 support with Sign in with Google button
- Automatically extracts user profile information (email, name, google_id)
- Falls back to demo mode if OAuth credentials not configured
- Added `REDIRECT_URI` configuration to environment variables

#### Admin Dashboard
- Created separate admin dashboard for administrator (ullas4101997@gmail.com)
- Admin automatically identified by email address
- Added `is_admin` field to Coach database model
- Three admin dashboard tabs:
  - **All Athletes**: View and search all tournament entries
  - **By Coach**: See breakdown of athletes per coach
  - **Statistics**: View belt distribution, day distribution, and top dojos
- Admin can download complete athlete list as Excel
- Admin sees total statistics across all coaches

#### Duplicate Prevention
- Added validation to prevent redundant entries
- Validates by combination of athlete name AND date of birth
- Manual athlete entry shows error when duplicate detected
- Excel upload skips duplicate entries with detailed reporting
- Clear user feedback showing which entries were skipped and why

#### Belt Standardization
- Updated belt colors to official tournament list:
  - White, Yellow, Blue, Purple, Green, Brown, Black
- Removed non-standard belts: Orange, Red
- Updated Excel template with correct belt examples
- Added belt validation in Excel processor
- Shows helpful error messages for invalid belt colors

### Changed

#### Database Schema
- Added `is_admin` column to `coaches` table (Integer, default=0)
- Requires database recreation for existing installations

#### User Interface
- Login page adapts based on OAuth configuration
- Shows "Sign in with Google" when OAuth configured
- Shows email/name form in demo mode
- Admin users see "Admin Dashboard" instead of "Coach Dashboard"
- Excel import shows separate counts for accepted vs skipped entries

#### Validation
- Excel validator now checks belt colors against whitelist
- Belt validation provides clear error messages
- Duplicate checking happens before database insertion

### Security
- CodeQL security scan: 0 vulnerabilities found
- Google OAuth provides secure authentication
- Admin privileges cannot be escalated by users
- SQL injection protection via SQLAlchemy ORM
- Duplicate checking prevents data pollution

### Testing
All tests passing:
- ✅ Database initialization and migrations
- ✅ Coach creation with admin flag
- ✅ Athlete creation and unique ID generation
- ✅ Duplicate detection by name + DOB
- ✅ Excel template generation
- ✅ Excel validation for valid and invalid data
- ✅ Belt color validation
- ✅ Streamlit app loads without errors

### Dependencies
- Added: `streamlit-oauth==0.1.14`
- Added: `httpx-oauth==0.15.1` (dependency)
- Added: `httpcore==1.*` (dependency)
- Updated: `python-dotenv==1.0.1` (from 1.0.0)

### Configuration

New environment variables:
```env
REDIRECT_URI=http://localhost:8501
```

Updated .env.example with REDIRECT_URI

### Migration Notes

#### For Existing Installations
1. Back up your database: `cp entrydesk.db entrydesk.db.backup`
2. Delete old database: `rm entrydesk.db`
3. Update code: `git pull`
4. Install new dependencies: `pip install -r requirements.txt`
5. Initialize new database: `python -c "from database import init_db; init_db()"`
6. App will create is_admin field automatically

#### For Production Deployment
1. Set up Google OAuth credentials in Google Cloud Console
2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env
3. Set appropriate REDIRECT_URI for your domain
4. Restart application

### Backward Compatibility
- Demo mode ensures app works without OAuth configuration
- Existing athlete data preserved (after schema migration)
- All existing features continue to work
- No breaking changes to Excel import format

---

## Previous Versions

### [1.0.0] - Initial Release
- Basic coach dashboard
- Manual athlete entry
- Excel file upload
- Athlete list viewing
- Search and filter functionality
- Unique ID generation
- SQLite database
- Demo mode authentication
