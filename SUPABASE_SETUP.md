# Supabase PostgreSQL Setup Guide for EntryDesk

This guide will help you set up persistent cloud storage for EntryDesk using Supabase PostgreSQL. This ensures your data is **never deleted** on application reboots.

## Why Supabase + PostgreSQL?

✅ **Persistent Storage** - Data survives reboots  
✅ **Cloud-Based** - Accessible from anywhere  
✅ **Free Tier** - 500MB database, 2GB bandwidth  
✅ **Automatic Backups** - Daily backups included  
✅ **Reliable** - 99.9% uptime SLA  
✅ **Fast** - Low latency connections  

---

## Part 1: Setting Up Supabase Database

### Step 1: Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"** (top right)
3. Sign up with GitHub, Google, or Email
4. Verify your email if required

### Step 2: Create a New Project

1. After logging in, click **"New Project"**
2. Fill in the project details:
   - **Name**: `entrydesk` (or any name you prefer)
   - **Database Password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`, `ap-southeast-1`, `eu-central-1`)
   - **Pricing Plan**: Select **"Free"** (sufficient for most tournaments)
3. Click **"Create new project"**
4. Wait 2-3 minutes for the project to be created

### Step 3: Get Your Database Connection String

1. Once your project is ready, go to **Project Settings** (gear icon in sidebar)
2. Navigate to **"Database"** in the left menu
3. Scroll down to **"Connection string"** section
4. Select **"URI"** tab
5. Copy the connection string - it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with the database password you created in Step 2
7. Your final connection string should look like:
   ```
   postgresql://postgres:your_actual_password@db.xxxxx.supabase.co:5432/postgres
   ```

> **Important**: Keep this connection string **SECRET** - it's like your database key!

### Step 4: Test Your Database Connection (Optional but Recommended)

You can use the Supabase SQL Editor to verify your database is working:

1. In your Supabase dashboard, click **"SQL Editor"** in the left sidebar
2. Click **"New query"**
3. Run this test query:
   ```sql
   SELECT version();
   ```
4. You should see PostgreSQL version information

---

## Part 2: Configuring EntryDesk for Supabase

### Option A: Running Locally

#### Step 1: Update Your .env File

1. In your EntryDesk folder, create or edit the `.env` file:
   ```bash
   # On Mac/Linux:
   nano .env
   
   # On Windows:
   notepad .env
   ```

2. Add or update the `DATABASE_URL` line:
   ```env
   # Supabase PostgreSQL Database
   DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
   
   # Google OAuth (keep your existing values)
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   REDIRECT_URI=http://localhost:8501
   
   # Security
   SECRET_KEY=your_secret_key_here
   ```

3. Save the file

#### Step 2: Install Dependencies (if needed)

Make sure PostgreSQL driver is installed:
```bash
pip install psycopg2-binary
```

#### Step 3: Initialize the Database

Run this command to create all necessary tables:
```bash
python -c "from database import init_db; init_db()"
```

You should see:
```
INFO:database:Using PostgreSQL database (cloud/persistent storage)
INFO:database:Database tables initialized successfully
```

#### Step 4: Start the Application

```bash
streamlit run app.py
```

Your app is now using persistent cloud storage! 🎉

---

### Option B: Deploying to Streamlit Cloud

#### Step 1: Push Your Code to GitHub

Make sure your code is pushed to GitHub (without the .env file):

```bash
git add .
git commit -m "Add Supabase support"
git push
```

> **Important**: Never commit your `.env` file! It should be in `.gitignore`.

#### Step 2: Deploy on Streamlit Cloud

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `ull0sm/EntryDesk`
5. Set **Main file path**: `app.py`
6. Click **"Advanced settings"**

#### Step 3: Configure Secrets in Streamlit Cloud

In the **Secrets** section, add:

```toml
# Supabase Database Connection
DATABASE_URL = "postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres"

# Google OAuth (if you're using it)
GOOGLE_CLIENT_ID = "your_google_client_id_here"
GOOGLE_CLIENT_SECRET = "your_google_client_secret_here"

