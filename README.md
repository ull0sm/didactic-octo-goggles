# EntryDesk 🥋

**Karate Tournament Entry Management System**

A centralized database system for managing karate tournament athlete entries. Coaches can easily upload Excel files or manually add athlete information, replacing the error-prone copy-paste method with a streamlined digital solution.

## Features

✨ **Key Features:**
- 🔐 **Google Authentication** - Secure login for coaches (demo mode available)
- 📊 **Dashboard** - View all registered athletes with statistics
- 📤 **Excel Upload** - Bulk import athletes from Excel files
- ➕ **Manual Entry** - Add individual athletes through a simple form
- 🔍 **Search & Filter** - Find athletes by name, dojo, belt, or day
- 📥 **Export** - Download athlete lists as Excel files
- 🎯 **Unique IDs** - Each athlete gets a globally unique ID number
- ✅ **Validation** - Automatic data validation with error reporting

## System Architecture

```
EntryDesk/
├── app.py              # Main Streamlit application
├── api.py              # FastAPI backend (optional)
├── database.py         # Database models and connection
├── auth.py             # Authentication utilities
├── excel_utils.py      # Excel processing functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── start.sh            # Quick start script
└── .streamlit/
    └── config.toml     # Streamlit configuration
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection for initial setup

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ull0sm/EntryDesk.git
cd EntryDesk
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration (optional for demo mode)
nano .env
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

**Option A: Using the start script (Recommended)**
```bash
./start.sh
```

**Option B: Manually**
```bash
# Initialize database
python -c "from database import init_db; init_db()"

# Start Streamlit app
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Configuration

### Environment Variables

Edit the `.env` file to configure:

```env
# Google OAuth (for production)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Admin Configuration
# Comma-separated list of admin email addresses (case-insensitive)
# Example: ADMIN_EMAILS=admin1@gmail.com, admin2@gmail.com, admin3@gmail.com
ADMIN_EMAILS=ullas4101997@gmail.com

# Database - IMPORTANT for persistent storage!
# For local/demo (data lost on reboot):
DATABASE_URL=sqlite:///./entrydesk.db

# For production with Supabase (RECOMMENDED - persistent cloud storage):
# DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
# See SUPABASE_SETUP.md for complete setup instructions

# Security
SECRET_KEY=your_secret_key_here
```

### Cloud Storage Setup (RECOMMENDED)

For persistent storage that survives reboots, use PostgreSQL with Supabase:

📖 **See detailed guides:**
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Complete Supabase configuration guide
- **[STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)** - Step-by-step deployment to Streamlit Cloud with Supabase

**Why Supabase?**
- ✅ **Free tier**: 500MB database, perfect for tournaments
- ✅ **Persistent**: Data never gets deleted on reboot
- ✅ **Cloud-based**: Accessible from anywhere
- ✅ **Automatic backups**: Daily backups included
- ✅ **Easy setup**: 15 minutes to configure

**Quick Start:**
1. Create account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy the PostgreSQL connection string
4. Add to `.env` or Streamlit Cloud secrets
5. Done! Data now persists forever 🎉

### Google OAuth Setup (Optional for Production)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Copy Client ID and Client Secret to `.env`

**For demo/testing**, the app works without Google OAuth using email-based authentication.

### Admin Management

EntryDesk supports multiple administrators through the `ADMIN_EMAILS` environment variable.

**Configuration:**
```env
# Single admin
ADMIN_EMAILS=admin@example.com

# Multiple admins (comma-separated, case-insensitive)
ADMIN_EMAILS=admin1@gmail.com, admin2@gmail.com, admin3@gmail.com
```

**Behavior:**
- **New coaches**: Accounts created for emails in `ADMIN_EMAILS` automatically become admins
- **Existing coaches**: When an existing coach's email is added to `ADMIN_EMAILS`, they are promoted to admin on their next login
- **No auto-demotion**: Removing an email from `ADMIN_EMAILS` does NOT automatically demote that coach (manual database update required)
- **Case-insensitive**: Email matching is case-insensitive and whitespace is trimmed

**Admin vs Regular Coach:**
- Regular coaches can only view and manage their own athletes
- Admins have access to the admin dashboard showing all athletes from all coaches

### Write Lock and Registration Timer

EntryDesk provides environment-based write lock and an optional registration countdown timer in IST (Asia/Kolkata).

**Configuration:**
```env
# ENTRYDESK_WRITES_ENABLED: Controls ALL write operations (add, upload, edit, delete)
# Set to "false" to disable writes; reads/search/export still work
# Accepts: true/false, 1/0, yes/no, y/n, on/off (case-insensitive)
# Default: true
ENTRYDESK_WRITES_ENABLED=true

# SHOW_REGISTRATION_TIMER: Display countdown timer banner (informational only)
# Set to "true" to show the timer banner
# NOTE: The timer is display-only and does NOT enforce the write lock
# Default: false
SHOW_REGISTRATION_TIMER=false

# REGISTRATION_CLOSES_AT_IST: Target datetime in IST (Asia/Kolkata) for the countdown
# Format: YYYY-MM-DDTHH:MM:SS (e.g., 2025-11-15T23:59:00)
# If timezone is provided, it will be converted to IST for display
# Only used when SHOW_REGISTRATION_TIMER=true
REGISTRATION_CLOSES_AT_IST=2025-11-15T23:59:00
```

