# EntryDesk Deployment Checklist

Use this checklist when deploying EntryDesk to production.

## Pre-Deployment

### 1. Test Locally
- [ ] Run `python test_app.py` - All tests pass
- [ ] Run `python demo.py` - Demo works
- [ ] Run `./start.sh` - Application starts
- [ ] Test login with sample email
- [ ] Upload sample Excel file
- [ ] Add individual athlete
- [ ] Search and filter athletes
- [ ] Download Excel export

### 2. Prepare Environment
- [ ] Create `.env` file from `.env.example`
- [ ] Generate secret key: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Set up admin emails in `ADMIN_EMAILS` environment variable
  - [ ] Format: comma-separated list (e.g., `admin1@gmail.com, admin2@gmail.com`)
  - [ ] Verify email addresses are correct
- [ ] Configure coach allowlist (for production)
  - [ ] Decide if you want to enforce the allowlist (`ENFORCE_COACH_ALLOWLIST=true` or `false`)
  - [ ] If enforcing, set up `COACH_EMAILS` with specific allowed email addresses
    - Example: `COACH_EMAILS=coach1@example.com, coach2@example.com`
  - [ ] If enforcing, optionally set up `COACH_DOMAINS` for allowed email domains
    - Example: `COACH_DOMAINS=myschool.edu, karate-club.org`
  - [ ] Remember: Admins automatically bypass the allowlist
  - [ ] Test with a non-allowed email to verify it's working
- [ ] Set up Google OAuth (if using)
  - [ ] Create Google Cloud Project
  - [ ] Enable Google+ API
  - [ ] Create OAuth credentials
  - [ ] Add authorized redirect URIs
  - [ ] Copy Client ID and Secret to `.env`

### 3. Code Review
- [ ] Check `.gitignore` includes `.env` and `*.db`
- [ ] Verify no secrets in code
- [ ] Update README if needed
- [ ] Check requirements.txt is complete

## Deployment Options

### Option A: Streamlit Cloud (Recommended for Beginners)

#### Prerequisites
- [ ] GitHub account
- [ ] Code pushed to GitHub repository

