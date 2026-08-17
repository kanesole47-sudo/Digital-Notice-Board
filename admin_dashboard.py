# admin_dashboard.py
# Purpose: Admin Frontend Interface — Notice composition, analytics, and management

import streamlit as st
from ui_styles import inject_css, render_navbar, get_priority_badge, get_priority_emoji, STREAMS, YEARS, DIVISIONS
from notice_manager import get_all_notices, search_notices, create_notice, delete_notice, toggle_bookmark, is_bookmarked, get_bookmarked_notices
from file_handler import save_uploaded_file, render_download_button, validate_file_type
from analytics_receipts import render_analytics_panel
from student_dashboard import _render_notice_card


@st.dialog("➕ Compose New Notice", width="large")
def show_compose_dialog(user_id):
    st.markdown("<p style='color: #5F6368; font-size: 0.9rem;'>Fill in the details below to publish a new notice to students.</p>", unsafe_allow_html=True)
    
    with st.form('compose_notice_form_main', clear_on_submit=True):
        title = st.text_input('📌 Notice Title', placeholder='Enter notice title')
        description = st.text_area('📝 Description', placeholder='Write the notice content...', height=150)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            priority = st.selectbox('🚦 Priority Level', [
                ('🔴 Urgent (Red)', 'red'),
                ('🟡 Moderate (Yellow)', 'yellow'),
                ('🟢 General (Green)', 'green')
            ], format_func=lambda x: x[0])
        with col_p2:
            target_stream = st.selectbox('📚 Target Stream', ['All'] + STREAMS, key='compose_stream_main')
        
        col_p3, col_p4 = st.columns(2)
        with col_p3:
            target_year = st.selectbox('📅 Target Year', ['All'] + YEARS, key='compose_year_main')
        with col_p4:
            target_division = st.selectbox('🏛️ Target Division', ['All'] + DIVISIONS, key='compose_div_main')
        
        attachment = st.file_uploader(
            '📎 Attach File (PDF, Word, Image)',
            type=['pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg'],
            key='compose_attachment_main'
        )
        
        submitted = st.form_submit_button('📤 Publish Notice', use_container_width=True, type='primary')
        
        if submitted:
            if not title or not description:
                st.error('⚠️ Title and Description are required.')
            else:
                attachment_path = None
                if attachment:
                    if validate_file_type(attachment):
                        attachment_path = save_uploaded_file(attachment, 'attachment')
                    else:
                        st.error('⚠️ Invalid file type.')
                        return
                
                notice_id = create_notice(
                    title=title,
                    description=description,
                    priority=priority[1],
                    target_stream=target_stream,
                    target_year=target_year,
                    target_division=target_division,
                    attachment_path=attachment_path,
                    creator_id=user_id
                )
                
                if notice_id:
                    st.success(f'✅ Notice published successfully! (ID: {notice_id})')
                    import time
                    time.sleep(1) # wait briefly before closing
                    st.rerun()
                else:
                    st.error('❌ Failed to publish notice.')

