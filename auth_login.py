# auth_login.py
# Purpose: Google-Style Minimalist Authentication UI & Logic

import streamlit as st
import bcrypt
from database_schema import get_session, User, init_db
from ui_styles import inject_css, STREAMS, YEARS, DIVISIONS, ADMIN_PASSKEY
from file_handler import save_uploaded_file, validate_file_type


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify a password against its bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def render_auth_page():
    """Renders the complete authentication page with login and registration tabs"""
    # Initialize database
    init_db()
    
    # Inject CSS
    inject_css()
    
    # Auth header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 24px;'>
        <h2 style='font-size: 1.8rem; font-weight: 700; color: #202124; margin-bottom: 8px;'>🏫 College Notice Board</h2>
        <p style='font-size: 0.95rem; color: #5F6368; margin: 0;'>Sign in to access your personalized notice feed</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(['🔑 Sign In', '📝 Register'])
    
    with tab_login:
        _render_login_form()
    
    with tab_register:
        _render_register_form()


def _render_login_form():
    """Renders the login form"""
    with st.form('login_form', clear_on_submit=False):
        email = st.text_input('📧 Email Address', placeholder='student@college.edu')
        password = st.text_input('🔒 Password', type='password', placeholder='Enter your password')
        
        submitted = st.form_submit_button('Sign In', use_container_width=True, type='primary')
        
        if submitted:
            if not email or not password:
                st.error('⚠️ Please fill in all fields.')
                return
            
            session = get_session()
            try:
                user = session.query(User).filter_by(email=email.strip().lower()).first()
                
                if user and verify_password(password, user.password_hash):
                    # Set session state
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user.id
                    st.session_state['user_email'] = user.email
                    st.session_state['user_role'] = user.role
                    st.session_state['user_stream'] = user.stream
                    st.session_state['user_year'] = user.year
                    st.session_state['user_division'] = user.division
                    st.session_state['user_seat'] = user.seat_number
                    st.session_state['user_pic'] = user.profile_pic_path
                    st.success('✅ Login successful! Redirecting...')
                    st.rerun()
                else:
                    st.error('❌ Invalid email or password.')
            finally:
                session.close()


def _render_register_form():
    """Renders the registration form"""
    role = st.radio('👤 Register As', ['Student', 'Admin'], horizontal=True, key='reg_role_selector')
    
    with st.form('register_form', clear_on_submit=False):
        email = st.text_input('📧 Email Address', placeholder='student@college.edu', key='reg_email')
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input('🔒 Password', type='password', key='reg_pass')
        with col2:
            confirm_password = st.text_input('🔒 Confirm Password', type='password', key='reg_confirm')
        
        # Role-specific fields
        if role == 'Admin':
            admin_passkey = st.text_input(
                '🔐 Admin Secret Passkey',
                type='password',
                placeholder='Enter college admin passkey',
                key='reg_passkey',
                help='Passkey required to register as Administrator'
            )
            stream = None
            year = None
            division = None
            seat_number = None
        else:
            admin_passkey = ''
            # Student-specific fields
            stream = st.selectbox('📚 Stream', STREAMS, key='reg_stream')
            
            col3, col4 = st.columns(2)
            with col3:
                year = st.selectbox('📅 Year', YEARS, key='reg_year')
            with col4:
                division = st.selectbox('🏛️ Division', DIVISIONS, key='reg_div')
            
            seat_number = st.text_input('💺 Seat Number', placeholder='e.g., 101', key='reg_seat')
        
        profile_pic = st.file_uploader(
            '📷 Profile Photo (Optional)',
            type=['png', 'jpg', 'jpeg', 'gif'],
            key='reg_pic'
        )
        
        submitted = st.form_submit_button('Create Account', use_container_width=True, type='primary')
        
        if submitted:
            # Validation
            if not email or not password or not confirm_password:
                st.error('⚠️ Please fill in all required fields.')
                return
            
            if password != confirm_password:
                st.error('❌ Passwords do not match.')
                return
            
            if len(password) < 6:
                st.error('⚠️ Password must be at least 6 characters.')
                return
            
            if role == 'Admin' and admin_passkey != ADMIN_PASSKEY:
                st.error('🚫 Invalid Admin Passkey. You cannot register as Admin without the correct passkey.')
                return
            
            # Save profile pic if uploaded
            pic_path = None
            if profile_pic:
                if validate_file_type(profile_pic, 'profile'):
                    pic_path = save_uploaded_file(profile_pic, 'profile')
                else:
                    st.error('⚠️ Invalid profile picture format.')
                    return
            
            # Create user
            session = get_session()
            try:
                # Check if email already exists
                existing = session.query(User).filter_by(email=email.strip().lower()).first()
                if existing:
                    st.error('⚠️ An account with this email already exists.')
                    return
                
                new_user = User(
                    email=email.strip().lower(),
                    password_hash=hash_password(password),
                    role=role.lower(),
                    stream=stream if role == 'Student' else None,
                    year=year if role == 'Student' else None,
                    division=division if role == 'Student' else None,
                    seat_number=seat_number if seat_number else None,
                    profile_pic_path=pic_path
                )
                session.add(new_user)
                session.commit()
                st.success('✅ Account created successfully! Please sign in.')
            except Exception as e:
                session.rollback()
                st.error(f'❌ Registration failed: {str(e)}')
            finally:
                session.close()