**Important Notes:**
- **Write Lock**: Only `ENTRYDESK_WRITES_ENABLED` controls write access. When set to `false`, all create/edit/delete operations are blocked in both the UI and API (returns 403 Forbidden).
- **Timer Banner**: The `SHOW_REGISTRATION_TIMER` feature is purely informational. It displays a countdown to the target datetime but does NOT enforce the write lock.
- **Independence**: The timer and write lock are independent. You can:
  - Show a timer without enforcing a write lock
  - Enforce a write lock without showing a timer
  - Use both together for a complete registration deadline experience
- **Read Operations**: When writes are disabled, viewing, searching, and downloading (export) continue to work normally.

### Coach Allowlist

EntryDesk provides a coach allowlist feature to restrict access to authorized coaches only. This is useful for production deployments where you want to control who can access the application.

**Configuration:**
```env
# Enable the allowlist (default: false)
ENFORCE_COACH_ALLOWLIST=true

# Allow specific email addresses
COACH_EMAILS=coach1@example.com, coach2@example.com, coach3@example.com

# Allow entire email domains
COACH_DOMAINS=myschool.edu, karate-club.org
```

**How It Works:**
- When `ENFORCE_COACH_ALLOWLIST=false` (default), all coaches can access the app (current behavior unchanged)
- When `ENFORCE_COACH_ALLOWLIST=true`, only coaches matching the allowlist can log in
- **Admin bypass**: Admins (emails in `ADMIN_EMAILS`) automatically bypass the allowlist and can always access the app
- **Email matching**: Exact email addresses listed in `COACH_EMAILS` are allowed
- **Domain matching**: Any email with a domain in `COACH_DOMAINS` is allowed (e.g., `anyone@myschool.edu`)
- **Case-insensitive**: All email and domain matching is case-insensitive with whitespace trimmed

**Login Paths:**
- **OAuth login**: After successful Google authentication, email is checked against the allowlist
- **Demo mode**: When OAuth is not configured, the email/name form also enforces the allowlist
- **Error message**: Unauthorized users see a clear error message and cannot proceed

**Examples:**

*Allow specific coaches:*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=john@example.com, jane@example.com
COACH_DOMAINS=
```

*Allow entire organization:*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=
COACH_DOMAINS=myschool.edu
```

*Allow specific coaches plus entire domain:*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=specialcoach@gmail.com
COACH_DOMAINS=myschool.edu, karate-club.org
```

**Notes:**
- Admins are always allowed regardless of allowlist settings
- When the allowlist is disabled, the application works exactly as before
- Email normalization (lowercase, trimmed) is consistent with admin email handling

## Usage Guide

### For Coaches

1. **Login**
   - Enter your email and name
   - Click "Login" to access your dashboard

2. **View Athletes**
   - See all registered athletes in a table
   - Search by name, dojo, or belt
   - Filter by competition day (Saturday/Sunday)
   - Download list as Excel

3. **Upload Excel**
   - Download the template to see required format
   - Fill in athlete information in Excel
   - Upload the file
   - Review validation results
   - Confirm import

4. **Add Individual Athlete**
   - Fill in the form with athlete details:
     - Name
     - Date of Birth
     - Dojo
     - Belt level
     - Competition day
     - Gender (Male/Female)
   - Click "Add Athlete"

### For Admins

Admins have access to all coach features plus:

1. **View All Athletes**
   - See athletes from all coaches
   - Filter by coach
   - Search and filter across entire tournament

2. **Upload Excel (Admin)**
   - Upload Excel files and attribute them to any coach
   - Select which coach the athletes should be assigned to
   - Uses same validation/normalization rules as coach uploads

3. **Manage All Entries**
   - Edit any athlete's information
   - Delete entries from any coach
   - View statistics across all coaches

### Excel Format

The Excel file should have these columns:

| Name | DOB | Dojo | Belt | Day | Gender |
|------|-----|------|------|-----|--------|
| John Doe | 2010-05-15 | Main Dojo | Yellow | Saturday | Male |
| Jane Smith | 2011-08-22 | East Branch | Green | Sunday | Female |

**Column Details:**
- **Name**: Athlete's full name (required)
- **DOB**: Date of birth in YYYY-MM-DD format (required)
- **Dojo**: Dojo/gym name (required)
- **Belt**: Belt color/level (required)
  - Valid values: White, Yellow, Blue, Purple, Green, Brown, Black (case-insensitive)
- **Day**: Competition day (required)
  - Valid values: Saturday, Sunday, Sat, Sun (case-insensitive)
  - Normalized to: "Saturday" or "Sunday"
- **Gender**: Athlete's gender (required)
  - Valid values: Male, Female, M, F, Boy, Girl, B, G (case-insensitive)
  - Normalized to: "Male" or "Female"

**Normalization & Validation:**
- Gender tokens are normalized: male/m/boy/b → "Male", female/f/girl/g → "Female"
- Day tokens are normalized: sat/saturday → "Saturday", sun/sunday → "Sunday"
- Rows with missing or invalid Gender/Day values are skipped with clear error messages showing the Excel row number and reason
- Duplicate detection runs on normalized values

## Database Schema

### Coaches Table
- `id`: Primary key
- `email`: Unique email address
- `name`: Coach name
- `google_id`: Google OAuth ID
- `created_at`: Registration timestamp

### Athletes Table
- `id`: Primary key
- `unique_id`: Global unique identifier (starts from 1000)
- `name`: Athlete name
- `dob`: Date of birth
- `dojo`: Dojo name
- `belt`: Belt level
- `day`: Competition day (Saturday/Sunday)
- `gender`: Gender (Male/Female)
- `coach_id`: Foreign key to coaches
- `created_at`: Registration timestamp
- `updated_at`: Last update timestamp

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment

**Recommended: Streamlit Cloud + Supabase (Free & Persistent)**

📖 **Complete step-by-step guide**: [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

**Quick overview:**
1. Push code to GitHub
2. Create Supabase project (free tier)
3. Deploy on Streamlit Cloud
4. Add DATABASE_URL to secrets
5. Done! Your data persists forever ✅

**Other options:**

**Option 1: Streamlit Cloud (Quick start - but needs PostgreSQL for persistence)**
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Configure secrets (use PostgreSQL DATABASE_URL!)
5. Deploy!

**Note**: Must use PostgreSQL DATABASE_URL for persistence. SQLite will lose data on reboot.

**Option 2: Heroku**
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

**Option 3: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

**Option 4: Traditional Server (VPS/Cloud VM)**
```bash
# Install dependencies
pip install -r requirements.txt

