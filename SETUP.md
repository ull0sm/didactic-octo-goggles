# EntryDesk Setup Guide

## Step-by-Step Setup for Beginners

### Prerequisites Check
```bash
# Check Python version (should be 3.8+)
python --version

# If not installed, download from python.org
```

### Installation Steps

#### 1. Download the Code
```bash
# Option A: Using git
git clone https://github.com/ull0sm/EntryDesk.git
cd EntryDesk

# Option B: Download ZIP from GitHub
# Extract and open terminal in the folder
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Environment Variables (Optional for demo)
```bash
# Copy the example file
cp .env.example .env

# For demo mode, you can skip editing .env
# For production, edit .env with your credentials
```

#### 5. Run the Application
```bash
# Quick start
./start.sh

# Or manually
streamlit run app.py
```

#### 6. Access the Application
Open your browser and go to:
```
http://localhost:8501
```

## First Time Usage

1. **Login Screen**
   - Enter your email (e.g., coach@example.com)
   - Enter your name (e.g., Coach John)
   - Click Login

2. **Dashboard**
   - You'll see your coach dashboard
   - Three tabs: View Athletes, Upload Excel, Add Athlete

3. **Add Your First Athlete**
   - Go to "Add Athlete" tab
   - Fill in the form
   - Click "Add Athlete"

4. **Upload Excel File**
   - Go to "Upload Excel" tab
   - Download the template first
   - Fill in your athletes' data
   - Upload the file
   - Review and import

## Deployment Options

### Option 1: Streamlit Cloud (Easiest)

**Requirements:**
- GitHub account
- Repository with your code

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Choose `app.py` as main file
6. Click Deploy

**Cost:** Free tier available

### Option 2: Heroku (Easy)

**Requirements:**
- Heroku account
- Heroku CLI installed

**Steps:**
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Deploy
git push heroku main

# Open app
heroku open
```

**Cost:** Free tier available (with limitations)

### Option 3: Your Own Server (Intermediate)

**Requirements:**
- VPS/Cloud server (e.g., DigitalOcean, AWS, Linode)
- SSH access
- Domain name (optional)

**Steps:**
```bash
# SSH into your server
ssh user@your-server-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip

# Clone your repository
git clone https://github.com/ull0sm/EntryDesk.git
cd EntryDesk

# Install dependencies
pip3 install -r requirements.txt

# Run in background
nohup streamlit run app.py --server.port 8501 &

# Setup nginx as reverse proxy (optional)
# Setup SSL with Let's Encrypt (optional)
```

**Cost:** $5-10/month for basic VPS

### Option 4: Docker (Advanced)

**Requirements:**
- Docker installed
- Docker Compose installed

**Steps:**
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

**Cost:** Depends on hosting

## Google OAuth Setup (For Production)

### Why Google OAuth?
- Secure authentication
- No password management
- Familiar login experience

### Setup Steps

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project"
   - Click "New Project"
   - Name it "EntryDesk"
   - Click "Create"

3. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For local: `http://localhost:8501`
     - For production: `https://your-domain.com`
   - Click "Create"

5. **Copy Credentials**
   - Copy "Client ID"
   - Copy "Client Secret"
   - Paste into your `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

6. **Update Code (if needed)**
   - The app is ready for Google OAuth
   - For now, it uses demo mode (email-based)
   - Full OAuth integration can be added later

## Admin Configuration

### Setting Up Administrators

EntryDesk uses the `ADMIN_EMAILS` environment variable to manage administrators.

**Edit your `.env` file:**
```env
# Single admin
ADMIN_EMAILS=admin@example.com

