# Streamlit Cloud + Supabase Deployment Guide

This guide provides **step-by-step instructions** for deploying EntryDesk to Streamlit Cloud with Supabase PostgreSQL for persistent storage.

## Why This Combination?

✅ **Streamlit Cloud**: Free hosting for your app  
✅ **Supabase**: Free PostgreSQL database with persistent storage  
✅ **No Data Loss**: Your data survives all reboots and redeployments  
✅ **Easy Setup**: Can be completed in 30 minutes  
✅ **Zero Cost**: Both offer generous free tiers  

---

## Prerequisites

Before you start, you need:
- [ ] GitHub account
- [ ] Your code pushed to a GitHub repository
- [ ] About 30 minutes of time

---

## Part 1: Set Up Supabase Database (15 minutes)

### Step 1: Create Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with GitHub (recommended) or Email
4. Verify your email if prompted

### Step 2: Create a New Project

1. Click **"New Project"** in the dashboard
2. Fill in the details:
   - **Organization**: Select or create one
   - **Name**: `entrydesk-production` (or any name)
   - **Database Password**: Click "Generate a password" and **COPY IT** somewhere safe!
   - **Region**: Choose closest to your users:
     - US East Coast: `us-east-1`
     - US West Coast: `us-west-2`
     - Europe: `eu-central-1`
     - Asia: `ap-southeast-1`
   - **Pricing Plan**: Select **Free**
3. Click **"Create new project"**
4. ⏱️ Wait 2-3 minutes while project is provisioning

### Step 3: Get Your Database Connection String

1. Once ready, click **⚙️ Project Settings** (bottom left)
2. Go to **"Database"** section
3. Scroll to **"Connection string"**
4. Click the **"URI"** tab
5. You'll see something like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres
   ```
6. Click **"Copy"** button
7. Replace `[YOUR-PASSWORD]` with the password you saved in Step 2

Your final connection string looks like:
```
postgresql://postgres:your_actual_password_123@db.abcdefgh.supabase.co:5432/postgres
```

> 🔐 **IMPORTANT**: Keep this connection string SECRET! Don't share it publicly or commit it to Git.

---

## Part 2: Deploy to Streamlit Cloud (15 minutes)

### Step 4: Prepare Your GitHub Repository

1. Make sure your code is pushed to GitHub:
   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud deployment"
   git push
   ```

2. Verify these files exist in your repo:
   - `app.py` (main application)
   - `requirements.txt` (dependencies)
   - `database.py` (database models)
   - `.streamlit/config.toml` (configuration)

3. Make sure `.env` is in `.gitignore` (it should be by default)

### Step 5: Create Streamlit Cloud Account