# Run with nohup for background process
nohup streamlit run app.py --server.port 8501 &

# Or use systemd service (recommended)
# Create /etc/systemd/system/entrydesk.service
```

### Streamlit Cloud Configuration

For persistent cloud storage, use Supabase PostgreSQL:

📖 **Complete deployment guide**: [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

Add these secrets in Streamlit Cloud dashboard:

```toml
# .streamlit/secrets.toml
# IMPORTANT: Use PostgreSQL for persistent storage!
DATABASE_URL = "postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres"
GOOGLE_CLIENT_ID = "your_client_id"
GOOGLE_CLIENT_SECRET = "your_client_secret"
SECRET_KEY = "your_secret_key"
```

⚠️ **Important**: SQLite is NOT persistent on Streamlit Cloud - data will be deleted on reboot!  
✅ **Solution**: Use Supabase PostgreSQL for permanent cloud storage (see guides above)

## What You Need to Provide

### For Development (Demo Mode)
- ✅ Nothing! Just run the app

### For Production Deployment
- 📧 **Google OAuth Credentials** (if using Google auth)
  - Client ID
  - Client Secret
  - Configure in Google Cloud Console
  
- 🔑 **Secret Key** (for session management)
  - Generate: `python -c "import secrets; print(secrets.token_hex(32))"`
  
- 🌐 **Hosting** (choose one)
  - Streamlit Cloud (free tier available)
  - Heroku (free tier available)
  - Your own server/VPS
  - Cloud provider (AWS, GCP, Azure)

## Troubleshooting

### Database Issues
```bash
# Reset database
rm entrydesk.db
python -c "from database import init_db; init_db()"
```

### Port Already in Use
```bash
# Change port
streamlit run app.py --server.port 8502
```

### Excel Upload Errors
- Check column names match exactly (case-insensitive)
- Ensure dates are in YYYY-MM-DD format
- Verify all required fields are filled
- Check for special characters in names

## API Endpoints (Optional)

If you want to use the FastAPI backend separately:

```bash
# Start API server
python api.py
```

Available endpoints:
- `GET /api/athletes/{coach_id}` - Get all athletes
- `POST /api/athletes/{coach_id}` - Create athlete
- `POST /api/upload/{coach_id}` - Upload Excel
- `DELETE /api/athletes/{athlete_id}` - Delete athlete
- `GET /api/stats/{coach_id}` - Get statistics

## Security Considerations

- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Input validation on all forms
- ✅ Unique ID generation prevents conflicts
- ✅ Session management for authentication
- ⚠️ For production: Enable HTTPS
- ⚠️ For production: Set strong SECRET_KEY
- ⚠️ For production: Configure proper CORS

## Contributing

This project is designed for a specific karate tournament use case. Feel free to fork and adapt for your needs!

## License

MIT License - feel free to use and modify for your tournaments.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the Usage Guide
3. Check the code comments
4. Open an issue on GitHub

## Roadmap

Potential future enhancements:
- [ ] Email notifications
- [ ] Payment tracking
- [ ] Category management
- [ ] Bracket generation
- [ ] Results recording
- [ ] Certificate generation
- [ ] Multi-tournament support
- [ ] Mobile app

---

**Built with ❤️ for the karate community**

*Streamlit • Python • SQLite • FastAPI*