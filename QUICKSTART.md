# Quick Start Guide 🚀

## For Coaches - How to Use EntryDesk

### Step 1: Access the Application
Your tournament organizer will provide you with the application URL.
- Local: `http://localhost:8501`
- Production: `https://your-tournament.streamlit.app`

### Step 2: Login
1. Enter your email address
2. Enter your full name
3. Click "Login"

![Login Screen]

### Step 3: View Your Dashboard
After login, you'll see:
- **Summary Statistics** - Total athletes, Saturday/Sunday counts
- **Three Tabs**:
  - 📋 View Athletes
  - 📤 Upload Excel
  - ➕ Add Athlete

![Dashboard]

### Step 4: Download Excel Template (First Time)
1. Go to "Upload Excel" tab
2. Click "Download Excel Template"
3. Open the template in Excel/Google Sheets

### Step 5: Fill Your Athlete Data
Fill in the template with your athletes:

| Name | DOB | Dojo | Belt | Day | Gender |
|------|-----|------|------|-----|--------|
| John Doe | 2010-05-15 | Dragon Dojo | Yellow | Saturday | Male |
| Jane Smith | 2011-08-22 | Dragon Dojo | Green | Sunday | Female |

**Important:**
- Date format: YYYY-MM-DD (e.g., 2010-05-15)
- Day: "Saturday", "Sunday", "Sat", or "Sun" (normalized automatically)
- Gender: "Male", "Female", "M", "F", "Boy", "Girl", "B", or "G" (normalized automatically)
- All fields are required

**Accepted Values:**
- **Day**: Saturday, Sunday, Sat, Sun (case-insensitive) → normalized to "Saturday" or "Sunday"
- **Gender**: Male, Female, M, F, Boy, Girl, B, G (case-insensitive) → normalized to "Male" or "Female"
- Rows with invalid or missing Gender/Day values will be skipped with clear error messages

### Step 6: Upload Your Excel File
1. Stay in "Upload Excel" tab
2. Click "Choose an Excel file"
3. Select your filled template
4. Wait for validation
5. Review any errors (if any)
6. Click "Import Athletes"
7. Done! 🎉

### Step 7: Add Individual Athletes (Optional)
For adding single athletes:
1. Go to "Add Athlete" tab
2. Fill in the form:
   - Name
   - Date of Birth
   - Dojo
   - Belt (select from dropdown)
   - Day (Saturday or Sunday)
3. Click "Add Athlete"

### Step 8: View and Search Athletes
1. Go to "View Athletes" tab
2. Use search box to find specific athletes
3. Filter by day (Saturday/Sunday/All)
4. Download your list as Excel if needed

### Tips for Coaches 💡

**Before Uploading:**
- ✅ Check all dates are in YYYY-MM-DD format
- ✅ Verify all required fields are filled (including Gender)
- ✅ Gender can be: Male, Female, M, F, Boy, Girl, B, G (will be normalized)
- ✅ Day can be: Saturday, Sunday, Sat, Sun (will be normalized)
- ✅ Remove any empty rows
- ✅ Double-check athlete names and information
- ✅ Save your Excel file before uploading

**During Tournament Prep:**
- 📊 Check your dashboard regularly
- 🔍 Use search to find specific athletes quickly
- 📥 Download your list for offline reference
- ➕ Add late entries manually

**Common Issues:**
- **Date errors**: Use format 2010-05-15 (not 15/05/2010)
- **Day errors**: Must be Saturday, Sunday, Sat, or Sun
- **Gender errors**: Must be Male, Female, M, F, Boy, Girl, B, or G
- **Empty fields**: All fields must be filled (including Gender)
- **File format**: Use .xlsx or .xls format

## For Organizers - Setup & Management

### Initial Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (optional for demo)
4. Run: `./start.sh` or `streamlit run app.py`

### For Production
1. Deploy to Streamlit Cloud (easiest)
2. Configure Google OAuth (recommended)
3. Share the URL with coaches
4. Monitor the database

### Database Management
The application uses SQLite by default. All data is stored in `entrydesk.db`.

**Backup:**
```bash
cp entrydesk.db entrydesk_backup_$(date +%Y%m%d).db
```

**Export all athletes:**
Use the "View Athletes" tab and download Excel, or query directly:
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('entrydesk.db')
df = pd.read_sql_query("SELECT * FROM athletes", conn)
df.to_excel('all_athletes.xlsx', index=False)
```

**View all coaches:**
```bash
sqlite3 entrydesk.db "SELECT * FROM coaches;"
```

**Count total athletes:**
```bash
sqlite3 entrydesk.db "SELECT COUNT(*) FROM athletes;"
```

### Monitoring
- Check application logs regularly
- Monitor disk space for database
- Keep backups before tournament day
- Test with sample data first

## Troubleshooting

### "Cannot connect to database"
```bash
# Reinitialize database
python -c "from database import init_db; init_db()"
```

### "Excel upload fails"
- Check column names match template exactly
- Verify date format (YYYY-MM-DD)
- Remove empty rows
- Try smaller batches (10-20 athletes at a time)

### "Port already in use"
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Support Contact

For technical issues:
1. Check SETUP.md for detailed instructions
2. Review README.md for documentation
3. Run test suite: `python test_app.py`
4. Contact tournament organizers

---

**Good luck with your tournament! 🥋**