# Multiple admins (comma-separated)
ADMIN_EMAILS=admin1@gmail.com, admin2@gmail.com, admin3@gmail.com
```

**Important notes:**
- Email matching is **case-insensitive** (Admin@Example.com = admin@example.com)
- Whitespace is automatically trimmed
- New accounts with emails in this list become admins automatically
- Existing accounts are **promoted to admin on their next login** if added to the list
- No auto-demotion: removing an email from the list does NOT demote existing admins

**Admin privileges:**
- Access to admin dashboard with all athletes from all coaches
- View statistics across all entries
- Filter and search across all data

## Coach Allowlist Configuration

### Restricting Access to Authorized Coaches

For production deployments, you can restrict access to only authorized coaches using the coach allowlist feature.

**Edit your `.env` file:**
```env
# Enable the allowlist (set to "true" to enable)
ENFORCE_COACH_ALLOWLIST=true

# Allow specific email addresses (comma-separated)
COACH_EMAILS=coach1@example.com, coach2@example.com

# Allow entire email domains (comma-separated)
COACH_DOMAINS=myschool.edu, karate-club.org
```

**Configuration options:**

1. **ENFORCE_COACH_ALLOWLIST** (default: `false`)
   - Set to `true` to enable allowlist enforcement
   - Set to `false` to allow all coaches (default behavior)

2. **COACH_EMAILS** (optional)
   - Comma-separated list of specific email addresses
   - Example: `coach1@example.com, coach2@example.com`
   - Email matching is case-insensitive and whitespace is trimmed

3. **COACH_DOMAINS** (optional)
   - Comma-separated list of email domains
   - Example: `myschool.edu, karate-club.org`
   - Any email ending with these domains will be allowed
   - Domain matching is case-insensitive and whitespace is trimmed

**Important notes:**
- **Admin bypass**: Admins (listed in `ADMIN_EMAILS`) automatically bypass the allowlist
- **OAuth and Demo mode**: The allowlist is enforced in both Google OAuth login and demo mode (email/name form)
- **Error message**: Unauthorized users see a clear error message when attempting to log in
- **Testing**: Test the allowlist with a non-allowed email before deploying to ensure it works correctly

**Example configurations:**

*For a school or organization:*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=
COACH_DOMAINS=karateschool.edu
```

*For specific coaches only:*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=john@gmail.com, jane@yahoo.com, coach@example.com
COACH_DOMAINS=
```

*Mixed approach (specific coaches + domain):*
```env
ENFORCE_COACH_ALLOWLIST=true
COACH_EMAILS=special.coach@gmail.com
COACH_DOMAINS=karateschool.edu
```

## Security Checklist for Production

- [ ] Generate strong SECRET_KEY
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] Enable HTTPS (use Let's Encrypt)
- [ ] Set up Google OAuth (don't use demo mode)
- [ ] Regular database backups
- [ ] Keep dependencies updated
- [ ] Monitor application logs
- [ ] Set up firewall rules
- [ ] Use environment variables (never commit .env)

## Customization

### Change Colors/Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"  # Change this
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Add More Belt Levels
Edit `app.py`, find `belt_options`:
```python
belt_options = ["White", "Yellow", "Orange", "Green", "Blue", "Purple", "Brown", "Red", "Black", "Your-New-Belt"]
```

### Change Starting ID Number
Edit `database.py`, find `get_next_unique_id`:
```python
return 1000  # Change this number
```

## Troubleshooting

### "Command not found: streamlit"
```bash
# Reinstall streamlit
pip install streamlit

# Or use full path
python -m streamlit run app.py
```

### "Port already in use"
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### "Permission denied: start.sh"
```bash
# Make executable
chmod +x start.sh
```

### Database locked
```bash
# Close all instances
# Delete database and restart
rm entrydesk.db
python -c "from database import init_db; init_db()"
```

### Excel upload fails
- Check column names (should match template)
- Verify date format (YYYY-MM-DD)
- Remove empty rows
- Save as .xlsx format

## Support

Need help?
1. Check this guide
2. Review README.md
3. Check error messages
4. Open issue on GitHub

## Next Steps

After setup:
1. Test with sample data
2. Share login link with coaches
3. Monitor first few uploads
4. Provide template to coaches
5. Set up regular backups
6. Plan for tournament day

---

**You're all set! 🥋**
