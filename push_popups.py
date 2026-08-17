# push_popups.py
# Purpose: In-app popup notification manager for urgent notices

import streamlit as st
from database_schema import get_session, Notice, ReadReceipt
from sqlalchemy import or_, and_


def check_new_urgent_notices(user_id, user_stream, user_year, user_division):
    """
    Check for unread RED-priority notices targeting this user.
    Returns list of notice dicts that haven't been read yet.
    """
    session = get_session()
    try:
        # Get IDs of notices already read by this user
        read_ids = session.query(ReadReceipt.notice_id).filter_by(user_id=user_id).all()
        read_ids = [r[0] for r in read_ids]
        
        # Query urgent notices targeting this user that haven't been read
        query = session.query(Notice).filter(
            Notice.priority == 'red',
            or_(Notice.target_stream == user_stream, Notice.target_stream == 'All'),
            or_(Notice.target_year == user_year, Notice.target_year == 'All'),
            or_(Notice.target_division == user_division, Notice.target_division == 'All')
        )
        
        if read_ids:
            query = query.filter(~Notice.id.in_(read_ids))
        
        urgent_notices = query.order_by(Notice.created_at.desc()).all()
        
        result = []
        for n in urgent_notices:
            result.append({
                'id': n.id,
                'title': n.title,
                'description': n.description,
                'priority': n.priority,
                'created_at': n.created_at,
                'creator_email': n.creator.email if n.creator else 'Unknown'
            })
        return result
    finally:
        session.close()


@st.dialog("🚨 Urgent Notice Alert", width="large")
def _show_urgent_dialog(notice):
    """Streamlit dialog popup for an urgent notice with Ignore and Acknowledge buttons."""
    time_str = notice['created_at'].strftime('%d %b %Y, %I:%M %p') if notice['created_at'] else ''
    
    st.markdown(f"""
    <div style='text-align: center; padding: 12px 0 20px 0;'>
        <span style='font-size: 3rem;'>🚨</span>
        <h3 style='color: #DC3545; margin: 8px 0 4px 0; font-size: 1.3rem; font-weight: 700;'>URGENT NOTICE</h3>
        <h2 style='color: #202124; margin: 0 0 12px 0; font-size: 1.6rem; font-weight: 800;'>{notice['title']}</h2>
        <p style='color: #3C4043; font-size: 1rem; line-height: 1.6; max-width: 480px; margin: 0 auto;'>
            {notice['description']}
        </p>
        <p style='color: #9AA0A6; font-size: 0.8rem; margin-top: 16px;'>
            📤 Posted by {notice['creator_email']} &nbsp;•&nbsp; {time_str}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: none; border-top: 1px solid #F0F0F0; margin: 8px 0 16px 0;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Ignore / Not Applicable", use_container_width=True, type="secondary"):
            # Just dismiss — don't mark as read so it may show again later
            st.session_state[f"popup_dismissed_{notice['id']}"] = True
            st.rerun()
    
    with col2:
        if st.button("✅ Yes, I Acknowledge", use_container_width=True, type="primary"):
            # Mark as read in DB so it never shows again
            _mark_as_read(notice['id'], st.session_state.get('user_id'))
            st.session_state[f"popup_dismissed_{notice['id']}"] = True
            st.rerun()


def _mark_as_read(notice_id, user_id):
    """Inserts a ReadReceipt so the notice won't popup again."""
    if not user_id:
        return
    session = get_session()
    try:
        from database_schema import ReadReceipt
        from datetime import datetime
        existing = session.query(ReadReceipt).filter_by(user_id=user_id, notice_id=notice_id).first()
        if not existing:
            receipt = ReadReceipt(user_id=user_id, notice_id=notice_id, read_at=datetime.utcnow())
            session.add(receipt)
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def render_toast_notifications(notices):
    """
    Renders st.toast() notifications for non-critical notices.
    Used for yellow and green priority notices.
    """
    for notice in notices[:3]:  # Limit to 3 toasts to avoid clutter
        priority = notice.get('priority', 'green')
        if priority == 'yellow':
            icon = '🟡'
        else:
            icon = '🟢'
        st.toast(f"{icon} {notice['title']}", icon=icon)


def show_urgent_alerts(user_id, user_stream, user_year, user_division):
    """
    Main entry point: checks for urgent notices and shows popup for the first unread one.
    Call this at the top of the dashboard to trigger alerts.
    """
    urgent = check_new_urgent_notices(user_id, user_stream, user_year, user_division)
    
    if urgent:
        notice = urgent[0]
        popup_key = f"popup_dismissed_{notice['id']}"
        # Only show if not already dismissed in this session
        if not st.session_state.get(popup_key, False):
            _show_urgent_dialog(notice)
