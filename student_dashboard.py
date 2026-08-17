# student_dashboard.py
# Purpose: Student Frontend Interface — Personalized notice feed, search, bookmarks

import streamlit as st
from ui_styles import inject_css, render_navbar, get_priority_badge, get_priority_emoji
from notice_manager import get_filtered_notices, search_notices, toggle_bookmark, is_bookmarked, get_bookmarked_notices
from file_handler import render_download_button
from analytics_receipts import record_read
from push_popups import show_urgent_alerts


def render_student_dashboard():
    """Main entry point for the student dashboard"""
    # Inject CSS
    inject_css()
    
    # Get user info from session
    user_id = st.session_state.get('user_id')
    user_email = st.session_state.get('user_email', 'Student')
    user_stream = st.session_state.get('user_stream', '')
    user_year = st.session_state.get('user_year', '')
    user_division = st.session_state.get('user_division', '')
    user_pic = st.session_state.get('user_pic')
    
    # Render navbar
    render_navbar(user_email, user_pic)
    
    # Check for urgent alerts
    show_urgent_alerts(user_id, user_stream, user_year, user_division)
    
    # Profile sidebar
    _render_profile_sidebar()
    
    # Search bar
    search_query = st.text_input(
        '🔍 Search notices...',
        placeholder='Search by title or description',
        key='student_search',
        label_visibility='collapsed'
    )
    
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    
    # Tabs: All Notices | Saved | Profile
    tab_all, tab_saved, tab_profile = st.tabs(['📋 All Notices', '🔖 Saved Notices', '👤 My Profile'])
    
    with tab_all:
        if search_query:
            notices = search_notices(search_query, user_stream, user_year, user_division)
            if notices:
                st.markdown(f"<p style='color: #5F6368; font-size: 0.85rem;'>🔍 Found {len(notices)} result(s) for '<strong>{search_query}</strong>'</p>", unsafe_allow_html=True)
            else:
                st.info(f'No notices found for "{search_query}".')
        else:
            notices = get_filtered_notices(user_stream, user_year, user_division)
        
        if not notices:
            st.markdown("""
            <div style='text-align: center; padding: 60px 20px; color: #5F6368;'>
                <p style='font-size: 3rem; margin-bottom: 16px;'>📭</p>
                <p style='font-size: 1.1rem;'>No notices for you right now.</p>
                <p style='font-size: 0.9rem;'>Check back later!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for notice in notices:
                _render_notice_card(notice, user_id, show_analytics=False, key_prefix='all')
    
    with tab_saved:
        saved = get_bookmarked_notices(user_id)
        if not saved:
            st.markdown("""
            <div style='text-align: center; padding: 60px 20px; color: #5F6368;'>
                <p style='font-size: 3rem; margin-bottom: 16px;'>🔖</p>
                <p style='font-size: 1.1rem;'>No saved notices yet.</p>
                <p style='font-size: 0.9rem;'>Bookmark important notices to find them here.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for notice in saved:
                _render_notice_card(notice, user_id, show_analytics=False, key_prefix='saved')

    with tab_profile:
        st.markdown("### 👤 Student Profile Details")
        st.markdown("<p style='color: #5F6368; font-size: 0.9rem;'>Here is the information you provided during registration.</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if user_pic:
                import base64
                import os
                try:
                    with open(user_pic, "rb") as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode()
                    ext = user_pic.split('.')[-1].lower()
                    if ext == 'jpg': ext = 'jpeg'
                    st.markdown(f'<img src="data:image/{ext};base64,{b64}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 3px solid #4285F4; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
                except:
                    st.markdown("<div style='width: 150px; height: 150px; border-radius: 50%; background: #E0E0E0; display: flex; align-items: center; justify-content: center; font-size: 60px;'>👤</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='width: 150px; height: 150px; border-radius: 50%; background: #E0E0E0; display: flex; align-items: center; justify-content: center; font-size: 60px;'>👤</div>", unsafe_allow_html=True)
                
        with col2:
            st.markdown(f"**📧 Email Address:** {user_email}")
            st.markdown(f"**🔑 Account Type:** Student")
            st.markdown(f"**📚 Enrolled Stream:** {user_stream}")
            st.markdown(f"**📅 Academic Year:** {user_year}")
            st.markdown(f"**🏛️ Division:** {user_division}")
            st.markdown(f"**💺 Seat Number:** {st.session_state.get('user_seat') or 'Not provided'}")
            
        st.markdown("<hr style='border: none; border-top: 1px solid #F0F0F0; margin: 24px 0;'>", unsafe_allow_html=True)
        st.info("💡 To update your profile details or password, please contact the College Admin.")


def _render_notice_card(notice, user_id, show_analytics=False, key_prefix='card'):
    """Renders a single notice card with badge, content, bookmark, and download"""
    notice_id = notice['id']
    priority = notice['priority']
    
    # Record read receipt
    record_read(user_id, notice_id)
    
    # Badge and emoji
    badge_html = get_priority_badge(priority)
    emoji = get_priority_emoji(priority)
    
    # Timestamp formatting
    created = notice['created_at']
    time_str = created.strftime('%d %b %Y, %I:%M %p') if created else ''
    
    # Target info
    target = f"{notice['target_stream']} • {notice['target_year']} • {notice['target_division']}"
    
    # Render native Streamlit card container
    with st.container(border=True):
        col_content, col_actions = st.columns([5, 1])
        
        with col_content:
            st.markdown(f"""
            <div style='display:flex; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;'>
                {badge_html}
                <span style='font-size:0.8rem; color:#5F6368;'>🎯 {target}</span>
            </div>
            <p style='font-size:1.3rem; font-weight:700; color:#202124; margin:0 0 8px 0;'>{emoji} {notice['title']}</p>
            <p style='color:#3C4043; line-height:1.5; margin:0 0 12px 0;'>{notice['description']}</p>
            <p style='font-size:0.8rem; color:#5F6368; margin:0;'>📤 Posted by {notice['creator_email']} • {time_str}</p>
            """, unsafe_allow_html=True)
            
        with col_actions:
            bookmarked = is_bookmarked(user_id, notice_id)
            bookmark_label = '✅ Saved' if bookmarked else '🔖 Save'
            
            if st.button(bookmark_label, key=f'{key_prefix}_bm_{notice_id}', use_container_width=True):
                toggle_bookmark(user_id, notice_id)
                st.rerun()
                
            if notice.get('attachment_path'):
                render_download_button(notice['attachment_path'], key_suffix=f'{key_prefix}_{notice_id}', compact=True)
        
        # Analytics panel (admin only)
        if show_analytics:
            from analytics_receipts import render_analytics_panel
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            render_analytics_panel(notice_id)


def _render_profile_sidebar():
    """Renders profile information in the sidebar"""
    with st.sidebar:
        st.markdown("### 👤 My Profile")
        
        # Profile picture
        user_pic = st.session_state.get('user_pic')
        if user_pic:
            try:
                st.image(user_pic, width=100)
            except Exception:
                st.markdown("<div style='font-size: 3rem; text-align: center;'>👤</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 3rem; text-align: center;'>👤</div>", unsafe_allow_html=True)
        
        st.markdown(f"**📧 Email:** {st.session_state.get('user_email', 'N/A')}")
        st.markdown(f"**📚 Stream:** {st.session_state.get('user_stream', 'N/A')}")
        st.markdown(f"**📅 Year:** {st.session_state.get('user_year', 'N/A')}")
        st.markdown(f"**🏛️ Division:** {st.session_state.get('user_division', 'N/A')}")
        st.markdown(f"**💺 Seat No:** {st.session_state.get('user_seat', 'N/A')}")
        
        st.markdown('---')
        
        if st.button('🚪 Logout', use_container_width=True, type='secondary'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
