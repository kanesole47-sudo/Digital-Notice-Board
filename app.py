# app.py
# Purpose: Main Execution Router — Routes to auth, student, or admin dashboard
# Run with: streamlit run app.py

import streamlit as st
from database_schema import init_db

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title='College Notice Board',
    page_icon='🏫',
    layout='wide',
    initial_sidebar_state='collapsed'
)


def main():
    """Main router function"""
    # Enable PWA features (mobile installability)
    from pwa_setup import enable_pwa
    enable_pwa()
    
    # Initialize database on first run
    init_db()
    
    # Check if user is logged in
    if not st.session_state.get('logged_in', False):
        # Not logged in -> show auth page
        from auth_login import render_auth_page
        render_auth_page()
    else:
        # Logged in -> route based on role
        role = st.session_state.get('user_role', 'student')
        
        if role == 'admin':
            from admin_dashboard import render_admin_dashboard
            render_admin_dashboard()
        else:
            from student_dashboard import render_student_dashboard
            render_student_dashboard()


if __name__ == '__main__':
    main()