1. Go to [https://share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit Cloud to access your GitHub account

### Step 6: Deploy Your App

1. Click **"New app"** (top right)
2. Fill in the deployment settings:
   - **Repository**: `ull0sm/EntryDesk` (or your fork)
   - **Branch**: `main` (or your working branch)
   - **Main file path**: `app.py`
3. Click **"Advanced settings..."**

### Step 7: Configure Secrets (IMPORTANT!)

In the **Secrets** section, paste this configuration:

```toml
# ===== SUPABASE DATABASE CONNECTION =====
# Replace the entire URL with YOUR Supabase connection string from Part 1, Step 3
DATABASE_URL = "postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres"

# ===== GOOGLE OAUTH (Optional - for production authentication) =====
# If you have Google OAuth set up, add your credentials here:
# GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
# GOOGLE_CLIENT_SECRET = "your-client-secret"

# ===== SECURITY =====
# Generate a secret key by running: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "generate-a-random-secret-key-here"

# ===== WRITE LOCK AND REGISTRATION TIMER (Optional) =====
# ENTRYDESK_WRITES_ENABLED: Controls all write operations (add, upload, edit, delete)
# Set to "false" to disable writes; reads/search/export still work
# Default: "true"
ENTRYDESK_WRITES_ENABLED = "true"

# SHOW_REGISTRATION_TIMER: Display countdown timer banner (informational only)
# Set to "true" to show the timer banner
# NOTE: The timer is display-only and does NOT enforce the write lock
# Default: "false"
SHOW_REGISTRATION_TIMER = "false"

# REGISTRATION_CLOSES_AT_IST: Target datetime in IST (Asia/Kolkata) for the countdown
# Format: YYYY-MM-DDTHH:MM:SS (e.g., 2025-11-15T23:59:00)
# Only used when SHOW_REGISTRATION_TIMER="true"
REGISTRATION_CLOSES_AT_IST = "2025-11-15T23:59:00"
```

**Important Notes:**
- Replace `DATABASE_URL` with YOUR actual Supabase connection string
- Replace the password in the DATABASE_URL with your actual password
- Generate a real SECRET_KEY (instructions below)
- Keep this tab open - you'll need to save these secrets

#### How to Generate SECRET_KEY:

Open a terminal/command prompt and run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your SECRET_KEY.

### Step 8: Launch Your App

1. Review your configuration:
   - Repository: ✓
   - Main file: `app.py` ✓
   - Secrets: ✓ (DATABASE_URL must be set!)
2. Click **"Deploy!"**
3. ⏱️ Wait 3-5 minutes for initial deployment

You'll see the deployment progress:
- Installing dependencies...
- Starting application...
- Running...

### Step 9: Initialize the Database

When your app first loads:

1. The database tables will be **automatically created** on first run
2. You'll see the login page
3. This is normal! Your database is now ready.

---

## Part 3: Verify Everything Works

### Step 10: Test Your Deployment

1. **Login Test:**
   - Enter your email and name
   - Click "Login"
   - You should see your dashboard

2. **Add Test Data:**
   - Go to "Add Athlete" tab
   - Fill in some test data:
     - Name: Test Athlete
     - DOB: 2010-01-01
     - Dojo: Test Dojo
     - Belt: Yellow
     - Day: Saturday
   - Click "Add Athlete"
   - You should see success message

3. **Persistence Test:**
   - Copy your app URL (e.g., `https://your-app.streamlit.app`)
   - Close the browser tab
   - Wait 2-3 minutes
   - Open the URL again
   - Login with same credentials
   - **Your test athlete should still be there!** ✅

4. **Verify in Supabase:**
   - Go to Supabase Dashboard
   - Click "Table Editor"
   - You should see:
     - `coaches` table with your coach record
     - `athletes` table with your test athlete
   - This confirms data is being saved to cloud! ✅

---

## Part 4: Share Your App

### Step 11: Get Your App URL

Your app is now live at:
```
https://your-app-name.streamlit.app
```

You can find the exact URL in:
- Streamlit Cloud dashboard
- Browser address bar
- Email from Streamlit

### Step 12: Share With Coaches

Send your coaches:

1. **App URL**: `https://your-app.streamlit.app`
2. **Instructions**: "Enter your email and name to login"
3. **Template**: Download link for Excel template (in the app)
4. **Support**: Your contact info for questions

Example message:
```
Hi Coaches,

Our tournament registration is now live!

🔗 App: https://your-tournament.streamlit.app

To register your athletes:
1. Visit the link above
2. Enter your email and name
3. Upload your athletes using the Excel template or add them manually

The Excel template is available in the "Upload Excel" tab.

Let me know if you have any questions!
```

---

## Part 5: Monitor and Maintain

### Check App Status

Monitor your app in Streamlit Cloud dashboard:
- **Logs**: View real-time application logs
- **Activity**: See when app was last accessed
- **Resources**: Check memory and CPU usage

### Check Database Status

Monitor your database in Supabase dashboard:
- **Database**: View storage usage (500MB free tier)
- **Table Editor**: View/edit data directly
- **Logs**: See database queries and errors

### Update Your App

When you need to make changes:

1. Update code locally
2. Test changes
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
4. Streamlit Cloud will **automatically redeploy** in 2-3 minutes
5. Your data remains safe during redeployment! ✅

### Update Secrets

If you need to change DATABASE_URL or other secrets:

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click ⚙️ Settings
4. Go to "Secrets"
5. Update the values
6. Click "Save"
7. App will automatically restart with new secrets

---

## Troubleshooting

### Problem: App shows "Checking database connection..."

**Cause**: Can't connect to Supabase database

**Solution:**
1. Go to Streamlit Cloud → Your App → Settings → Secrets
2. Verify DATABASE_URL is correct
3. Check you replaced `[YOUR-PASSWORD]` with actual password
4. Verify no extra spaces before/after the URL
5. Make sure Supabase project is not paused (Settings → General)

### Problem: "Table does not exist"

**Cause**: Database not initialized

**Solution:**
This should happen automatically. If it doesn't:
1. Check logs in Streamlit Cloud
2. Look for initialization error messages
3. Verify DATABASE_URL is a valid PostgreSQL connection string
4. Try restarting the app (Streamlit Cloud → Manage app → Reboot)

### Problem: "Too many connections"

**Cause**: Connection pool exhausted

**Solution:**
1. This is rare with the current configuration
2. If it happens, the app will automatically recover
3. Check for memory leaks in custom code
4. Consider upgrading Supabase plan for more connections

### Problem: Data disappeared

**Cause**: Using SQLite instead of Supabase

**Solution:**
1. Check Streamlit Cloud logs for this line:
   ```
   INFO:database:Using PostgreSQL database (cloud/persistent storage)
   ```
2. If you see "SQLite" warning instead, DATABASE_URL is not configured
3. Go to Settings → Secrets and add DATABASE_URL
4. Restart the app

### Problem: App is slow

**Cause**: Cold start or database distance

**Solution:**
1. Cold start: First request after inactivity takes longer (normal)
2. Database distance: Make sure Supabase region is close to users
3. Check Streamlit Cloud resources in dashboard
4. Consider Streamlit Cloud paid tier for better performance

### Problem: Supabase project paused

**Cause**: Free tier projects pause after 7 days inactivity

**Solution:**
1. Go to Supabase dashboard
2. Click "Restore project"
3. Wait 2 minutes for restore
4. Data is never deleted, just paused

---

## Cost Breakdown

### Streamlit Cloud (Free Tier)
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ 1 CPU per app
- ⚠️ Sleep after inactivity (wakes on first request)
- 💰 **Cost: $0/month**

### Supabase (Free Tier)
- ✅ 500MB database storage
- ✅ 2GB bandwidth per month
- ✅ Unlimited API requests
- ✅ Daily automatic backups (7 days retention)
- ⚠️ Projects pause after 7 days inactivity
- 💰 **Cost: $0/month**

### Total Monthly Cost
**$0** for most tournaments! 🎉

### When to Upgrade?

Consider upgrading if:
- You have 1000+ athletes (database > 500MB)
- High traffic (> 2GB bandwidth/month)
- Need guaranteed uptime (no pausing)
- Want longer backup retention

**Streamlit Cloud Pro**: $20/month per app  
**Supabase Pro**: $25/month

But for most karate tournaments, free tier is sufficient!

---

## Quick Reference Card

### Your Credentials (Fill this out!)

```
Streamlit Cloud App URL:
https://_________________________________.streamlit.app

Supabase Project URL:
https://app.supabase.com/project/_______________________

Supabase Database Password:
_______________________________________________________

DATABASE_URL (for secrets):
postgresql://postgres:____________@db.________.supabase.co:5432/postgres

SECRET_KEY:
_______________________________________________________
```

### Quick Commands

**Test database connection:**
```python
python -c "from database import check_db_connection; check_db_connection()"
```

**View current configuration:**
```python
python -c "from database import DATABASE_URL; print(DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Using SQLite')"
```

**Generate new secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Important Links

- Streamlit Cloud Dashboard: https://share.streamlit.io
- Supabase Dashboard: https://app.supabase.com
- Supabase Status: https://status.supabase.com
- Your App: https://[your-app].streamlit.app

---

## Next Steps

After successful deployment:

1. ✅ Test thoroughly with real data
2. ✅ Share URL with all coaches
3. ✅ Provide Excel template
4. ✅ Set up monitoring alerts (optional)
5. ✅ Schedule regular data exports (backup)
6. ✅ Document admin credentials safely
7. ✅ Plan for tournament day support

---

## Success Checklist

Before going live, verify:

- [ ] App URL is accessible
- [ ] Login works
- [ ] Can add athletes manually
- [ ] Can upload Excel file
- [ ] Can search and filter athletes
- [ ] Can download Excel export
- [ ] Data persists after browser restart
- [ ] Data visible in Supabase dashboard
- [ ] Logs show "Using PostgreSQL database"
- [ ] All coaches have been notified
- [ ] Backup plan in place
- [ ] Support contact shared with coaches

---

**🎉 Congratulations! Your EntryDesk is now live with persistent cloud storage!**

Your tournament data is now:
- ✅ Stored in the cloud (Supabase)
- ✅ Persistent across reboots
- ✅ Backed up automatically
- ✅ Accessible from anywhere
- ✅ Free to operate

For additional help, see:
- `SUPABASE_SETUP.md` - Detailed Supabase configuration
- `README.md` - Full application documentation
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment checklist
