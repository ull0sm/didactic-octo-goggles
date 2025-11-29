# Troubleshooting Guide for EntryDesk

Common issues and solutions for EntryDesk deployment and usage.

## Database Issues

### Issue: Data disappears after reboot (Streamlit Cloud)

**Symptom:** Athletes and coaches disappear when the app restarts

**Cause:** Using SQLite database on Streamlit Cloud (SQLite files are deleted on reboot)

**Solution:**
1. Set up Supabase PostgreSQL database
2. Update DATABASE_URL in Streamlit secrets
3. See: [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)

**How to verify:**
- Check logs for: `INFO:database:Using PostgreSQL database (cloud/persistent storage)`
- If you see: `WARNING:database:Using SQLite database`, you're not using persistent storage!

---

### Issue: "Can't connect to database"

**Symptom:** Error messages about database connection failing

**Possible causes and solutions:**

**1. Wrong DATABASE_URL format**
```
# Wrong ❌
DATABASE_URL = postgresql://postgres@db.xxxxx.supabase.co:5432/postgres

# Correct ✅
DATABASE_URL = postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
```
Note the `:password` after `postgres`

**2. Incorrect password**
- Verify password in Supabase dashboard
- Reset password if needed: Supabase → Settings → Database → Reset password
- Update DATABASE_URL with new password

**3. Supabase project paused**
- Free tier projects pause after 7 days of inactivity
- Go to Supabase dashboard and click "Restore project"
- Wait 2 minutes, then try again

**4. SSL connection issues**
Add `?sslmode=require` to the end of your DATABASE_URL:
```
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
```

---

### Issue: "Table does not exist"

**Symptom:** Error when trying to add or view athletes

**Cause:** Database tables not initialized

**Solution:**

For local development:
```bash
python -c "from database import init_db; init_db()"
```

For Streamlit Cloud:
- Tables should auto-initialize on first run
- Check logs for initialization errors
- Try restarting the app: Streamlit Cloud → Manage app → Reboot

---

### Issue: "Too many connections"

**Symptom:** Database connection pool exhausted

**Cause:** Too many simultaneous connections to database

**Solution:**
- The app uses connection pooling (5 connections + 10 overflow)
- This should handle normal traffic
- If issue persists, check for connection leaks in custom code
- Consider upgrading Supabase plan for more connections

**Temporary workaround:**
Restart the app to clear connection pool

---

### Issue: Migration from SQLite to PostgreSQL fails

**Symptom:** Error when running `migrate_to_postgres.py`

**Solutions:**

**1. Check DATABASE_URL is PostgreSQL:**
```bash
# In your .env file:
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
# NOT sqlite:///./entrydesk.db
```

**2. Verify PostgreSQL connection:**
```bash
python -c "from database import check_db_connection; check_db_connection()"
```

**3. Check SQLite file exists:**
```bash
ls -la entrydesk.db
```

**4. Manual migration:**
Use the Excel export/import method:
- Export data from old database (Download as Excel)
- Switch to PostgreSQL DATABASE_URL
- Import Excel file in new database

---

## Streamlit Cloud Issues

### Issue: App won't start on Streamlit Cloud

**Symptom:** Deployment fails or app shows error

**Common causes:**

**1. Missing secrets**
- Go to: App settings → Secrets
- Verify DATABASE_URL is set
- Verify it's a valid PostgreSQL URL

**2. Requirements not installed**
- Check if requirements.txt is in repository root
- Verify all packages are listed
- Check logs for "ModuleNotFoundError"

**3. Python version mismatch**
- Check `runtime.txt` has: `python-3.9` (or your version)
- Streamlit Cloud supports Python 3.7-3.11

**4. Import errors**
- Check logs for specific error
- Verify all files are committed to Git
- Check file paths are correct (case-sensitive)

---

### Issue: App is slow or times out

**Symptom:** Long loading times, timeouts, or "App is sleeping"

**Causes and solutions:**

**1. Cold start (normal)**
- First request after inactivity takes 10-30 seconds
- Subsequent requests are fast
- This is expected behavior on free tier