# Security
SECRET_KEY = "your_secret_key_here"
```

> **Replace the values** with your actual credentials!

#### Step 4: Deploy

1. Click **"Deploy!"**
2. Wait 2-5 minutes for deployment
3. Your app will automatically initialize the database on first run

#### Step 5: Verify Persistent Storage

1. Login to your app
2. Add a test athlete
3. Copy your app URL and close the browser
4. Wait a few minutes
5. Open the URL again and login
6. Your test athlete should still be there! ✅

---

## Part 3: Verification and Testing

### Check 1: Verify Database Type

When you start the app, check the logs. You should see:
```
INFO:database:Using PostgreSQL database (cloud/persistent storage)
```

If you see SQLite warning, your DATABASE_URL is not configured correctly.

### Check 2: Test Data Persistence

1. Add an athlete to the system
2. Stop and restart the application
3. Verify the athlete is still there
4. ✅ Success! You have persistent storage

### Check 3: View Data in Supabase

1. Go to your Supabase dashboard
2. Click **"Table Editor"** in the left sidebar
3. You should see two tables:
   - `coaches` - All registered coaches
   - `athletes` - All registered athletes
4. Click on each table to view the data

---

## Part 4: Migrating Existing Data (SQLite to PostgreSQL)

If you already have data in SQLite that you want to move to Supabase:

### Option 1: Manual Migration (Recommended for Small Datasets)

1. **Export from SQLite:**
   ```bash
   python -c "
   from database import get_db, Athlete, Coach
   import json
   
   db = next(get_db())
   
   # Export coaches
   coaches = db.query(Coach).all()
   coach_data = [{
       'email': c.email,
       'name': c.name,
       'google_id': c.google_id,
       'is_admin': c.is_admin
   } for c in coaches]
   
   # Export athletes
   athletes = db.query(Athlete).all()
   athlete_data = [{
       'unique_id': a.unique_id,
       'name': a.name,
       'dob': a.dob.isoformat(),
       'dojo': a.dojo,
       'belt': a.belt,
       'day': a.day,
       'coach_email': a.coach.email
   } for a in athletes]
   
   with open('export.json', 'w') as f:
       json.dump({'coaches': coach_data, 'athletes': athlete_data}, f)
   
   print('Data exported to export.json')
   "
   ```

2. **Update .env to use Supabase:**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
   ```

3. **Import to PostgreSQL:**
   ```bash
   python -c "
   from database import get_db, Athlete, Coach, init_db
   from datetime import datetime
   import json
   
   # Initialize PostgreSQL database
   init_db()
   
   db = next(get_db())
   
   # Load data
   with open('export.json', 'r') as f:
       data = json.load(f)
   
   # Import coaches
   coach_map = {}
   for c_data in data['coaches']:
       coach = Coach(**c_data)
       db.add(coach)
       db.commit()
       db.refresh(coach)
       coach_map[c_data['email']] = coach.id
   
   # Import athletes
   for a_data in data['athletes']:
       coach_email = a_data.pop('coach_email')
       a_data['coach_id'] = coach_map[coach_email]
       a_data['dob'] = datetime.fromisoformat(a_data['dob']).date()
       athlete = Athlete(**a_data)
       db.add(athlete)
       db.commit()
   
   print('Data imported successfully!')
   "
   ```

### Option 2: Using Excel Export/Import

1. **Export to Excel** from your current app:
   - Login to your app
   - Go to "View Athletes" tab
   - Click "Download Filtered as Excel"
   - Save the file

2. **Switch to Supabase:**
   - Update DATABASE_URL in .env or Streamlit secrets
   - Restart the application

3. **Import from Excel:**
   - Login to your app
   - Go to "Upload Excel" tab
   - Upload the Excel file you saved
   - Review and import

---

## Part 5: Maintenance and Monitoring

### Monitoring Database Usage

1. Go to your Supabase dashboard
2. Click **"Database"** in the left sidebar
3. View usage statistics:
   - Database size
   - Number of connections
   - Query performance

### Database Backups

Supabase provides **automatic daily backups** on the free tier:
- 7 days of backups retained
- Access backups in: Project Settings > Database > Backups

### Manual Backup

To create a manual backup:

1. In Supabase dashboard, go to **SQL Editor**
2. Run queries to export data as needed
3. Or use Supabase CLI:
   ```bash
   # Install Supabase CLI
   npm install -g supabase
   
   # Login
   supabase login
   
   # Create backup
   supabase db dump -p your_project_ref > backup.sql
   ```

