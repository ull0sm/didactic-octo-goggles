"""
EntryDesk - Karate Tournament Entry Management System
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import os
import time
from datetime import date, datetime
from io import BytesIO
import tempfile
from streamlit_oauth import OAuth2Component
from zoneinfo import ZoneInfo
from pathlib import Path

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="EntryDesk - Tournament Management",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules (after set_page_config)
from database import get_db, Athlete, Coach, get_next_unique_id, init_db, check_duplicate_athlete
from excel_utils import process_excel_file, create_template_excel

# Initialize database
init_db()

# Check database type and warn if using SQLite in production
try:
    from database import DATABASE_URL, logger
    if DATABASE_URL.startswith("sqlite"):
        logger.warning("⚠️  Using SQLite database - Data will be LOST on reboot!")
        logger.info("📘 For persistent storage, set up Supabase: See QUICK_START_CLOUD.md")
except Exception:
    pass

# Session state initialization - Check if user is already logged in from database
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'coach_id' not in st.session_state:
    st.session_state.coach_id = None
if 'coach_email' not in st.session_state:
    st.session_state.coach_email = None
if 'coach_name' not in st.session_state:
    st.session_state.coach_name = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

# Admin emails - comma-separated list from environment variable
ADMIN_EMAILS = {
    e.strip().lower()
    for e in os.getenv("ADMIN_EMAILS", "ullas4101997@gmail.com").split(",")
    if e.strip()
}

# Coach allowlist configuration
ENFORCE_COACH_ALLOWLIST = os.getenv("ENFORCE_COACH_ALLOWLIST", "false").lower() == "true"
COACH_EMAILS = {
    e.strip().lower()
    for e in os.getenv("COACH_EMAILS", "").split(",")
    if e.strip()
}
COACH_DOMAINS = {
    d.strip().lower()
    for d in os.getenv("COACH_DOMAINS", "").split(",")
    if d.strip()
}

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")


def parse_bool(s):
    """
    Parse a string to a boolean value.
    Accepts: true/false, 1/0, yes/no, y/n, on/off (case-insensitive).
    
    Args:
        s: String or value to parse
        
    Returns:
        True if the value represents a truthy value, False otherwise
    """
    return str(s).strip().lower() in {"1", "true", "yes", "y", "on"}


# Write lock and timer configuration
ENTRYDESK_WRITES_ENABLED = parse_bool(os.getenv("ENTRYDESK_WRITES_ENABLED", "true"))
SHOW_REGISTRATION_TIMER = parse_bool(os.getenv("SHOW_REGISTRATION_TIMER", "false"))
REGISTRATION_CLOSES_AT_IST = os.getenv("REGISTRATION_CLOSES_AT_IST", "")


def show_ist_timer_banner():
    """
    Display an informational countdown timer banner for registration closing.
    This is display-only and does NOT enforce write lock.
    """
    if not SHOW_REGISTRATION_TIMER:
        return
    
    if not REGISTRATION_CLOSES_AT_IST:
        return
    
    try:
        # Parse the target datetime
        target_dt = datetime.fromisoformat(REGISTRATION_CLOSES_AT_IST.strip())
        
        # If naive (no timezone), assume IST
        ist_tz = ZoneInfo("Asia/Kolkata")
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=ist_tz)
        else:
            # If aware, convert to IST
            target_dt = target_dt.astimezone(ist_tz)
        
        # Get current time in IST
        now_ist = datetime.now(ist_tz)
        
        # Calculate time delta
        delta = target_dt - now_ist
        
        # Format target datetime for display
        target_display = target_dt.strftime("%Y-%m-%d %H:%M IST")
        
        # Build the banner message
        st.info(f"**Registration closes at:** {target_display}")
        
        if delta.total_seconds() > 0:
            # Calculate days, hours, minutes
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            st.info(f"**Registration closes in:** {days} days {hours} hours {minutes} minutes")
        else:
            st.warning("**Registration has closed.**")
    
    except Exception as e:
        # If parsing fails, log warning but don't crash
        from database import logger
        logger.warning(f"Failed to parse REGISTRATION_CLOSES_AT_IST: {e}")
        # Don't show any UI if there's an error


def show_writes_disabled_message():
    """Display a message when writes are disabled."""
    st.error("⏰ **Time up. Registrations are closed.**")
    st.info("ℹ️ Viewing, search, and download remain available.")


def is_allowed_coach(email: str) -> bool:
    """
    Check if a coach email is allowed to access the application.
    
    Args:
        email: Email address to check
        
    Returns:
        True if the email is allowed, False otherwise
    """
    # Normalize email (lowercase and trim whitespace)
    email = (email or "").strip().lower()
    
    # If allowlist is not enforced, allow all
    if not ENFORCE_COACH_ALLOWLIST:
        return True
    
    # Admins always bypass the allowlist
    if email in ADMIN_EMAILS:
        return True
    
    # Check if email is in the allowlist
    if email in COACH_EMAILS:
        return True
    
    # Check if email's domain matches any allowed domain
    if '@' in email:
        domain = email.split('@')[1]
        if domain in COACH_DOMAINS:
            return True
    
    return False


def login_page():
    """Display login page with premium, modern aesthetic"""
    # Custom CSS for premium styling
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Poppins:wght@500;600;700&display=swap');

        /* Global Reset & Base Styles for Login Page */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* Main Container */
        .login-container {
            max-width: 480px;
            margin: 4rem auto;
            padding: 0 1rem;
            animation: fadeInUp 0.8s ease-out;
        }

        /* Glassmorphism Card */
        .login-box {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 3rem 2.5rem;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 
                0 10px 40px rgba(0, 0, 0, 0.08),
                0 1px 3px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .login-box:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 20px 50px rgba(0, 0, 0, 0.12),
                0 2px 5px rgba(0, 0, 0, 0.05);
        }

        /* Logo Styling */
        .logo-container {
            margin-bottom: 2rem;
            display: flex;
            justify-content: center;
        }
        
        .logo-img {
            max-width: 140px;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .logo-img:hover {
            transform: scale(1.05) rotate(2deg);
        }
        
        .logo-placeholder {
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #1a472a 0%, #2d5016 100%);
            border-radius: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 2rem;
            box-shadow: 0 10px 25px rgba(45, 80, 22, 0.3);
            margin: 0 auto;
        }

        /* Typography */
        .org-name {
            color: #1a472a;
            font-family: 'Poppins', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin: 1.5rem 0 0.5rem 0;
            text-transform: uppercase;
            opacity: 0.9;
        }

        .app-title {
            color: #111;
            font-family: 'Poppins', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            background: linear-gradient(90deg, #111 0%, #444 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            color: #666;
            font-size: 1.05rem;
            margin-bottom: 2rem;
            font-weight: 400;
        }

        .event-badge {
            display: inline-block;
            background: rgba(45, 80, 22, 0.1);
            color: #1a472a;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 2.5rem;
            border: 1px solid rgba(45, 80, 22, 0.2);
        }

        .login-message {
            color: #555;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translate3d(0, 40px, 0);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Center container using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
        
        # Logo Logic
        import base64
        import os
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
        
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_data}" class="logo-img" alt="Organization Logo">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="logo-container">
                <div class="logo-placeholder">
                    ED
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Content
        st.markdown("""
            <div class="org-name">Okinawa ShorinRyu Shorin Kai</div>
            <div class="app-title">EntryDesk</div>
            <div class="subtitle">Tournament Management System</div>
            <div class="event-badge">30th National Karate Championship</div>
        """, unsafe_allow_html=True)
        
        # OAuth Section
        if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
            st.markdown('<div class="login-message">Sign in to manage your athletes</div>', unsafe_allow_html=True)
            
            # Initialize OAuth component
            oauth2 = OAuth2Component(
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                refresh_token_endpoint="https://oauth2.googleapis.com/token",
                revoke_token_endpoint="https://oauth2.googleapis.com/revoke",
            )

            # Render OAuth button
            result = oauth2.authorize_button(
                name="Sign in with Google",
                icon="https://www.google.com/favicon.ico",
                redirect_uri=REDIRECT_URI,
                scope="openid email profile",
                key="google_oauth",
                extras_params={"prompt": "consent", "access_type": "offline"},
            )
            
            if result and result.get("token"):
                # Verify token
                user_info = verify_google_token(result["token"]["id_token"])
                
                if user_info:
                    # Check allowlist
                    if is_allowed_coach(user_info['email']):
                        # Get database session
                        db = next(get_db())
                        try:
                            # Get or create coach
                            coach = get_or_create_coach(db, user_info)
                            
                            # Set session state
                            st.session_state.logged_in = True
                            st.session_state.coach_id = coach.id
                            st.session_state.coach_email = coach.email
                            st.session_state.coach_name = coach.name
                            st.session_state.is_admin = (coach.is_admin == 1)
                            st.session_state.auth_token = result["token"]
                            st.rerun()
                        finally:
                            db.close()
                    else:
                        st.error("🚫 Access Denied: Your email is not authorized for this tournament.")
                else:
                    st.error("❌ Authentication failed. Please try again.")
        else:
            # Demo Mode
            st.warning("⚠️ Demo Mode (No OAuth Configured)")
            st.markdown('<div class="login-message">Enter your details to continue</div>', unsafe_allow_html=True)
            
            with st.form("demo_login"):
                email = st.text_input("Email Address")
                name = st.text_input("Coach Name")
                submitted = st.form_submit_button("Enter Demo Mode", use_container_width=True)
                
                if submitted:
                    if email and name:
                        if is_allowed_coach(email):
                            # Get database session
                            db = next(get_db())
                            try:
                                # Create demo user info
                                user_info = {
                                    'email': email,
                                    'name': name,
                                    'google_id': f"demo_{email}"
                                }
                                coach = get_or_create_coach(db, user_info)
                                
                                st.session_state.logged_in = True
                                st.session_state.coach_id = coach.id
                                st.session_state.coach_email = coach.email
                                st.session_state.coach_name = coach.name
                                st.session_state.is_admin = (coach.is_admin == 1)
                                st.rerun()
                            finally:
                                db.close()
                        else:
                            st.error("🚫 Access Denied")
                    else:
                        st.error("Please fill in all fields")

        st.markdown('</div></div>', unsafe_allow_html=True)



def dashboard_page():
    """Display main dashboard"""
    # Sidebar
    with st.sidebar:
        st.title("🥋 EntryDesk")
        st.markdown(f"**Coach:** {st.session_state.coach_name}")
        st.markdown(f"**Email:** {st.session_state.coach_email}")
        
        # Database status - compact warning
        from database import DATABASE_URL
        if DATABASE_URL.startswith("sqlite"):
            st.divider()
            st.caption("⚠️ Using local database - data will be lost on reboot")
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.coach_id = None
            st.session_state.coach_email = None
            st.session_state.coach_name = None
            st.session_state.auth_token = None
            st.rerun()
    
    # Main content
    st.title("Coach Dashboard")
    
    # Show IST timer banner if enabled (display-only, does NOT enforce writes)
    show_ist_timer_banner()
    
    # Show write lockdown message if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        show_writes_disabled_message()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Fetch coach's athletes
        athletes = db.query(Athlete).filter(Athlete.coach_id == st.session_state.coach_id).all()
        
        # Display statistics
        st.header("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Athletes", len(athletes))
        
        saturday_count = sum(1 for a in athletes if a.day == 'Saturday')
        with col2:
            st.metric("Saturday", saturday_count)
        
        sunday_count = sum(1 for a in athletes if a.day == 'Sunday')
        with col3:
            st.metric("Sunday", sunday_count)
        
        # Count unique belts
        belts = set(a.belt for a in athletes)
        with col4:
            st.metric("Belt Levels", len(belts))
        
        st.markdown("---")
        
        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["📋 View Athletes", "📤 Upload Excel", "➕ Add Athlete"])
        
        with tab1:
            view_athletes_tab(db, athletes)
        
        with tab2:
            upload_excel_tab(db)
        
        with tab3:
            add_athlete_tab(db)
    
    finally:
        db.close()


def view_athletes_tab(db, athletes):
    """Tab for viewing and searching athletes with pagination, edit, and delete"""
    st.subheader("Your Registered Athletes")
    
    if not athletes:
        st.info("No athletes registered yet. Upload an Excel file or add athletes manually.")
        return
    
    # Initialize session state for selections
    if 'selected_athletes' not in st.session_state:
        st.session_state.selected_athletes = set()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'edit_athlete_id' not in st.session_state:
        st.session_state.edit_athlete_id = None
    
    # Search and filter functionality
    st.markdown("#### Search Functionalities")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search by name, dojo, or belt", "")
    with col2:
        day_filter = st.selectbox("Filter by day", ["All", "Saturday", "Sunday"])
    with col3:
        belt_filter = st.selectbox("Filter by belt", ["All", "White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"])
    with col4:
        gender_filter = st.selectbox("Filter by gender", ["All", "Male", "Female"])
    
    # Filter athletes
    filtered_athletes = athletes
    if search_query:
        filtered_athletes = [
            a for a in filtered_athletes
            if search_query.lower() in a.name.lower() or
               search_query.lower() in a.dojo.lower() or
               search_query.lower() in a.belt.lower()
        ]
    
    if day_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.day == day_filter]
    
    if belt_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.belt == belt_filter]
    
    if gender_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.gender == gender_filter]
    
    # Pagination setup
    items_per_page = 100
    total_pages = (len(filtered_athletes) + items_per_page - 1) // items_per_page
    
    # Ensure current page is within bounds
    if st.session_state.current_page >= total_pages:
        st.session_state.current_page = max(0, total_pages - 1)
    
    start_idx = st.session_state.current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_athletes))
    page_athletes = filtered_athletes[start_idx:end_idx]
    
    st.write(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_athletes)} athletes (Total: {len(athletes)})")
    
    st.markdown("")
    
    # Display athletes with checkboxes
    if page_athletes:
        # Table header
        st.markdown("#### Athlete List")
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.5, 1, 2, 2, 1.5, 1, 1, 1, 1])
        with col1:
            # Header checkbox to select/deselect all visible rows
            all_selected = all(a.id in st.session_state.selected_athletes for a in page_athletes)
            header_check = st.checkbox("", value=all_selected, key="header_select_all", label_visibility="collapsed")
            # Handle state change only if value actually changed
            if header_check != all_selected:
                if header_check:
                    # Select all on current page
                    st.session_state.selected_athletes.update([a.id for a in page_athletes])
                else:
                    # Deselect all on current page
                    for a in page_athletes:
                        st.session_state.selected_athletes.discard(a.id)
        with col2:
            st.markdown("**ID**")
        with col3:
            st.markdown("**Name**")
        with col4:
            st.markdown("**Dojo**")
        with col5:
            st.markdown("**DOB**")
        with col6:
            st.markdown("**Belt**")
        with col7:
            st.markdown("**Day**")
        with col8:
            st.markdown("**Gender**")
        with col9:
            st.markdown("**Actions**")
        
        st.markdown("---")
        
        for athlete in page_athletes:
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.5, 1, 2, 2, 1.5, 1, 1, 1, 1])
            
            with col1:
                is_selected = athlete.id in st.session_state.selected_athletes
                checkbox_value = st.checkbox("", value=is_selected, key=f"cb_{athlete.id}", label_visibility="collapsed")
                # Handle state change only if value actually changed
                if checkbox_value != is_selected:
                    if checkbox_value:
                        st.session_state.selected_athletes.add(athlete.id)
                    else:
                        st.session_state.selected_athletes.discard(athlete.id)
            
            with col2:
                st.write(f"**{athlete.unique_id}**")
            with col3:
                st.write(athlete.name)
            with col4:
                st.write(athlete.dojo)
            with col5:
                st.write(athlete.dob.strftime("%Y-%m-%d"))
            with col6:
                st.write(athlete.belt)
            with col7:
                st.write(athlete.day)
            with col8:
                st.write(athlete.gender if athlete.gender else "-")
            with col9:
                # Edit and Delete icons for each entry
                if ENTRYDESK_WRITES_ENABLED:
                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        if st.button("✏️", key=f"edit_{athlete.id}", help="Edit athlete"):
                            st.session_state.edit_athlete_id = athlete.id
                            st.rerun()
                    with action_col2:
                        if st.button("🗑️", key=f"delete_{athlete.id}", help="Delete athlete"):
                            # Set up delete confirmation
                            if 'confirm_delete' not in st.session_state:
                                st.session_state.confirm_delete = None
                            st.session_state.confirm_delete = athlete.id
                            st.rerun()
                else:
                    st.write("-")
            
            # Show inline edit modal if this athlete is being edited
            if st.session_state.edit_athlete_id == athlete.id:
                show_edit_modal_inline(db, athlete.id)
        
        # Delete Selected button below table
        st.markdown("---")
        if ENTRYDESK_WRITES_ENABLED and st.session_state.selected_athletes:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🗑️ Delete Selected", key="delete_selected_below", type="primary", use_container_width=True):
                    st.session_state.confirm_delete_selected = True
                    st.rerun()
        
        # Confirmation modal for delete selected
        if ENTRYDESK_WRITES_ENABLED and 'confirm_delete_selected' in st.session_state and st.session_state.confirm_delete_selected:
            st.warning(f"⚠️ Are you sure you want to delete {len(st.session_state.selected_athletes)} selected athlete(s)? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", key="confirm_delete_yes", type="primary", use_container_width=True):
                    deleted_count = 0
                    for athlete_id in st.session_state.selected_athletes:
                        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
                        if athlete:
                            db.delete(athlete)
                            deleted_count += 1
                    db.commit()
                    st.session_state.selected_athletes.clear()
                    st.session_state.confirm_delete_selected = False
                    st.success(f"✅ Deleted {deleted_count} athletes")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key="confirm_delete_no", use_container_width=True):
                    st.session_state.confirm_delete_selected = False
                    st.rerun()
        
        # Confirmation modal for individual delete
        if ENTRYDESK_WRITES_ENABLED and 'confirm_delete' in st.session_state and st.session_state.confirm_delete:
            athlete_to_delete = db.query(Athlete).filter(Athlete.id == st.session_state.confirm_delete).first()
            if athlete_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{athlete_to_delete.name}'? This action cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key="confirm_single_delete_yes", type="primary", use_container_width=True):
                        db.delete(athlete_to_delete)
                        db.commit()
                        st.session_state.selected_athletes.discard(st.session_state.confirm_delete)
                        st.session_state.confirm_delete = None
                        st.success(f"✅ Deleted {athlete_to_delete.name}")
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key="confirm_single_delete_no", use_container_width=True):
                        st.session_state.confirm_delete = None
                        st.rerun()
        
        # Pagination controls
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=(st.session_state.current_page == 0)):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col3:
                st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")
            
            with col5:
                if st.button("Next ➡️", disabled=(st.session_state.current_page >= total_pages - 1)):
                    st.session_state.current_page += 1
                    st.rerun()
        
        # Download as Excel
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 Download Filtered as Excel"):
                data = []
                for athlete in filtered_athletes:
                    data.append({
                        "ID": athlete.unique_id,
                        "Name": athlete.name,
                        "DOB": athlete.dob.strftime("%Y-%m-%d"),
                        "Dojo": athlete.dojo,
                        "Belt": athlete.belt,
                        "Day": athlete.day,
                        "Gender": athlete.gender if athlete.gender else "-",
                        "Registered": athlete.created_at.strftime("%Y-%m-%d %H:%M")
                    })
                df = pd.DataFrame(data)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Athletes')
                
                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name=f"athletes_{st.session_state.coach_name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


def show_edit_modal_inline(db, athlete_id):
    """Show inline edit form for an athlete - renders directly below the row"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("✏️ Editing is currently disabled.")
        st.session_state.edit_athlete_id = None
        return
    
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        st.error("Athlete not found")
        st.session_state.edit_athlete_id = None
        return
    
    # Initialize confirmation state
    if 'confirm_edit' not in st.session_state:
        st.session_state.confirm_edit = False
    if 'pending_edit_data' not in st.session_state:
        st.session_state.pending_edit_data = None
    
    # Create inline edit container with expander
    with st.expander(f"✏️ Editing: {athlete.name}", expanded=True):
        # Show confirmation dialog if needed
        if st.session_state.confirm_edit and st.session_state.pending_edit_data:
            st.warning("⚠️ Are you sure you want to save these changes?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Save", key=f"confirm_edit_yes_{athlete_id}", type="primary", use_container_width=True):
                    try:
                        # Apply the pending changes
                        data = st.session_state.pending_edit_data
                        athlete.name = data['name']
                        athlete.dob = data['dob']
                        athlete.dojo = data['dojo']
                        athlete.belt = data['belt']
                        athlete.day = data['day']
                        athlete.gender = data['gender']
                        athlete.updated_at = datetime.utcnow()
                        
                        db.commit()
                        st.success(f"✅ Successfully updated {data['name']}")
                        st.session_state.edit_athlete_id = None
                        st.session_state.confirm_edit = False
                        st.session_state.pending_edit_data = None
                        st.session_state.selected_athletes.clear()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error updating athlete: {str(e)}")
                        st.session_state.confirm_edit = False
                        st.session_state.pending_edit_data = None
            with col2:
                if st.button("❌ Cancel", key=f"confirm_edit_no_{athlete_id}", use_container_width=True):
                    st.session_state.confirm_edit = False
                    st.session_state.pending_edit_data = None
                    st.rerun()
        else:
            # Show edit form
            with st.form(f"edit_athlete_form_{athlete_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name *", value=athlete.name)
                    edit_dob = st.date_input("Date of Birth *", value=athlete.dob, max_value=date.today())
                    edit_dojo = st.text_input("Dojo *", value=athlete.dojo)
                
                with col2:
                    belt_options = ["White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"]
                    current_belt_idx = belt_options.index(athlete.belt) if athlete.belt in belt_options else 0
                    edit_belt = st.selectbox("Belt *", belt_options, index=current_belt_idx)
                    
                    day_options = ["Saturday", "Sunday"]
                    current_day_idx = day_options.index(athlete.day) if athlete.day in day_options else 0
                    edit_day = st.selectbox("Competition Day *", day_options, index=current_day_idx)
                    
                    gender_options = ["Male", "Female"]
                    # Handle case where gender might be None for legacy data
                    if athlete.gender and athlete.gender in gender_options:
                        current_gender_idx = gender_options.index(athlete.gender)
                    else:
                        current_gender_idx = 0
                    edit_gender = st.selectbox("Gender *", gender_options, index=current_gender_idx)
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted:
                    if not edit_name or not edit_dojo:
                        st.error("Please fill in all required fields")
                    else:
                        # Store pending data and show confirmation
                        st.session_state.pending_edit_data = {
                            'name': edit_name.strip(),
                            'dob': edit_dob,
                            'dojo': edit_dojo.strip(),
                            'belt': edit_belt,
                            'day': edit_day,
                            'gender': edit_gender
                        }
                        st.session_state.confirm_edit = True
                        st.rerun()
                
                if cancelled:
                    st.session_state.edit_athlete_id = None
                    st.session_state.confirm_edit = False
                    st.session_state.pending_edit_data = None
                    st.session_state.selected_athletes.clear()
                    st.rerun()


