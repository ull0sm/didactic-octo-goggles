# Session Persistence in Streamlit

## Overview
Streamlit's session state is designed to persist data within a single browser session, but it is **reset on page reload** by default. This is expected behavior for Streamlit applications.

## Current Implementation

### OAuth Flow
The application uses `streamlit-oauth` for Google OAuth authentication. The OAuth flow works as follows:

1. User clicks "Sign in with Google"
2. User is redirected to Google's authentication page
3. After successful authentication, user is redirected back with an OAuth token
4. The application stores user information in session state:
   - `logged_in`: Boolean flag
   - `coach_id`: Database ID of the coach
   - `coach_email`: Email address
   - `coach_name`: Display name
   - `is_admin`: Admin status
   - `auth_token`: OAuth access token

### Session Persistence Behavior

**What works:**
- Session state persists during navigation within the app (without page reload)
- OAuth tokens are managed by the `streamlit-oauth` library
- User data is stored in the database for future logins

**Known limitation:**
- When the browser page is refreshed (F5 or Ctrl+R), Streamlit clears all session state
- This causes the user to appear logged out after a page refresh
- The OAuth component should re-authenticate automatically if configured properly

## Solutions

### For Production Deployment

1. **Streamlit Cloud Deployment**: When deployed on Streamlit Cloud with proper OAuth configuration, the OAuth flow typically handles re-authentication more smoothly.

2. **Session Cookies**: For production deployments, consider implementing browser-based session storage using:
   - `streamlit-cookies-manager` package
   - Custom JavaScript components for localStorage
   - Server-side session management

3. **OAuth Token Refresh**: Ensure OAuth tokens have reasonable expiration times and implement token refresh logic.

### Current Workaround

Users should:
- Avoid refreshing the page unnecessarily
- Use the application's navigation (tabs, buttons) instead of browser refresh
- Keep their browser tab open during their work session
- Re-authenticate via Google OAuth if they need to refresh

## Code Changes Made

Added `auth_token` to session state initialization (line 49-50 in app.py):
```python
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
```

This prepares the application for future token-based session management if needed.

## Future Improvements

1. Implement browser-based session storage (cookies/localStorage)
2. Add "Remember Me" functionality
3. Implement automatic token refresh
4. Add session timeout warnings
5. Store minimal session data in encrypted cookies

## References

- [Streamlit Session State Documentation](https://docs.streamlit.io/library/api-reference/session-state)
- [streamlit-oauth Library](https://github.com/dnplus/streamlit-oauth)
- [Streamlit Cookies Manager](https://github.com/ktosiek/streamlit-cookies-manager)
