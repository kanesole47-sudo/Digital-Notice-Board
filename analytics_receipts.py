# analytics_receipts.py
# Purpose: Admin-only read receipt tracking and analytics

import streamlit as st
from sqlalchemy import func, or_
from database_schema import get_session, ReadReceipt, Notice, User
from datetime import datetime


def record_read(user_id, notice_id):
    """
    Record that a user has read a notice.
    Only inserts if not already recorded (idempotent).
    """
    session = get_session()
    try:
        existing = session.query(ReadReceipt).filter_by(
            user_id=user_id, notice_id=notice_id
        ).first()
        
        if not existing:
            receipt = ReadReceipt(
                user_id=user_id,
                notice_id=notice_id,
                read_at=datetime.utcnow()
            )
            session.add(receipt)
            session.commit()
    finally:
        session.close()


def get_notice_analytics(notice_id):
    """
    Calculate read analytics for a specific notice.
    Returns dict with: total_target, read_count, percentage, readers_list
    """
    session = get_session()
    try:
        # Get the notice details
        notice = session.query(Notice).filter_by(id=notice_id).first()
        if not notice:
            return {'total_target': 0, 'read_count': 0, 'percentage': 0, 'readers': []}
        
        # Count target audience (students matching the notice target)
        target_query = session.query(User).filter(User.role == 'student')
        
        if notice.target_stream != 'All':
            target_query = target_query.filter(User.stream == notice.target_stream)
        if notice.target_year != 'All':
            target_query = target_query.filter(User.year == notice.target_year)
        if notice.target_division != 'All':
            target_query = target_query.filter(User.division == notice.target_division)
        
        total_target = target_query.count()
        target_users = target_query.all()
        target_user_ids = [u.id for u in target_users]
        
        # Get read receipts for this notice from target users
        read_receipts = session.query(ReadReceipt).filter(
            ReadReceipt.notice_id == notice_id,
            ReadReceipt.user_id.in_(target_user_ids) if target_user_ids else ReadReceipt.user_id == -1
        ).all()
        
        read_user_ids = {r.user_id for r in read_receipts}
        read_count = len(read_user_ids)
        
        percentage = round((read_count / total_target * 100), 1) if total_target > 0 else 0
        
        # Build readers list with details
        readers = []
        for user in target_users:
            receipt = next((r for r in read_receipts if r.user_id == user.id), None)
            readers.append({
                'user_id': user.id,
                'email': user.email,
                'seat_number': user.seat_number,
                'stream': user.stream,
                'year': user.year,
                'division': user.division,
                'has_read': user.id in read_user_ids,
                'read_at': receipt.read_at if receipt else None
            })
        
        return {
            'total_target': total_target,
            'read_count': read_count,
            'percentage': percentage,
            'readers': readers
        }
    finally:
        session.close()


def render_analytics_panel(notice_id):
    """
    Renders the analytics UI panel for a specific notice.
    Shows percentage bar, blue/grey ticks, and reader details.
    """
    analytics = get_notice_analytics(notice_id)
    
    total = analytics['total_target']
    read = analytics['read_count']
    pct = analytics['percentage']
    
    # Header stats
    st.markdown(f"""  
    <div style='margin: 12px 0;'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
            <span style='font-size: 0.9rem; color: #5F6368;'>📊 Read by <strong>{read}</strong> of <strong>{total}</strong> students</span>
            <span style='font-size: 0.9rem; font-weight: 600; color: #202124;'>{pct}%</span>
        </div>
        <div class='analytics-bar-bg'>
            <div class='analytics-bar-fill' style='width: {pct}%;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reader details in expander
    if analytics['readers']:
        with st.expander(f'👁️ View Reader Details ({read}/{total})'):
            for reader in analytics['readers']:
                if reader['has_read']:
                    tick = '<span class="blue-tick">✓✓</span>'
                    time_str = reader['read_at'].strftime('%d %b %Y, %I:%M %p') if reader['read_at'] else ''
                    st.markdown(
                        f"{tick} <strong>{reader['email']}</strong> "
                        f"<span style='color: #5F6368; font-size: 0.8rem;'>"
                        f"(Seat: {reader['seat_number'] or 'N/A'}) — Read at {time_str}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    tick = '<span class="grey-tick">✓</span>'
                    st.markdown(
                        f"{tick} <strong>{reader['email']}</strong> "
                        f"<span style='color: #9E9E9E; font-size: 0.8rem;'>"
                        f"(Seat: {reader['seat_number'] or 'N/A'}) — Not yet viewed</span>",
                        unsafe_allow_html=True
                    )