def show_edit_modal(db, athlete_id):
    """Show edit modal for an athlete"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("✏️ Editing is currently disabled.")
        st.session_state.edit_athlete_id = None
        return
    
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        st.error("Athlete not found")
        st.session_state.edit_athlete_id = None
        return
    
    # Initialize confirmation state
    if 'confirm_edit' not in st.session_state:
        st.session_state.confirm_edit = False
    if 'pending_edit_data' not in st.session_state:
        st.session_state.pending_edit_data = None
    
    # Create a modal-like container
    with st.container():
        st.markdown("---")
        st.subheader(f"✏️ Edit Athlete: {athlete.name}")
        
        # Show confirmation dialog if needed
        if st.session_state.confirm_edit and st.session_state.pending_edit_data:
            st.warning("⚠️ Are you sure you want to save these changes?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Save", key="confirm_edit_yes", type="primary", use_container_width=True):
                    try:
                        # Apply the pending changes
                        data = st.session_state.pending_edit_data
                        athlete.name = data['name']
                        athlete.dob = data['dob']
                        athlete.dojo = data['dojo']
                        athlete.belt = data['belt']
                        athlete.day = data['day']
                        athlete.gender = data['gender']
                        athlete.updated_at = datetime.utcnow()
                        
                        db.commit()
                        st.success(f"✅ Successfully updated {data['name']}")
                        st.session_state.edit_athlete_id = None
                        st.session_state.confirm_edit = False
                        st.session_state.pending_edit_data = None
                        st.session_state.selected_athletes.clear()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error updating athlete: {str(e)}")
                        st.session_state.confirm_edit = False
                        st.session_state.pending_edit_data = None
            with col2:
                if st.button("❌ Cancel", key="confirm_edit_no", use_container_width=True):
                    st.session_state.confirm_edit = False
                    st.session_state.pending_edit_data = None
                    st.rerun()
        else:
            # Show edit form
            with st.form("edit_athlete_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name *", value=athlete.name)
                    edit_dob = st.date_input("Date of Birth *", value=athlete.dob, max_value=date.today())
                    edit_dojo = st.text_input("Dojo *", value=athlete.dojo)
                
                with col2:
                    belt_options = ["White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"]
                    current_belt_idx = belt_options.index(athlete.belt) if athlete.belt in belt_options else 0
                    edit_belt = st.selectbox("Belt *", belt_options, index=current_belt_idx)
                    
                    day_options = ["Saturday", "Sunday"]
                    current_day_idx = day_options.index(athlete.day) if athlete.day in day_options else 0
                    edit_day = st.selectbox("Competition Day *", day_options, index=current_day_idx)
                    
                    gender_options = ["Male", "Female"]
                    # Handle case where gender might be None for legacy data
                    if athlete.gender and athlete.gender in gender_options:
                        current_gender_idx = gender_options.index(athlete.gender)
                    else:
                        current_gender_idx = 0
                    edit_gender = st.selectbox("Gender *", gender_options, index=current_gender_idx)
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted:
                    if not edit_name or not edit_dojo:
                        st.error("Please fill in all required fields")
                    else:
                        # Store pending data and show confirmation
                        st.session_state.pending_edit_data = {
                            'name': edit_name.strip(),
                            'dob': edit_dob,
                            'dojo': edit_dojo.strip(),
                            'belt': edit_belt,
                            'day': edit_day,
                            'gender': edit_gender
                        }
                        st.session_state.confirm_edit = True
                        st.rerun()
                
                if cancelled:
                    st.session_state.edit_athlete_id = None
                    st.session_state.confirm_edit = False
                    st.session_state.pending_edit_data = None
                    st.session_state.selected_athletes.clear()
                    st.rerun()
        
        st.markdown("---")

TEMPLATE_PATH = Path(__file__).parent / "templates" / "entrysheet-template.xlsx"

def upload_excel_tab(db):
    st.subheader("Upload Excel File")

    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("📤 Excel upload is currently disabled.")
        st.info("You can still download the template for future use.")

    st.markdown("### 📥 Download Template")
    st.write("First time uploading? Download our Excel template to see the required format.")

    # Prefer your static template if present, fallback to generated template
    if TEMPLATE_PATH.exists():
        template_bytes = TEMPLATE_PATH.read_bytes()
        file_name = TEMPLATE_PATH.name
    else:
        # Fallback to the existing programmatic template
        template_df = create_template_excel()
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            template_df.to_excel(writer, index=False, sheet_name="Athletes")
        template_bytes = buf.getvalue()
        file_name = "entrysheet-template.xlsx"

    st.download_button(
        label="Download Excel Template",
        data=template_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    if not ENTRYDESK_WRITES_ENABLED:
        return

    st.markdown("---")
    
    # Upload file
    st.markdown("### 📤 Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with columns: Name, DOB, Dojo, Belt, Day, Gender"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Process the file
            with st.spinner("Processing Excel file..."):
                df, errors = process_excel_file(tmp_file_path)
            
            # Display results
            if errors:
                st.error("❌ Validation errors / Skipped rows:")
                for error in errors:
                    st.write(f"- {error}")
            
            if not df.empty:
                st.success(f"✅ Successfully validated {len(df)} athletes")
                
                # Show preview
                st.write("Preview of data to be imported:")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Confirm import
                if st.button("Import Athletes", type="primary"):
                    accepted = 0
                    skipped = 0
                    skipped_rows = []
                    failed_rows = []
                    
                    with st.spinner("Importing athletes..."):
                        for idx, row in df.iterrows():
                            row_num = idx + 2  # Excel row number (accounting for header)
                            try:
                                athlete_name = str(row['name']).strip()
                                athlete_dob = row['dob'].date() if hasattr(row['dob'], 'date') else row['dob']
                                athlete_dojo = str(row['dojo']).strip()
                                
                                # Check for duplicate (case-insensitive, with space normalization)
                                existing = check_duplicate_athlete(db, athlete_name, athlete_dob, athlete_dojo)
                                if existing:
                                    skipped += 1
                                    skipped_rows.append(row_num)
                                    continue
                                
                                unique_id = get_next_unique_id(db)
                                
                                # Get gender (now required and normalized)
                                athlete_gender = str(row['gender']).strip()
                                
                                db_athlete = Athlete(
                                    unique_id=unique_id,
                                    name=athlete_name,
                                    dob=athlete_dob,
                                    dojo=athlete_dojo,
                                    belt=str(row['belt']).strip(),
                                    day=str(row['day']).strip(),
                                    gender=athlete_gender,
                                    coach_id=st.session_state.coach_id
                                )
                                db.add(db_athlete)
                                db.commit()
                                db.refresh(db_athlete)
                                accepted += 1
                            except Exception as e:
                                db.rollback()
                                failed_rows.append(row_num)
                    
                    # Show results - Display imported data table
                    if accepted > 0:
                        st.success(f"✅ Successfully imported {accepted} athletes!")
                        
                        # Show imported data in a table for 3 seconds
                        imported_athletes = db.query(Athlete).filter(
                            Athlete.coach_id == st.session_state.coach_id
                        ).order_by(Athlete.created_at.desc()).limit(accepted).all()
                        
                        if imported_athletes:
                            import_data = []
                            for athlete in imported_athletes:
                                import_data.append({
                                    "ID": athlete.unique_id,
                                    "Name": athlete.name,
                                    "DOB": athlete.dob.strftime("%Y-%m-%d"),
                                    "Dojo": athlete.dojo,
                                    "Belt": athlete.belt,
                                    "Day": athlete.day,
                                    "Gender": athlete.gender if athlete.gender else "-"
                                })
                            import_df = pd.DataFrame(import_data)
                            
                            # Create a placeholder for the table
                            table_placeholder = st.empty()
                            table_placeholder.dataframe(import_df, use_container_width=True, hide_index=True)
                            
                            # Wait 3 seconds then clear
                            import time
                            time.sleep(3)
                            table_placeholder.empty()
                    
                    if skipped > 0:
                        st.warning(f"⚠️ Skipped {skipped} duplicate entries - Rows: {', '.join(map(str, skipped_rows))}")
                    if failed_rows:
                        st.error(f"❌ Failed to import rows: {', '.join(map(str, failed_rows))}")
                    
                    if accepted > 0:
                        st.balloons()
                    st.rerun()
            else:
                st.warning("No valid data found in the Excel file. Please check the format and try again.")
        
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)


def add_athlete_tab(db):
    """Tab for adding individual athlete"""
    st.subheader("Add Individual Athlete")
    
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("➕ Manual athlete addition is currently disabled.")
        return
    
    with st.form("add_athlete_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="Athlete Name")
            dob = st.date_input("Date of Birth *", max_value=date.today())
            dojo = st.text_input("Dojo *", placeholder="Dojo Name")
        
        with col2:
            belt_options = ["White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"]
            belt = st.selectbox("Belt *", belt_options)
            day = st.selectbox("Competition Day *", ["Saturday", "Sunday"])
            gender = st.selectbox("Gender *", ["Male", "Female"])
        
        submitted = st.form_submit_button("Add Athlete", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not dojo:
                st.error("Please fill in all required fields")
            else:
                try:
                    # Check for duplicate athlete (case-insensitive, with space normalization)
                    existing = check_duplicate_athlete(db, name.strip(), dob, dojo.strip())
                    if existing:
                        st.error(f"❌ Duplicate entry! An athlete named '{name}' with DOB {dob} and Dojo '{dojo}' is already registered (ID: {existing.unique_id})")
                    else:
                        unique_id = get_next_unique_id(db)
                        db_athlete = Athlete(
                            unique_id=unique_id,
                            name=name.strip(),
                            dob=dob,
                            dojo=dojo.strip(),
                            belt=belt,
                            day=day,
                            gender=gender,
                            coach_id=st.session_state.coach_id
                        )
                        db.add(db_athlete)
                        db.commit()
                        
                        st.success(f"✅ Successfully added {name} with ID: {unique_id}")
                        st.balloons()
                        st.rerun()
                
                except Exception as e:
                    db.rollback()
                    st.error(f"Error adding athlete: {str(e)}")


def admin_dashboard_page():
    """Display admin dashboard with all athletes"""
    # Sidebar
    with st.sidebar:
        st.title("🥋 EntryDesk Admin")
        st.markdown(f"**Admin:** {st.session_state.coach_name}")
        st.markdown(f"**Email:** {st.session_state.coach_email}")
        
        # Database status - compact warning
        from database import DATABASE_URL
        if DATABASE_URL.startswith("sqlite"):
            st.divider()
            st.caption("⚠️ Using local database - data will be lost on reboot")
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.coach_id = None
            st.session_state.coach_email = None
            st.session_state.coach_name = None
            st.session_state.is_admin = False
            st.session_state.auth_token = None
            st.rerun()
    
    # Main content
    st.title("Admin Dashboard")
    st.markdown("### 👨‍💼 All Tournament Entries")
    
    # Show IST timer banner if enabled (display-only, does NOT enforce writes)
    show_ist_timer_banner()
    
    # Show write lockdown message if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        show_writes_disabled_message()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Fetch all athletes from all coaches
        athletes = db.query(Athlete).all()
        coaches = db.query(Coach).all()
        
        # Display statistics
        st.header("📊 Overall Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Coaches", len(coaches))
        
        with col2:
            st.metric("Total Athletes", len(athletes))
        
        saturday_count = sum(1 for a in athletes if a.day == 'Saturday')
        with col3:
            st.metric("Saturday", saturday_count)
        
        sunday_count = sum(1 for a in athletes if a.day == 'Sunday')
        with col4:
            st.metric("Sunday", sunday_count)
        
        # Count unique belts
        belts = set(a.belt for a in athletes)
        with col5:
            st.metric("Belt Levels", len(belts))
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📋 All Athletes", "👥 By Coach", "📊 Statistics", "📤 Upload Excel"])
        
        with tab1:
            view_all_athletes_tab(db, athletes)
        
        with tab2:
            view_by_coach_tab(db, coaches)
        
        with tab3:
            view_statistics_tab(db, athletes, coaches)
        
        with tab4:
            admin_upload_excel_tab(db, coaches)
    
    finally:
        db.close()


def view_all_athletes_tab(db, athletes):
    """Admin tab for viewing all athletes with pagination, edit, and delete"""
    st.subheader("All Registered Athletes")
    
    if not athletes:
        st.info("No athletes registered yet.")
        return
    
    # Initialize session state for admin selections
    if 'admin_selected_athletes' not in st.session_state:
        st.session_state.admin_selected_athletes = set()
    if 'admin_current_page' not in st.session_state:
        st.session_state.admin_current_page = 0
    if 'admin_edit_athlete_id' not in st.session_state:
        st.session_state.admin_edit_athlete_id = None
    
    # Search and filter functionality
    st.markdown("#### Search Functionalities")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        search_query = st.text_input("🔍 Search by name, dojo, or belt", key="admin_search")
    with col2:
        day_filter = st.selectbox("Filter by day", ["All", "Saturday", "Sunday"], key="admin_day_filter")
    with col3:
        belt_filter = st.selectbox("Filter by belt", ["All", "White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"], key="admin_belt_filter")
    with col4:
        gender_filter = st.selectbox("Filter by gender", ["All", "Male", "Female"], key="admin_gender_filter")
    with col5:
        # Get unique coach names
        coaches = db.query(Coach).all()
        coach_names = ["All"] + [c.name for c in coaches]
        coach_filter = st.selectbox("Filter by coach", coach_names, key="admin_coach_filter")
    
    # Filter athletes
    filtered_athletes = athletes
    if search_query:
        filtered_athletes = [
            a for a in filtered_athletes
            if search_query.lower() in a.name.lower() or
               search_query.lower() in a.dojo.lower() or
               search_query.lower() in a.belt.lower()
        ]
    
    if day_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.day == day_filter]
    
    if belt_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.belt == belt_filter]
    
    if gender_filter != "All":
        filtered_athletes = [a for a in filtered_athletes if a.gender == gender_filter]
    
    if coach_filter != "All":
        coach = next((c for c in coaches if c.name == coach_filter), None)
        if coach:
            filtered_athletes = [a for a in filtered_athletes if a.coach_id == coach.id]
    
    # Pagination setup
    items_per_page = 100
    total_pages = (len(filtered_athletes) + items_per_page - 1) // items_per_page
    
    # Ensure current page is within bounds
    if st.session_state.admin_current_page >= total_pages:
        st.session_state.admin_current_page = max(0, total_pages - 1)
    
    start_idx = st.session_state.admin_current_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_athletes))
    page_athletes = filtered_athletes[start_idx:end_idx]
    
    st.write(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_athletes)} athletes (Total: {len(athletes)})")
    
    st.markdown("")
    
    # Display athletes with checkboxes
    if page_athletes:
        # Table header
        st.markdown("#### Athlete List")
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.5, 1, 2, 2, 1.5, 1, 1, 1, 1.5, 1])
        with col1:
            # Header checkbox to select/deselect all visible rows
            all_selected = all(a.id in st.session_state.admin_selected_athletes for a in page_athletes)
            admin_header_check = st.checkbox("", value=all_selected, key="admin_header_select_all", label_visibility="collapsed")
            # Handle state change only if value actually changed
            if admin_header_check != all_selected:
                if admin_header_check:
                    # Select all on current page
                    st.session_state.admin_selected_athletes.update([a.id for a in page_athletes])
                else:
                    # Deselect all on current page
                    for a in page_athletes:
                        st.session_state.admin_selected_athletes.discard(a.id)
        with col2:
            st.markdown("**ID**")
        with col3:
            st.markdown("**Name**")
        with col4:
            st.markdown("**Dojo**")
        with col5:
            st.markdown("**DOB**")
        with col6:
            st.markdown("**Belt**")
        with col7:
            st.markdown("**Day**")
        with col8:
            st.markdown("**Gender**")
        with col9:
            st.markdown("**Coach**")
        with col10:
            st.markdown("**Actions**")
        
        st.markdown("---")
        
        for athlete in page_athletes:
            coach = db.query(Coach).filter(Coach.id == athlete.coach_id).first()
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.5, 1, 2, 2, 1.5, 1, 1, 1, 1.5, 1])
            
            with col1:
                is_selected = athlete.id in st.session_state.admin_selected_athletes
                admin_checkbox_value = st.checkbox("", value=is_selected, key=f"admin_cb_{athlete.id}", label_visibility="collapsed")
                # Handle state change only if value actually changed
                if admin_checkbox_value != is_selected:
                    if admin_checkbox_value:
                        st.session_state.admin_selected_athletes.add(athlete.id)
                    else:
                        st.session_state.admin_selected_athletes.discard(athlete.id)
            
            with col2:
                st.write(f"**{athlete.unique_id}**")
            with col3:
                st.write(athlete.name)
            with col4:
                st.write(athlete.dojo)
            with col5:
                st.write(athlete.dob.strftime("%Y-%m-%d"))
            with col6:
                st.write(athlete.belt)
            with col7:
                st.write(athlete.day)
            with col8:
                st.write(athlete.gender if athlete.gender else "-")
            with col9:
                st.write(coach.name if coach else "Unknown")
            with col10:
                # Edit and Delete icons for each entry
                if ENTRYDESK_WRITES_ENABLED:
                    admin_action_col1, admin_action_col2 = st.columns(2)
                    with admin_action_col1:
                        if st.button("✏️", key=f"admin_edit_{athlete.id}", help="Edit athlete"):
                            st.session_state.admin_edit_athlete_id = athlete.id
                            st.rerun()
                    with admin_action_col2:
                        if st.button("🗑️", key=f"admin_delete_{athlete.id}", help="Delete athlete"):
                            # Set up delete confirmation
                            if 'admin_confirm_delete' not in st.session_state:
                                st.session_state.admin_confirm_delete = None
                            st.session_state.admin_confirm_delete = athlete.id
                            st.rerun()
                else:
                    st.write("-")
            
            # Show inline edit modal if this athlete is being edited
            if st.session_state.admin_edit_athlete_id == athlete.id:
                show_admin_edit_modal_inline(db, athlete.id)
        
        # Delete Selected button below table
        st.markdown("---")
        if ENTRYDESK_WRITES_ENABLED and st.session_state.admin_selected_athletes:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🗑️ Delete Selected", key="admin_delete_selected_below", type="primary", use_container_width=True):
                    st.session_state.admin_confirm_delete_selected = True
                    st.rerun()
        
        # Confirmation modal for delete selected
        if ENTRYDESK_WRITES_ENABLED and 'admin_confirm_delete_selected' in st.session_state and st.session_state.admin_confirm_delete_selected:
            st.warning(f"⚠️ Are you sure you want to delete {len(st.session_state.admin_selected_athletes)} selected athlete(s)? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", key="admin_confirm_delete_yes", type="primary", use_container_width=True):
                    deleted_count = 0
                    for athlete_id in st.session_state.admin_selected_athletes:
                        athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
                        if athlete:
                            db.delete(athlete)
                            deleted_count += 1
                    db.commit()
                    st.session_state.admin_selected_athletes.clear()
                    st.session_state.admin_confirm_delete_selected = False
                    st.success(f"✅ Deleted {deleted_count} athletes")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key="admin_confirm_delete_no", use_container_width=True):
                    st.session_state.admin_confirm_delete_selected = False
                    st.rerun()
        
        # Confirmation modal for individual delete
        if ENTRYDESK_WRITES_ENABLED and 'admin_confirm_delete' in st.session_state and st.session_state.admin_confirm_delete:
            athlete_to_delete = db.query(Athlete).filter(Athlete.id == st.session_state.admin_confirm_delete).first()
            if athlete_to_delete:
                st.warning(f"⚠️ Are you sure you want to delete '{athlete_to_delete.name}'? This action cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key="admin_confirm_single_delete_yes", type="primary", use_container_width=True):
                        db.delete(athlete_to_delete)
                        db.commit()
                        st.session_state.admin_selected_athletes.discard(st.session_state.admin_confirm_delete)
                        st.session_state.admin_confirm_delete = None
                        st.success(f"✅ Deleted {athlete_to_delete.name}")
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key="admin_confirm_single_delete_no", use_container_width=True):
                        st.session_state.admin_confirm_delete = None
                        st.rerun()
        
        # Pagination controls
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⬅️ Previous", key="admin_prev", disabled=(st.session_state.admin_current_page == 0)):
                    st.session_state.admin_current_page -= 1
                    st.rerun()
            
            with col3:
                st.write(f"Page {st.session_state.admin_current_page + 1} of {total_pages}")
            
            with col5:
                if st.button("Next ➡️", key="admin_next", disabled=(st.session_state.admin_current_page >= total_pages - 1)):
                    st.session_state.admin_current_page += 1
                    st.rerun()
        
        # Download as Excel
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 Download Filtered as Excel", key="admin_download"):
                data = []
                for athlete in filtered_athletes:
                    coach = db.query(Coach).filter(Coach.id == athlete.coach_id).first()
                    data.append({
                        "ID": athlete.unique_id,
                        "Name": athlete.name,
                        "DOB": athlete.dob.strftime("%Y-%m-%d"),
                        "Dojo": athlete.dojo,
                        "Belt": athlete.belt,
                        "Day": athlete.day,
                        "Gender": athlete.gender if athlete.gender else "-",
                        "Coach": coach.name if coach else "Unknown",
                        "Registered": athlete.created_at.strftime("%Y-%m-%d %H:%M")
                    })
                df = pd.DataFrame(data)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='All Athletes')
                
                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name=f"all_athletes_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


def show_admin_edit_modal_inline(db, athlete_id):
    """Show inline edit form for an athlete (admin version) - renders directly below the row"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("✏️ Editing is currently disabled.")
        st.session_state.admin_edit_athlete_id = None
        return
    
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        st.error("Athlete not found")
        st.session_state.admin_edit_athlete_id = None
        return
    
    # Initialize confirmation state
    if 'admin_confirm_edit' not in st.session_state:
        st.session_state.admin_confirm_edit = False
    if 'admin_pending_edit_data' not in st.session_state:
        st.session_state.admin_pending_edit_data = None
    
    # Create inline edit container with expander
    with st.expander(f"✏️ Editing: {athlete.name}", expanded=True):
        # Show confirmation dialog if needed
        if st.session_state.admin_confirm_edit and st.session_state.admin_pending_edit_data:
            st.warning("⚠️ Are you sure you want to save these changes?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Save", key=f"admin_confirm_edit_yes_{athlete_id}", type="primary", use_container_width=True):
                    try:
                        # Apply the pending changes
                        data = st.session_state.admin_pending_edit_data
                        athlete.name = data['name']
                        athlete.dob = data['dob']
                        athlete.dojo = data['dojo']
                        athlete.belt = data['belt']
                        athlete.day = data['day']
                        athlete.gender = data['gender']
                        athlete.updated_at = datetime.utcnow()
                        
                        db.commit()
                        st.success(f"✅ Successfully updated {data['name']}")
                        st.session_state.admin_edit_athlete_id = None
                        st.session_state.admin_confirm_edit = False
                        st.session_state.admin_pending_edit_data = None
                        st.session_state.admin_selected_athletes.clear()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error updating athlete: {str(e)}")
                        st.session_state.admin_confirm_edit = False
                        st.session_state.admin_pending_edit_data = None
            with col2:
                if st.button("❌ Cancel", key=f"admin_confirm_edit_no_{athlete_id}", use_container_width=True):
                    st.session_state.admin_confirm_edit = False
                    st.session_state.admin_pending_edit_data = None
                    st.rerun()
        else:
            # Show edit form
            with st.form(f"admin_edit_athlete_form_{athlete_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name *", value=athlete.name)
                    edit_dob = st.date_input("Date of Birth *", value=athlete.dob, max_value=date.today())
                    edit_dojo = st.text_input("Dojo *", value=athlete.dojo)
                
                with col2:
                    belt_options = ["White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"]
                    current_belt_idx = belt_options.index(athlete.belt) if athlete.belt in belt_options else 0
                    edit_belt = st.selectbox("Belt *", belt_options, index=current_belt_idx)
                    
                    day_options = ["Saturday", "Sunday"]
                    current_day_idx = day_options.index(athlete.day) if athlete.day in day_options else 0
                    edit_day = st.selectbox("Competition Day *", day_options, index=current_day_idx)
                    
                    gender_options = ["Male", "Female"]
                    # Handle case where gender might be None for legacy data
                    if athlete.gender and athlete.gender in gender_options:
                        current_gender_idx = gender_options.index(athlete.gender)
                    else:
                        current_gender_idx = 0
                    edit_gender = st.selectbox("Gender *", gender_options, index=current_gender_idx)
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted:
                    if not edit_name or not edit_dojo:
                        st.error("Please fill in all required fields")
                    else:
                        # Store pending data and show confirmation
                        st.session_state.admin_pending_edit_data = {
                            'name': edit_name.strip(),
                            'dob': edit_dob,
                            'dojo': edit_dojo.strip(),
                            'belt': edit_belt,
                            'day': edit_day,
                            'gender': edit_gender
                        }
                        st.session_state.admin_confirm_edit = True
                        st.rerun()
                
                if cancelled:
                    st.session_state.admin_edit_athlete_id = None
                    st.session_state.admin_confirm_edit = False
                    st.session_state.admin_pending_edit_data = None
                    st.session_state.admin_selected_athletes.clear()
                    st.rerun()