**2. Database connection issues**
- Check Supabase region matches user location
- Verify pool_pre_ping is enabled (already configured)
- Check Supabase status: [status.supabase.com](https://status.supabase.com)

**3. Large data sets**
- Use pagination (already implemented)
- Limit query results
- Add database indexes if needed

**Solutions:**
- Upgrade to Streamlit Cloud paid tier for better performance
- Optimize database queries
- Use caching for frequently accessed data

---

### Issue: Secrets not updating

**Symptom:** Changed secrets but app still uses old values

**Solution:**
1. Update secrets in Streamlit Cloud dashboard
2. Click "Save"
3. Manually restart app: Manage app → Reboot
4. Wait 30 seconds for app to restart
5. Clear browser cache if needed

---

## Google OAuth Issues

### Issue: OAuth not working

**Symptom:** Can't login with Google, OAuth errors

**Possible causes:**

**1. Credentials not configured**
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in secrets
- Verify they're correct (no extra spaces)

**2. Redirect URI mismatch**
- Go to Google Cloud Console
- Check authorized redirect URIs
- Should include your Streamlit Cloud URL: `https://your-app.streamlit.app`

**3. OAuth consent screen not configured**
- Set up OAuth consent screen in Google Cloud Console
- Add test users if in testing mode

**Solution:**
For development/testing, the app can work without OAuth:
- Just use email-based login
- OAuth is optional for production

---

## Excel Upload Issues

### Issue: Excel upload fails with validation errors

**Symptom:** Can't import Excel file, shows validation errors

**Common causes:**

**1. Wrong column names**
Required columns (case-insensitive):
- Name
- DOB
- Dojo
- Belt
- Day
- Gender (required)

**2. Date format issues**
Dates must be in format: `YYYY-MM-DD`
Examples:
- Correct: `2010-05-15`
- Wrong: `15/05/2010`, `May 15 2010`

**3. Missing required fields**
All fields are required for each athlete, including Gender

**4. Invalid values**
- Day must be: `Saturday`, `Sunday`, `Sat`, or `Sun` (normalized automatically)
- Gender must be: `Male`, `Female`, `M`, `F`, `Boy`, `Girl`, `B`, or `G` (normalized automatically)
- Belt must be valid belt color
- DOB must be a valid date in the past

**Solution:**
1. Download the template from the app
2. Fill it correctly with all required fields
3. Use accepted values for Gender and Day (see above)
4. Save as .xlsx format
5. Upload again

**Note:** Rows with missing or invalid Gender/Day values will be skipped with clear error messages showing the Excel row number and reason.

---

### Issue: Duplicate entries when uploading

**Symptom:** Warning about duplicate athletes

**Cause:** Athlete with same name, DOB, and dojo already exists

**This is intentional protection!** The app prevents duplicate registrations.

**Solutions:**
- If it's a duplicate: Skip it (already handled by app)
- If it's a different athlete with same name/DOB: Change dojo or add middle name
- If you need to update an existing athlete: Use the Edit function instead

---

## Data Issues

### Issue: Athlete unique ID conflicts

**Symptom:** Error about duplicate unique_id

**Cause:** Database migration or manual data insertion issues

**Solution:**
```python
# Check max unique_id
python -c "
from database import get_db, Athlete
db = next(get_db())
max_id = db.query(Athlete.unique_id).order_by(Athlete.unique_id.desc()).first()
print(f'Max ID: {max_id[0] if max_id else 0}')
"
```

The app auto-generates unique IDs, so this should be rare.

---

### Issue: Can't delete athletes

**Symptom:** Delete button doesn't work or shows error

**Solutions:**
1. Select at least one athlete using checkboxes
2. Click "Delete Selected"
3. Confirm in the dialog
4. Refresh page if needed

If error persists:
- Check database connection
- Verify you have permission (logged in as correct coach)
- Check browser console for JavaScript errors

---

### Issue: Search not finding athletes

**Symptom:** Search returns no results but athletes exist

**Solutions:**
1. Search is case-insensitive
2. Try partial matches (e.g., just first name)
3. Check filters (Day, Belt) aren't too restrictive
4. Try clearing search and filters
5. Verify athletes are actually in database (check Supabase Table Editor)

---

## Performance Issues

### Issue: App running out of memory

**Symptom:** App crashes or becomes unresponsive

**Causes:**
1. Too many athletes loaded at once
2. Large Excel files
3. Memory leak in session state

**Solutions:**
- Use pagination (already implemented for 100 athletes per page)
- Upload athletes in smaller batches
- Clear browser cache and restart
- Check session state isn't storing large objects

---

## Security Issues

### Issue: Getting security warnings

**Symptom:** Browser shows security warnings

**Solutions:**

**1. Enable HTTPS**
- Streamlit Cloud automatically uses HTTPS
- For custom deployment, set up SSL certificate

**2. Verify SECRET_KEY is set**
- Generate new key: `python -c "import secrets; print(secrets.token_hex(32))"`
- Add to secrets/environment variables

**3. Don't commit secrets**
- Never commit .env file
- Use .gitignore (already configured)
- Use Streamlit secrets or environment variables

---

## Browser Issues

### Issue: UI not displaying correctly

**Symptom:** Broken layout, missing buttons, strange appearance

**Solutions:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Try different browser (Chrome, Firefox, Safari)
3. Disable browser extensions
4. Check browser console for errors (F12)
5. Try incognito/private mode

---

### Issue: File upload not working

**Symptom:** Can't select or upload files

**Solutions:**
1. Check file is .xlsx or .xls format
2. File size limit is ~200MB (should be plenty)
3. Try different browser
4. Check file isn't corrupted (open in Excel first)
5. Try uploading smaller file to test

---

## Diagnostic Commands

### Check database type
```bash
python -c "
from database import DATABASE_URL
print('SQLite' if 'sqlite' in DATABASE_URL else 'PostgreSQL')
"
```

### Test database connection
```bash
python -c "from database import check_db_connection; check_db_connection()"
```

### Count records
```bash
python -c "
from database import get_db, Coach, Athlete
db = next(get_db())
print(f'Coaches: {db.query(Coach).count()}')
print(f'Athletes: {db.query(Athlete).count()}')
"
```

### View all unique IDs
```bash
python -c "
from database import get_db, Athlete
db = next(get_db())
ids = [a.unique_id for a in db.query(Athlete).all()]
print(f'Unique IDs: {sorted(ids)}')
"
```

### Check environment variables
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'DATABASE_URL set: {bool(os.getenv(\"DATABASE_URL\"))}')
print(f'GOOGLE_CLIENT_ID set: {bool(os.getenv(\"GOOGLE_CLIENT_ID\"))}')
print(f'SECRET_KEY set: {bool(os.getenv(\"SECRET_KEY\"))}')
"
```

---

## Getting Help

If your issue isn't covered here:

1. **Check the logs:**
   - Streamlit Cloud: App → Manage app → Logs
   - Local: Terminal output

2. **Review documentation:**
   - [README.md](README.md) - General documentation
   - [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Database setup
   - [STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md) - Deployment guide

3. **Check external services:**
   - Supabase Status: [status.supabase.com](https://status.supabase.com)
   - Streamlit Status: [status.streamlit.io](https://status.streamlit.io)

4. **Create an issue:**
   - GitHub Issues: Include error messages and steps to reproduce

5. **Emergency backup:**
   - Export data to Excel from the app
   - Use migration script: `python migrate_to_postgres.py`
   - Save backup JSON file if migration ran

---

## Prevention Tips

To avoid common issues:

✅ **Always use PostgreSQL for production** (Supabase)  
✅ **Never commit .env files or secrets**  
✅ **Test uploads with small files first**  
✅ **Keep backups of your data** (export to Excel regularly)  
✅ **Monitor database size** (Supabase dashboard)  
✅ **Use correct date format in Excel** (YYYY-MM-DD)  
✅ **Set strong SECRET_KEY** (generate with Python)  
✅ **Check logs regularly** for warnings  
✅ **Test changes locally** before deploying  
✅ **Keep dependencies updated** (requirements.txt)  

---

## Quick Fix Checklist

When something goes wrong:

- [ ] Check logs for error messages
- [ ] Verify DATABASE_URL is PostgreSQL (not SQLite)
- [ ] Confirm Supabase project is not paused
- [ ] Restart the app
- [ ] Clear browser cache
- [ ] Check Supabase and Streamlit status pages
- [ ] Verify secrets are correctly configured
- [ ] Test database connection with diagnostic command
- [ ] Review recent code changes
- [ ] Check GitHub issues for similar problems

---

**Still stuck?** Open an issue on GitHub with:
- Error message (full text)
- Steps to reproduce
- What you've already tried
- Logs (without sensitive info)
- Environment (Streamlit Cloud, local, Docker, etc.)
