# Quick Start: Setting Up Persistent Cloud Storage

**Goal:** Get your EntryDesk app running on Streamlit Cloud with Supabase PostgreSQL so data **never gets deleted** on reboot.

**Time needed:** 30 minutes

---

## What You Need

- [ ] GitHub account (to deploy on Streamlit Cloud)
- [ ] Your code pushed to GitHub
- [ ] 30 minutes of your time

---

## Step 1: Create Supabase Account (5 minutes)

1. **Go to Supabase**
   - Visit: https://supabase.com
   - Click "Start your project"

2. **Sign Up**
   - Use GitHub, Google, or Email
   - Verify your email

3. **Create a Project**
   - Click "New Project"
   - Name: `entrydesk` (or anything you want)
   - **Database Password**: Click "Generate a password"
   - ⚠️ **SAVE THIS PASSWORD!** Copy it somewhere safe
   - Region: Choose closest to you (e.g., `us-east-1` for US East)
   - Plan: **Free** (it's enough!)
   - Click "Create new project"
   - ⏱️ Wait 2-3 minutes

---

## Step 2: Get Your Database Connection String (2 minutes)

1. **After project is created:**
   - Click ⚙️ **Settings** (bottom left corner)
   - Click **Database** in the left menu
   - Scroll to "Connection string"
   - Click the **URI** tab

2. **You'll see something like:**
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxx.supabase.co:5432/postgres
   ```

3. **Copy it and replace `[YOUR-PASSWORD]`** with the password you saved in Step 1

4. **Your final connection string looks like:**
   ```
   postgresql://postgres:abc123xyz456@db.abcdefgh.supabase.co:5432/postgres
   ```

5. **Save this connection string** - you'll need it in the next step!

---

## Step 3: Deploy to Streamlit Cloud (10 minutes)

1. **Push Your Code to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub

3. **Create New App**
   - Click "New app" (top right)
   - Repository: Select `ull0sm/EntryDesk`
   - Branch: `main` (or your branch)
   - Main file: `app.py`
   - Click "Advanced settings..."

4. **Add Secrets** (IMPORTANT!)
   
   In the "Secrets" box, paste this:
   
   ```toml
   DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
   SECRET_KEY = "your_secret_key_here"
   ```
   
   **Replace:**
   - `DATABASE_URL` → Your connection string from Step 2
   - `SECRET_KEY` → Generate one with this command:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   
   **Example of filled secrets:**
   ```toml
   DATABASE_URL = "postgresql://postgres:abc123xyz456@db.abcdefgh.supabase.co:5432/postgres"
   SECRET_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"
   ```

5. **Deploy!**
   - Click "Deploy!"
   - ⏱️ Wait 3-5 minutes for deployment
   - Your app URL: `https://your-app.streamlit.app`

---

## Step 4: Verify Everything Works (5 minutes)

1. **Check the Logs**
   - In Streamlit Cloud, click on your app
   - Look for this line in the logs:
     ```
     INFO:database:Using PostgreSQL database (cloud/persistent storage)
     ```
   - ✅ If you see this, you're good!
   - ❌ If you see "SQLite", go back to Step 3 and check DATABASE_URL

2. **Test Data Persistence**
   - Open your app: `https://your-app.streamlit.app`
   - Login with your email
   - Add a test athlete:
     - Name: Test Athlete
     - DOB: 2010-01-01
     - Dojo: Test Dojo
     - Belt: Yellow
     - Day: Saturday
   - Close the browser
   - Wait 2 minutes
   - Open the app again
   - Login again
   - **Your test athlete should still be there!** ✅

3. **Verify in Supabase**
   - Go to Supabase dashboard
   - Click "Table Editor" (left sidebar)
   - You should see:
     - `coaches` table → Your coach record
     - `athletes` table → Your test athlete
   - ✅ This confirms data is in the cloud!

---

## Step 5: Share Your App (2 minutes)

Your app is now live! Share it with your coaches:

**App URL:** `https://your-app.streamlit.app`

**Message to coaches:**
```
Hi everyone,

Our tournament registration system is now live!

🔗 Link: https://your-app.streamlit.app

To register your athletes:
1. Visit the link
2. Enter your email and name
3. Use the Excel template to upload your athletes, or add them manually

Let me know if you have any questions!
```

---

## What You Get

✅ **Free hosting** on Streamlit Cloud  
✅ **Free database** on Supabase (500MB)  
✅ **Persistent storage** - data never deleted  
✅ **Automatic backups** - daily backups by Supabase  
✅ **No maintenance** - everything is managed  
✅ **Accessible anywhere** - cloud-based  

---

## Important URLs to Save

Save these for future reference:

| What | URL | Notes |
|------|-----|-------|
| Your App | `https://______.streamlit.app` | Your tournament registration |
| Streamlit Dashboard | https://share.streamlit.io | Manage your app |
| Supabase Dashboard | https://app.supabase.com | View database |
| Supabase Project | `https://app.supabase.com/project/______` | Your project |

---

## Troubleshooting

### Problem: Data still disappears

**Check:**
1. Streamlit logs show "Using PostgreSQL database" (not SQLite)
2. DATABASE_URL in secrets is correct
3. Password in DATABASE_URL is correct (no brackets like `[YOUR-PASSWORD]`)
4. Supabase project is not paused (check dashboard)

**Solution:**
- Go to Streamlit Cloud → Settings → Secrets
- Verify DATABASE_URL starts with `postgresql://`
- Click "Save" and restart app

### Problem: Can't connect to database

**Check:**
1. Supabase project status (might be paused after 7 days inactivity)
2. Password is correct
3. No extra spaces in DATABASE_URL

**Solution:**
- Go to Supabase dashboard
- If project is paused, click "Restore"
- Verify connection string is correct

### Problem: App shows errors

**Check the logs:**
- Streamlit Cloud → Your App → Manage app → Logs
- Look for specific error messages

**Common fixes:**
- Restart app: Manage app → Reboot
- Check DATABASE_URL format
- Verify Supabase is running

---

## What to Do Next

After successful deployment:

1. ✅ Delete test athlete
2. ✅ Test with real data
3. ✅ Share with coaches
4. ✅ Provide Excel template
5. ✅ Monitor for issues

---

## Need More Help?

**Detailed guides:**
- 📖 [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) - Complete deployment guide
- 📖 [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Detailed Supabase setup
- 📖 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- 📖 [README.md](README.md) - Full documentation

**Still stuck?**
- Check logs for error messages
- Review troubleshooting guide
- Open issue on GitHub

---

## Success! 🎉

You now have:
- ✅ Cloud-hosted tournament registration system
- ✅ Persistent database that never loses data
- ✅ Free tier for everything
- ✅ Automatic backups
- ✅ Ready for production use

**Your data is now safe and persistent across all reboots!**

---

## Checklist

Before you finish, verify:

- [ ] Supabase project created
- [ ] Database connection string saved
- [ ] App deployed to Streamlit Cloud
- [ ] DATABASE_URL added to secrets
- [ ] SECRET_KEY added to secrets
- [ ] Logs show "Using PostgreSQL database"
- [ ] Test athlete added and persists after restart
- [ ] Data visible in Supabase Table Editor
- [ ] App URL saved
- [ ] Coaches notified

---

**You're all set!** Your EntryDesk now has persistent cloud storage. No more data loss on reboot! 🚀