### Scaling

If you need more resources:
- Free tier: 500MB database, 2GB bandwidth
- Pro tier ($25/month): 8GB database, 100GB bandwidth
- Upgrade in: Project Settings > Billing

---

## Troubleshooting

### Problem: "Can't connect to database"

**Solution:**
1. Check your DATABASE_URL is correct
2. Verify your database password
3. Ensure your IP is not blocked (Supabase allows all IPs by default)
4. Check Supabase project is not paused (happens after 7 days of inactivity on free tier)

### Problem: "Table does not exist"

**Solution:**
Run database initialization:
```bash
python -c "from database import init_db; init_db()"
```

### Problem: "SSL connection error"

**Solution:**
Add `?sslmode=require` to your DATABASE_URL:
```
postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

### Problem: "Too many connections"

**Solution:**
Close unused connections or upgrade your plan. The app uses connection pooling to minimize this issue.

### Problem: "Password authentication failed"

**Solution:**
1. Go to Supabase Dashboard > Project Settings > Database
2. Click "Reset database password"
3. Update your DATABASE_URL with the new password

### Problem: "Project paused"

**Solution:**
On the free tier, projects pause after 7 days of inactivity:
1. Go to your Supabase dashboard
2. Click "Restore" on your project
3. The project will be active again in ~2 minutes

---

## Security Best Practices

✅ **Never commit your DATABASE_URL to Git**  
✅ **Use environment variables or Streamlit secrets**  
✅ **Rotate your database password periodically**  
✅ **Enable Row Level Security (RLS) in Supabase for additional protection**  
✅ **Monitor database access logs**  
✅ **Keep Supabase dashboard login credentials secure**  

---

## FAQ

**Q: Is Supabase free tier enough for a tournament?**  
A: Yes! The free tier supports:
- 500MB database (thousands of athletes)
- 2GB bandwidth per month
- Unlimited API requests
- This is more than enough for most karate tournaments

**Q: What happens if I exceed the free tier limits?**  
A: Your project will stop accepting new writes, but existing data remains safe. You can upgrade to Pro tier or wait for the monthly reset.

**Q: Can I use a different PostgreSQL provider?**  
A: Yes! This app works with any PostgreSQL database. Just update the DATABASE_URL. Other options:
- Heroku Postgres
- AWS RDS
- Google Cloud SQL
- DigitalOcean Managed Databases
- ElephantSQL
- Neon

**Q: How do I backup my data?**  
A: Supabase provides automatic daily backups. You can also export to Excel from the app or use the Supabase CLI for SQL dumps.

**Q: Will my data be deleted if I don't use the app for a while?**  
A: On the free tier, projects pause after 7 days of inactivity, but **data is never deleted**. Simply restore your project from the dashboard.

**Q: Can I switch back to SQLite?**  
A: Yes, but it's not recommended for production. SQLite data is lost on Streamlit Cloud reboots. To switch back, just change DATABASE_URL to:
```
DATABASE_URL=sqlite:///./entrydesk.db
```

**Q: How do I know if I'm using Supabase?**  
A: Check the application logs when starting. You should see:
```
INFO:database:Using PostgreSQL database (cloud/persistent storage)
```

---

## Quick Reference

### Supabase Connection String Format
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Get Your Connection String
Supabase Dashboard → Project Settings → Database → Connection string → URI

### Environment Variable
```env
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### Streamlit Cloud Secret
```toml
DATABASE_URL = "postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres"
```

### Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

### Test Connection
```bash
python -c "from database import check_db_connection; print('Connected!' if check_db_connection() else 'Failed!')"
```

---

## Support

If you encounter issues:

1. Check this guide's **Troubleshooting** section
2. Review application logs for error messages
3. Check Supabase status: [status.supabase.com](https://status.supabase.com)
4. Visit Supabase docs: [supabase.com/docs](https://supabase.com/docs)
5. Open an issue on GitHub

---

**🎉 Congratulations! You now have persistent cloud storage for your tournament data!**

Your athletes' data will be safe and accessible from anywhere, surviving all reboots and deployments.