def show_admin_edit_modal(db, athlete_id):
    """Show edit modal for an athlete (admin version)"""
    # Check if writes are disabled
    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("✏️ Editing is currently disabled.")
        st.session_state.admin_edit_athlete_id = None
        return
    
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        st.error("Athlete not found")
        st.session_state.admin_edit_athlete_id = None
        return
    
    # Initialize confirmation state
    if 'admin_confirm_edit' not in st.session_state:
        st.session_state.admin_confirm_edit = False
    if 'admin_pending_edit_data' not in st.session_state:
        st.session_state.admin_pending_edit_data = None
    
    # Create a modal-like container
    with st.container():
        st.markdown("---")
        st.subheader(f"✏️ Edit Athlete: {athlete.name}")
        
        # Show confirmation dialog if needed
        if st.session_state.admin_confirm_edit and st.session_state.admin_pending_edit_data:
            st.warning("⚠️ Are you sure you want to save these changes?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Save", key="admin_confirm_edit_yes", type="primary", use_container_width=True):
                    try:
                        # Apply the pending changes
                        data = st.session_state.admin_pending_edit_data
                        athlete.name = data['name']
                        athlete.dob = data['dob']
                        athlete.dojo = data['dojo']
                        athlete.belt = data['belt']
                        athlete.day = data['day']
                        athlete.gender = data['gender']
                        athlete.updated_at = datetime.utcnow()
                        
                        db.commit()
                        st.success(f"✅ Successfully updated {data['name']}")
                        st.session_state.admin_edit_athlete_id = None
                        st.session_state.admin_confirm_edit = False
                        st.session_state.admin_pending_edit_data = None
                        st.session_state.admin_selected_athletes.clear()
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error updating athlete: {str(e)}")
                        st.session_state.admin_confirm_edit = False
                        st.session_state.admin_pending_edit_data = None
            with col2:
                if st.button("❌ Cancel", key="admin_confirm_edit_no", use_container_width=True):
                    st.session_state.admin_confirm_edit = False
                    st.session_state.admin_pending_edit_data = None
                    st.rerun()
        else:
            # Show edit form
            with st.form("admin_edit_athlete_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name *", value=athlete.name)
                    edit_dob = st.date_input("Date of Birth *", value=athlete.dob, max_value=date.today())
                    edit_dojo = st.text_input("Dojo *", value=athlete.dojo)
                
                with col2:
                    belt_options = ["White", "Yellow", "Blue", "Purple", "Green", "Brown", "Black"]
                    current_belt_idx = belt_options.index(athlete.belt) if athlete.belt in belt_options else 0
                    edit_belt = st.selectbox("Belt *", belt_options, index=current_belt_idx)
                    
                    day_options = ["Saturday", "Sunday"]
                    current_day_idx = day_options.index(athlete.day) if athlete.day in day_options else 0
                    edit_day = st.selectbox("Competition Day *", day_options, index=current_day_idx)
                    
                    gender_options = ["Male", "Female"]
                    # Handle case where gender might be None for legacy data
                    if athlete.gender and athlete.gender in gender_options:
                        current_gender_idx = gender_options.index(athlete.gender)
                    else:
                        current_gender_idx = 0
                    edit_gender = st.selectbox("Gender *", gender_options, index=current_gender_idx)
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with col_cancel:
                    cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if submitted:
                    if not edit_name or not edit_dojo:
                        st.error("Please fill in all required fields")
                    else:
                        # Store pending data and show confirmation
                        st.session_state.admin_pending_edit_data = {
                            'name': edit_name.strip(),
                            'dob': edit_dob,
                            'dojo': edit_dojo.strip(),
                            'belt': edit_belt,
                            'day': edit_day,
                            'gender': edit_gender
                        }
                        st.session_state.admin_confirm_edit = True
                        st.rerun()
                
                if cancelled:
                    st.session_state.admin_edit_athlete_id = None
                    st.session_state.admin_confirm_edit = False
                    st.session_state.admin_pending_edit_data = None
                    st.session_state.admin_selected_athletes.clear()
                    st.rerun()
        
        st.markdown("---")