def render_admin_dashboard():
    """Main entry point for the admin dashboard"""
    # Inject CSS
    inject_css()
    
    # Get user info
    user_id = st.session_state.get('user_id')
    user_email = st.session_state.get('user_email', 'Admin')
    user_pic = st.session_state.get('user_pic')
    
    # Render navbar
    render_navbar(user_email, user_pic)
    
    # Admin sidebar with compose and profile
    _render_admin_sidebar(user_id)
    
    # Search bar
    search_query = st.text_input(
        '🔍 Search all notices...',
        placeholder='Search by title or description',
        key='admin_search',
        label_visibility='collapsed'
    )
    
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    
    # Tabs: All Notices | Analytics | Saved | Profile
    tab_all, tab_analytics, tab_saved, tab_profile = st.tabs(['📋 All Notices', '📊 Read Analytics', '🔖 Saved Notices', '👤 My Profile'])

    with tab_all:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Send New Notice", use_container_width=True, type="primary"):
                show_compose_dialog(user_id)
                
        st.markdown("<hr style='border: none; border-top: 1px solid #F0F0F0; margin: 16px 0;'>", unsafe_allow_html=True)
        
        if search_query:
            notices = search_notices(search_query)
            if notices:
                st.markdown(f"<p style='color: #5F6368; font-size: 0.85rem;'>🔍 Found {len(notices)} result(s) for '<strong>{search_query}</strong>'</p>", unsafe_allow_html=True)
            else:
                st.info(f'No notices found for "{search_query}".')
        else:
            notices = get_all_notices()
        
        if not notices:
            st.markdown("""
            <div style='text-align: center; padding: 60px 20px; color: #5F6368;'>
                <p style='font-size: 3rem; margin-bottom: 16px;'>📭</p>
                <p style='font-size: 1.1rem;'>No notices posted yet.</p>
                <p style='font-size: 0.9rem;'>Click the ➕ Send New Notice button above to create one.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for notice in notices:
                _render_admin_notice_card(notice, user_id)
    
    with tab_analytics:
        st.markdown("### 📊 Read Receipt Analytics")
        st.markdown("<p style='color: #5F6368; font-size: 0.9rem;'>Track how many students from the target audience have viewed each notice.</p>", unsafe_allow_html=True)
        
        all_notices = get_all_notices()
        if not all_notices:
            st.info('No notices to show analytics for.')
        else:
            for notice in all_notices:
                emoji = get_priority_emoji(notice['priority'])
                badge = get_priority_badge(notice['priority'])
                target = f"{notice['target_stream']} • {notice['target_year']} • {notice['target_division']}"
                
                with st.expander(f"{emoji} {notice['title']} — 🎯 {target}"):
                    render_analytics_panel(notice['id'])
    
    with tab_saved:
        saved = get_bookmarked_notices(user_id)
        if not saved:
            st.markdown("""
            <div style='text-align: center; padding: 60px 20px; color: #5F6368;'>
                <p style='font-size: 3rem; margin-bottom: 16px;'>🔖</p>
                <p style='font-size: 1.1rem;'>No saved notices.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for notice in saved:
                _render_notice_card(notice, user_id, show_analytics=True)

    with tab_profile:
        st.markdown("### 👤 Admin Profile Details")
        st.markdown("<p style='color: #5F6368; font-size: 0.9rem;'>Your administrative account details.</p>", unsafe_allow_html=True)
        
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
                    st.markdown(f'<img src="data:image/{ext};base64,{b64}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 3px solid #34A853; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
                except:
                    st.markdown("<div style='width: 150px; height: 150px; border-radius: 50%; background: #E0E0E0; display: flex; align-items: center; justify-content: center; font-size: 60px;'>👤</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='width: 150px; height: 150px; border-radius: 50%; background: #E0E0E0; display: flex; align-items: center; justify-content: center; font-size: 60px;'>👤</div>", unsafe_allow_html=True)
                
        with col2:
            st.markdown(f"**📧 Email Address:** {user_email}")
            st.markdown(f"**🔑 Account Type:** Admin")
            st.markdown(f"**⚙️ Privileges:** Can create and delete notices, view read analytics.")
            
        st.markdown("<hr style='border: none; border-top: 1px solid #F0F0F0; margin: 24px 0;'>", unsafe_allow_html=True)


def _render_admin_notice_card(notice, admin_id):
    """Renders a notice card with admin controls (delete, analytics)"""
    notice_id = notice['id']
    priority = notice['priority']
    badge_html = get_priority_badge(priority)
    emoji = get_priority_emoji(priority)
    time_str = notice['created_at'].strftime('%d %b %Y, %I:%M %p') if notice['created_at'] else ''
    target = f"{notice['target_stream']} • {notice['target_year']} • {notice['target_division']}"
    
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
            bookmarked = is_bookmarked(admin_id, notice_id)
            bookmark_label = '✅ Saved' if bookmarked else '🔖 Save'
            
            if st.button(bookmark_label, key=f'admin_bm_{notice_id}', use_container_width=True):
                toggle_bookmark(admin_id, notice_id)
                st.rerun()
                
            if notice.get('attachment_path'):
                render_download_button(notice['attachment_path'], key_suffix=f'admin_{notice_id}', compact=True)
                
            if notice['creator_id'] == admin_id:
                if st.button('🗑️ Delete', key=f'del_{notice_id}', type='primary', use_container_width=True):
                    if delete_notice(notice_id, admin_id):
                        st.success('Notice deleted.')
                        st.rerun()
                    else:
                        st.error('Failed to delete notice.')
        
        # Inline analytics
        with st.expander(f'👁️ View Read Receipts', expanded=False):
            render_analytics_panel(notice_id)


def _render_admin_sidebar(admin_id):
    """Renders admin sidebar with compose form and profile"""
    with st.sidebar:
        # Profile section
        st.markdown("### 👤 Admin Profile")
        user_pic = st.session_state.get('user_pic')
        if user_pic:
            try:
                st.image(user_pic, width=100)
            except Exception:
                st.markdown("<div style='font-size: 3rem; text-align: center;'>👤</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 3rem; text-align: center;'>👤</div>", unsafe_allow_html=True)
        
        st.markdown(f"**📧** {st.session_state.get('user_email', 'N/A')}")
        st.markdown(f"**🔑 Role:** Admin")
        
        st.markdown('---')
        
        if st.button('🚪 Logout', use_container_width=True, type='secondary'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