#### Steps
1. [ ] Go to [share.streamlit.io](https://share.streamlit.io)
2. [ ] Sign in with GitHub
3. [ ] Click "New app"
4. [ ] Select repository: `ull0sm/EntryDesk`
5. [ ] Main file: `app.py`
6. [ ] Advanced settings > Secrets (optional):
   ```toml
   GOOGLE_CLIENT_ID = "your_client_id"
   GOOGLE_CLIENT_SECRET = "your_client_secret"
   SECRET_KEY = "your_secret_key"
   ADMIN_EMAILS = "admin1@gmail.com, admin2@gmail.com"
   ENFORCE_COACH_ALLOWLIST = "true"
   COACH_EMAILS = "coach1@example.com, coach2@example.com"
   COACH_DOMAINS = "myschool.edu"
   ENTRYDESK_WRITES_ENABLED = "true"
   SHOW_REGISTRATION_TIMER = "false"
   REGISTRATION_CLOSES_AT_IST = "2025-11-15T23:59:00"
   ```
7. [ ] Click "Deploy"
8. [ ] Wait for deployment (2-5 minutes)
9. [ ] Test the deployed app

#### Post-Deployment
- [ ] Save the app URL
- [ ] Share URL with coaches
- [ ] Test with real data
- [ ] Monitor logs

**Cost:** Free

### Option B: Heroku

#### Prerequisites
- [ ] Heroku account
- [ ] Heroku CLI installed
- [ ] Git repository

#### Steps
1. [ ] Login: `heroku login`
2. [ ] Create app: `heroku create your-app-name`
3. [ ] Set environment variables:
   ```bash
   heroku config:set SECRET_KEY="your_secret_key"
   heroku config:set GOOGLE_CLIENT_ID="your_client_id"
   heroku config:set GOOGLE_CLIENT_SECRET="your_client_secret"
   heroku config:set ADMIN_EMAILS="admin1@gmail.com, admin2@gmail.com"
   heroku config:set ENFORCE_COACH_ALLOWLIST="true"
   heroku config:set COACH_EMAILS="coach1@example.com, coach2@example.com"
   heroku config:set COACH_DOMAINS="myschool.edu"
   heroku config:set ENTRYDESK_WRITES_ENABLED="true"
   heroku config:set SHOW_REGISTRATION_TIMER="false"
   heroku config:set REGISTRATION_CLOSES_AT_IST="2025-11-15T23:59:00"
   ```
4. [ ] Deploy: `git push heroku main`
5. [ ] Open: `heroku open`

#### Post-Deployment
- [ ] Check logs: `heroku logs --tail`
- [ ] Test application
- [ ] Set up custom domain (optional)

**Cost:** $7/month (Eco tier) or Free (with limitations)

### Option C: Docker

#### Prerequisites
- [ ] Docker installed
- [ ] Docker Compose installed

#### Steps
1. [ ] Create `.env` file with secrets
2. [ ] Build: `docker-compose build`
3. [ ] Start: `docker-compose up -d`
4. [ ] Check: `docker-compose ps`
5. [ ] View logs: `docker-compose logs -f`
6. [ ] Access: http://localhost:8501

#### Post-Deployment
- [ ] Set up reverse proxy (nginx)
- [ ] Configure SSL (Let's Encrypt)
- [ ] Set up auto-restart
- [ ] Configure backups

**Cost:** Depends on hosting

### Option D: VPS/Cloud Server

#### Prerequisites
- [ ] VPS with Ubuntu/Debian
- [ ] SSH access
- [ ] Domain name (optional)

#### Steps
1. [ ] SSH into server
2. [ ] Update system:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```
3. [ ] Install Python and pip:
   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```
4. [ ] Clone repository:
   ```bash
   git clone https://github.com/ull0sm/EntryDesk.git
   cd EntryDesk
   ```
5. [ ] Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
6. [ ] Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. [ ] Create `.env` file
8. [ ] Test locally: `./start.sh`
9. [ ] Set up systemd service (see below)
10. [ ] Configure nginx (see below)
11. [ ] Set up SSL with Let's Encrypt

#### Systemd Service
Create `/etc/systemd/system/entrydesk.service`:
```ini
[Unit]
Description=EntryDesk Streamlit Application
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/EntryDesk
Environment="PATH=/path/to/EntryDesk/venv/bin"
ExecStart=/path/to/EntryDesk/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable entrydesk
sudo systemctl start entrydesk
sudo systemctl status entrydesk
```

#### Nginx Configuration
Create `/etc/nginx/sites-available/entrydesk`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/entrydesk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Cost:** $5-10/month for basic VPS

## Post-Deployment Testing

### Functional Testing
- [ ] Access application URL
- [ ] Login with test account
- [ ] Upload sample Excel file
- [ ] Add individual athlete
- [ ] Search functionality works
- [ ] Filter by day works
- [ ] Download Excel works
- [ ] Logout works

### Performance Testing
- [ ] Page loads in < 3 seconds
- [ ] Excel upload processes in < 10 seconds
- [ ] Search responds in < 1 second
- [ ] Can handle 50+ athletes

### Security Testing
- [ ] HTTPS enabled (production only)
- [ ] No sensitive data in URLs
- [ ] Session expires on logout
- [ ] SQL injection protected (built-in)
- [ ] XSS protected (built-in)

## Monitoring Setup

### Application Monitoring
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure email alerts
- [ ] Monitor disk space
- [ ] Monitor memory usage

### Database Backups
- [ ] Set up daily backups
- [ ] Test restore process
- [ ] Store backups off-site

Backup script example:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp entrydesk.db backups/entrydesk_$DATE.db
# Keep only last 7 days
find backups/ -name "entrydesk_*.db" -mtime +7 -delete
```

### Logs
- [ ] Configure log rotation
- [ ] Set up log aggregation (optional)
- [ ] Monitor error logs

## Launch Checklist

### Before Launch
- [ ] All tests passing
- [ ] Application deployed
- [ ] SSL certificate active (if production)
- [ ] Backups configured
- [ ] Monitoring active

### Launch Day
- [ ] Send URL to coaches
- [ ] Provide quick start guide
- [ ] Share sample Excel template
- [ ] Monitor for issues
- [ ] Be available for support

### First Week
- [ ] Monitor usage daily
- [ ] Check for errors
- [ ] Gather feedback
- [ ] Make minor adjustments
- [ ] Ensure backups working

## Troubleshooting

### Application won't start
- Check logs
- Verify dependencies installed
- Check port availability
- Verify environment variables

### Database errors
- Check file permissions
- Verify database not locked
- Check disk space
- Restore from backup if needed

### Slow performance
- Check server resources
- Monitor database size
- Check for slow queries
- Consider caching

### Upload failures
- Check file size limits
- Verify Excel format
- Check server disk space
- Review error messages

## Support Resources

- README.md - Full documentation
- SETUP.md - Detailed setup guide
- QUICKSTART.md - User guide
- PROJECT_SUMMARY.md - Overview
- GitHub Issues - Report problems

## Rollback Plan

If something goes wrong:
1. [ ] Keep previous version available
2. [ ] Document the issue
3. [ ] Revert to previous version
4. [ ] Fix issue in development
5. [ ] Re-test before deploying again

---

**Remember:** Test thoroughly before tournament day!
