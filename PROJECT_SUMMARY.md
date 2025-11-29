# EntryDesk - Project Summary

## What is EntryDesk?

EntryDesk is a centralized database system for managing karate tournament athlete entries. It replaces the traditional error-prone Excel copy-paste method with a streamlined digital solution.

## Problem Solved

**Before EntryDesk:**
- Coaches email Excel sheets to organizers
- Organizers manually copy-paste data into a master sheet
- Error-prone process
- Time-consuming
- No validation
- Difficult to track changes

**After EntryDesk:**
- Coaches login and upload their Excel sheets
- Automatic data validation
- No manual copy-paste needed
- Each athlete gets a unique ID
- Easy search and filtering
- Instant statistics

## Key Features

### For Coaches 🥋
- ✅ Simple login (Google OAuth ready, demo mode available)
- 📤 Upload Excel files with athlete data
- ➕ Add individual athletes via form
- 📊 View all registered athletes
- 🔍 Search by name, dojo, or belt
- 📥 Download your athlete list
- 🎯 Each athlete gets a unique ID

### For Organizers 🎪
- 📊 Centralized database
- 🔐 Secure authentication
- 📈 Real-time statistics
- 💾 Easy data export
- 🛡️ Data validation
- 🚀 Easy deployment

## Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **Backend:** FastAPI (optional, for API access)
- **Database:** SQLite (can be upgraded to PostgreSQL)
- **Auth:** Google OAuth (with demo mode)
- **Excel:** pandas + openpyxl

## Project Structure

```
EntryDesk/
├── app.py              # Main Streamlit application
├── api.py              # FastAPI backend (optional)
├── database.py         # Database models & operations
├── auth.py             # Authentication utilities
├── excel_utils.py      # Excel processing
├── requirements.txt    # Dependencies
├── test_app.py         # Test suite
├── demo.py             # Demo script
├── start.sh            # Quick start script
├── README.md           # Full documentation
├── SETUP.md            # Setup guide
├── QUICKSTART.md       # Quick start for users
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose
├── Procfile            # Heroku deployment
└── .streamlit/
    └── config.toml     # Streamlit settings
```

## Database Schema

### Coaches Table
- `id` - Primary key
- `email` - Unique email (login identifier)
- `name` - Coach name
- `google_id` - Google OAuth ID
- `created_at` - Registration timestamp

### Athletes Table
- `id` - Primary key
- `unique_id` - **Global unique identifier (starts at 1000)**
- `name` - Athlete name
- `dob` - Date of birth
- `dojo` - Dojo/gym name
- `belt` - Belt level
- `day` - Competition day (Saturday/Sunday)
- `gender` - Gender (Male/Female) - **Required**
- `coach_id` - Foreign key to coaches
- `created_at` - Registration timestamp
- `updated_at` - Last update timestamp

## Unique Features

### 1. Unique ID System
Every athlete gets a globally unique ID number:
- Starts from 1000
- Increments sequentially
- Never reused
- Same ID across all views
- Coach A's athlete #1 and Coach B's athlete #1 have different unique IDs

### 2. Excel Validation
Automatic validation with detailed error reporting:
- Checks required fields (including Gender)
- Validates date formats
- Normalizes day values (Sat/Sun → Saturday/Sunday)
- Normalizes gender values (M/F/Boy/Girl → Male/Female)
- Skips invalid rows with clear error messages (row number + reason)
- Reports line numbers for errors
- Shows what was accepted vs rejected/skipped

**Required Fields:**
- Name, DOB, Dojo, Belt, Day, Gender

**Accepted Gender tokens:** Male, Female, M, F, Boy, Girl, B, G (case-insensitive)
**Accepted Day tokens:** Saturday, Sunday, Sat, Sun (case-insensitive)

### 3. Demo Mode
Works out-of-the-box without Google OAuth:
- Email-based login for testing
- No external dependencies
- Perfect for development
- Easy to switch to production

## Deployment Options

### 1. Streamlit Cloud (Easiest)
- Free tier available
- One-click deployment from GitHub
- Built-in secrets management
- Automatic HTTPS