def view_by_coach_tab(db, coaches):
    """Admin tab for viewing athletes by coach"""
    st.subheader("Athletes by Coach")
    
    if not coaches:
        st.info("No coaches registered yet.")
        return
    
    # Create a dropdown to select coach
    coach_names = {f"{c.name} ({c.email})": c.id for c in coaches}
    selected_coach_name = st.selectbox("Select Coach", ["All Coaches"] + list(coach_names.keys()))
    
    if selected_coach_name == "All Coaches":
        # Show summary for all coaches
        st.markdown("### Summary by Coach")
        coach_data = []
        for coach in coaches:
            athletes = db.query(Athlete).filter(Athlete.coach_id == coach.id).all()
            coach_data.append({
                "Coach": coach.name,
                "Email": coach.email,
                "Total Athletes": len(athletes),
                "Saturday": sum(1 for a in athletes if a.day == 'Saturday'),
                "Sunday": sum(1 for a in athletes if a.day == 'Sunday')
            })
        
        df = pd.DataFrame(coach_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        # Show details for selected coach
        coach_id = coach_names[selected_coach_name]
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        athletes = db.query(Athlete).filter(Athlete.coach_id == coach_id).all()
        
        st.markdown(f"### {coach.name}")
        st.write(f"**Email:** {coach.email}")
        st.write(f"**Total Athletes:** {len(athletes)}")
        
        if athletes:
            data = []
            for athlete in athletes:
                data.append({
                    "ID": athlete.unique_id,
                    "Name": athlete.name,
                    "DOB": athlete.dob.strftime("%Y-%m-%d"),
                    "Dojo": athlete.dojo,
                    "Belt": athlete.belt,
                    "Day": athlete.day,
                    "Registered": athlete.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)


def view_statistics_tab(db, athletes, coaches):
    """Admin tab for viewing statistics"""
    st.subheader("Tournament Statistics")
    
    if not athletes:
        st.info("No data available yet.")
        return
    
    # Belt distribution
    st.markdown("### Belt Distribution")
    belt_counts = {}
    for athlete in athletes:
        belt_counts[athlete.belt] = belt_counts.get(athlete.belt, 0) + 1
    
    belt_df = pd.DataFrame(list(belt_counts.items()), columns=['Belt', 'Count'])
    belt_df = belt_df.sort_values('Count', ascending=False)
    st.bar_chart(belt_df.set_index('Belt'))
    
    # Day distribution
    st.markdown("### Competition Day Distribution")
    col1, col2 = st.columns(2)
    saturday_count = sum(1 for a in athletes if a.day == 'Saturday')
    sunday_count = sum(1 for a in athletes if a.day == 'Sunday')
    
    with col1:
        st.metric("Saturday Participants", saturday_count)
    with col2:
        st.metric("Sunday Participants", sunday_count)
    
    # Top dojos
    st.markdown("### Top Dojos")
    dojo_counts = {}
    for athlete in athletes:
        dojo_counts[athlete.dojo] = dojo_counts.get(athlete.dojo, 0) + 1
    
    dojo_df = pd.DataFrame(list(dojo_counts.items()), columns=['Dojo', 'Athletes'])
    dojo_df = dojo_df.sort_values('Athletes', ascending=False).head(10)
    st.dataframe(dojo_df, use_container_width=True, hide_index=True)


def admin_upload_excel_tab(db, coaches):
    st.subheader("Upload Excel File (Admin)")

    if not ENTRYDESK_WRITES_ENABLED:
        st.warning("📤 Excel upload is currently disabled.")
        st.info("You can still download the template for future use.")

    st.markdown("### 📥 Download Template")
    st.write("Download the Excel template to see the required format.")

    if TEMPLATE_PATH.exists():
        template_bytes = TEMPLATE_PATH.read_bytes()
        file_name = TEMPLATE_PATH.name
    else:
        template_df = create_template_excel()
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            template_df.to_excel(writer, index=False, sheet_name="Athletes")
        template_bytes = buf.getvalue()
        file_name = "athlete_template.xlsx"

    st.download_button(
        label="Download Excel Template",
        data=template_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    if not ENTRYDESK_WRITES_ENABLED:
        return

    st.markdown("### 📤 Upload Your File")
    
    # Coach selection
    st.markdown("### 👤 Select Coach")
    st.write("Select the coach to whom this upload should be attributed:")
    
    if not coaches:
        st.error("No coaches found in the system. Please have at least one coach log in first.")
        return
    
    # Create coach options with name and email
    coach_options = [f"{coach.name} ({coach.email})" for coach in coaches]
    selected_coach_str = st.selectbox(
        "Coach *",
        coach_options,
        help="All imported athletes will be attributed to this coach"
    )
    
    # Get the selected coach object
    selected_coach_idx = coach_options.index(selected_coach_str)
    selected_coach = coaches[selected_coach_idx]
    
    st.info(f"Athletes will be imported for coach: **{selected_coach.name}** ({selected_coach.email})")
    
    st.markdown("---")
    
    # Upload file
    st.markdown("### 📤 Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with columns: Name, DOB, Dojo, Belt, Day, Gender",
        key="admin_upload"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Process the file
            with st.spinner("Processing Excel file..."):
                df, errors = process_excel_file(tmp_file_path)
            
            # Display results
            if errors:
                st.error("❌ Validation errors / Skipped rows:")
                for error in errors:
                    st.write(f"- {error}")
            
            if not df.empty:
                st.success(f"✅ Successfully validated {len(df)} athletes")
                
                # Show preview
                st.write("Preview of data to be imported:")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Confirm import
                if st.button("Import Athletes", type="primary", key="admin_import_btn"):
                    accepted = 0
                    skipped = 0
                    skipped_rows = []
                    failed_rows = []
                    
                    with st.spinner("Importing athletes..."):
                        for idx, row in df.iterrows():
                            row_num = idx + 2  # Excel row number (accounting for header)
                            try:
                                athlete_name = str(row['name']).strip()
                                athlete_dob = row['dob'].date() if hasattr(row['dob'], 'date') else row['dob']
                                athlete_dojo = str(row['dojo']).strip()
                                
                                # Check for duplicate (case-insensitive, with space normalization)
                                existing = check_duplicate_athlete(db, athlete_name, athlete_dob, athlete_dojo)
                                if existing:
                                    skipped += 1
                                    skipped_rows.append(row_num)
                                    continue
                                
                                unique_id = get_next_unique_id(db)
                                
                                # Get gender (now required and normalized)
                                athlete_gender = str(row['gender']).strip()
                                
                                db_athlete = Athlete(
                                    unique_id=unique_id,
                                    name=athlete_name,
                                    dob=athlete_dob,
                                    dojo=athlete_dojo,
                                    belt=str(row['belt']).strip(),
                                    day=str(row['day']).strip(),
                                    gender=athlete_gender,
                                    coach_id=selected_coach.id  # Use selected coach
                                )
                                db.add(db_athlete)
                                db.commit()
                                db.refresh(db_athlete)
                                accepted += 1
                            except Exception as e:
                                db.rollback()
                                failed_rows.append(row_num)
                    
                    # Show results - Display imported data table
                    if accepted > 0:
                        st.success(f"✅ Successfully imported {accepted} athletes for {selected_coach.name}!")
                        
                        # Show imported data in a table for 3 seconds
                        imported_athletes = db.query(Athlete).filter(
                            Athlete.coach_id == selected_coach.id
                        ).order_by(Athlete.created_at.desc()).limit(accepted).all()
                        
                        if imported_athletes:
                            import_data = []
                            for athlete in imported_athletes:
                                import_data.append({
                                    "ID": athlete.unique_id,
                                    "Name": athlete.name,
                                    "DOB": athlete.dob.strftime("%Y-%m-%d"),
                                    "Dojo": athlete.dojo,
                                    "Belt": athlete.belt,
                                    "Day": athlete.day,
                                    "Gender": athlete.gender if athlete.gender else "-"
                                })
                            import_df = pd.DataFrame(import_data)
                            
                            # Create a placeholder for the table
                            table_placeholder = st.empty()
                            table_placeholder.dataframe(import_df, use_container_width=True, hide_index=True)
                            
                            # Wait 3 seconds then clear
                            import time
                            time.sleep(3)
                            table_placeholder.empty()
                    
                    if skipped > 0:
                        st.warning(f"⚠️ Skipped {skipped} duplicate entries - Rows: {', '.join(map(str, skipped_rows))}")
                    if failed_rows:
                        st.error(f"❌ Failed to import rows: {', '.join(map(str, failed_rows))}")
                    
                    if accepted > 0:
                        st.balloons()
                    st.rerun()
            else:
                st.warning("No valid data found in the Excel file. Please check the format and try again.")
        
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)


def main():
    """Main application"""
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.is_admin:
            admin_dashboard_page()
        else:
            dashboard_page()


if __name__ == "__main__":
    main()