### 2. Heroku
- Free tier available (with limitations)
- Heroku CLI deployment
- Easy scaling
- PostgreSQL addon available

### 3. Docker
- Included Dockerfile
- Docker Compose for local dev
- Deploy anywhere Docker runs
- Easy scaling

### 4. Traditional Server
- VPS/Cloud VM
- Full control
- Custom domain
- Manual setup

## What You Need to Provide

### For Development (Demo)
✅ Nothing! Just run: `./start.sh`

### For Production
1. **Google OAuth Credentials** (optional but recommended)
   - Client ID
   - Client Secret
   - Get from Google Cloud Console

2. **Hosting** (choose one)
   - Streamlit Cloud (free)
   - Heroku (free tier)
   - Your own server
   - Cloud provider

3. **Domain** (optional)
   - Custom domain for branding
   - Configure DNS

## Getting Started

### Quick Start (5 minutes)
```bash
# Clone repository
git clone https://github.com/ull0sm/EntryDesk.git
cd EntryDesk

# Install dependencies
pip install -r requirements.txt

# Start application
./start.sh
```

Open browser to http://localhost:8501

### Production Deployment (30 minutes)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Configure secrets (optional)
5. Deploy
6. Share URL with coaches

## Usage Workflow

### Coach Workflow
1. **Login** → Enter email and name
2. **Choose action:**
   - Upload Excel file (bulk), or
   - Add athlete manually (individual)
3. **View athletes** → Search, filter, download
4. **Done!**

### Organizer Workflow
1. **Deploy application** → Share URL with coaches
2. **Monitor** → Check statistics
3. **Export data** → Download complete athlete list
4. **Tournament day** → Use exported data

## Excel Format

Required columns (case-insensitive):

| Name | DOB | Dojo | Belt | Day |
|------|-----|------|------|-----|
| Athlete Name | YYYY-MM-DD | Dojo Name | Belt Color | Saturday/Sunday |

Example:
| Name | DOB | Dojo | Belt | Day |
|------|-----|------|------|-----|
| John Doe | 2010-05-15 | Dragon Dojo | Yellow | Saturday |
| Jane Smith | 2011-08-22 | Phoenix MA | Green | Sunday |

## Security Features

- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Input validation on all forms
- ✅ Session management
- ✅ Unique ID prevents conflicts
- ✅ No passwords stored (Google OAuth)
- ✅ HTTPS ready

## Testing

Run the test suite:
```bash
python test_app.py
```

Run demonstrations:
```bash
python demo.py
```

## Support & Documentation

- **README.md** - Complete documentation
- **SETUP.md** - Detailed setup instructions
- **QUICKSTART.md** - Quick user guide
- **demo.py** - Code examples
- **test_app.py** - Test suite

## Future Enhancements

Potential additions:
- Email notifications
- Payment tracking
- Category/division management
- Bracket generation
- Results recording
- Certificate generation
- Mobile app
- Multi-tournament support

## Cost Estimation

### Development/Testing
- **Cost:** $0
- **Time:** Ready to use

### Production (Basic)
- **Hosting:** $0-10/month (Streamlit Cloud free or Heroku)
- **Domain:** $10-15/year (optional)
- **Total:** ~$0-15/month

### Production (Professional)
- **Hosting:** $20-50/month (VPS or cloud)
- **Database:** $0-20/month (included or managed)
- **Domain:** $10-15/year
- **SSL:** $0 (Let's Encrypt)
- **Total:** ~$20-70/month

## Technical Requirements

### Minimum
- Python 3.8+
- 512MB RAM
- 1GB storage
- Modern browser

### Recommended
- Python 3.9+
- 1GB RAM
- 2GB storage
- Chrome/Firefox latest

## License

MIT License - Use and modify freely for your tournaments!

## Credits

Built with:
- Streamlit - Web framework
- FastAPI - API framework
- SQLAlchemy - Database ORM
- pandas - Data processing
- openpyxl - Excel handling

## Contact & Support

- **Issues:** GitHub Issues
- **Documentation:** This repository
- **Updates:** Watch repository for updates

---

**EntryDesk - Simplifying tournament management, one entry at a time. 🥋**
