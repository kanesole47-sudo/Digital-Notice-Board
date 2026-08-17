# notice_manager.py
# Purpose: Core notice filtering, search, and bookmark management

from sqlalchemy import or_, and_, func
from database_schema import get_session, Notice, SavedNotice, User


def get_filtered_notices(user_stream, user_year, user_division):
    """
    Returns notices that match the user's profile.
    A notice matches if its target matches the user's value OR is 'All'.
    Results ordered by created_at descending (newest first).
    """
    session = get_session()
    try:
        notices = session.query(Notice).filter(
            or_(Notice.target_stream == user_stream, Notice.target_stream == 'All'),
            or_(Notice.target_year == user_year, Notice.target_year == 'All'),
            or_(Notice.target_division == user_division, Notice.target_division == 'All')
        ).order_by(Notice.created_at.desc()).all()
        
        # Detach from session by converting to dicts
        result = []
        for n in notices:
            result.append({
                'id': n.id,
                'title': n.title,
                'description': n.description,
                'priority': n.priority,
                'target_stream': n.target_stream,
                'target_year': n.target_year,
                'target_division': n.target_division,
                'attachment_path': n.attachment_path,
                'creator_id': n.creator_id,
                'created_at': n.created_at,
                'creator_email': n.creator.email if n.creator else 'Unknown'
            })
        return result
    finally:
        session.close()


def get_all_notices():
    """Returns all notices (for admin view), newest first."""
    session = get_session()
    try:
        notices = session.query(Notice).order_by(Notice.created_at.desc()).all()
        result = []
        for n in notices:
            result.append({
                'id': n.id,
                'title': n.title,
                'description': n.description,
                'priority': n.priority,
                'target_stream': n.target_stream,
                'target_year': n.target_year,
                'target_division': n.target_division,
                'attachment_path': n.attachment_path,
                'creator_id': n.creator_id,
                'created_at': n.created_at,
                'creator_email': n.creator.email if n.creator else 'Unknown'
            })
        return result
    finally:
        session.close()


def search_notices(query, user_stream=None, user_year=None, user_division=None):
    """
    Search notices by title or description containing the query string.
    If user profile is provided, results are filtered to matching notices.
    """
    session = get_session()
    try:
        search_filter = or_(
            Notice.title.ilike(f'%{query}%'),
            Notice.description.ilike(f'%{query}%')
        )
        
        if user_stream and user_year and user_division:
            profile_filter = and_(
                or_(Notice.target_stream == user_stream, Notice.target_stream == 'All'),
                or_(Notice.target_year == user_year, Notice.target_year == 'All'),
                or_(Notice.target_division == user_division, Notice.target_division == 'All')
            )
            notices = session.query(Notice).filter(search_filter, profile_filter).order_by(Notice.created_at.desc()).all()
        else:
            notices = session.query(Notice).filter(search_filter).order_by(Notice.created_at.desc()).all()
        
        result = []
        for n in notices:
            result.append({
                'id': n.id,
                'title': n.title,
                'description': n.description,
                'priority': n.priority,
                'target_stream': n.target_stream,
                'target_year': n.target_year,
                'target_division': n.target_division,
                'attachment_path': n.attachment_path,
                'creator_id': n.creator_id,
                'created_at': n.created_at,
                'creator_email': n.creator.email if n.creator else 'Unknown'
            })
        return result
    finally:
        session.close()


def toggle_bookmark(user_id, notice_id):
    """
    Toggle bookmark status. If bookmarked, remove it. If not, add it.
    Returns True if now bookmarked, False if removed.
    """
    session = get_session()
    try:
        existing = session.query(SavedNotice).filter_by(
            user_id=user_id, notice_id=notice_id
        ).first()
        
        if existing:
            session.delete(existing)
            session.commit()
            return False
        else:
            saved = SavedNotice(user_id=user_id, notice_id=notice_id)
            session.add(saved)
            session.commit()
            return True
    finally:
        session.close()


def is_bookmarked(user_id, notice_id):
    """Check if a notice is bookmarked by the user."""
    session = get_session()
    try:
        exists = session.query(SavedNotice).filter_by(
            user_id=user_id, notice_id=notice_id
        ).first()
        return exists is not None
    finally:
        session.close()


def get_bookmarked_notices(user_id):
    """Get all notices bookmarked by the user."""
    session = get_session()
    try:
        saved_ids = session.query(SavedNotice.notice_id).filter_by(user_id=user_id).all()
        saved_ids = [s[0] for s in saved_ids]
        
        if not saved_ids:
            return []
        
        notices = session.query(Notice).filter(
            Notice.id.in_(saved_ids)
        ).order_by(Notice.created_at.desc()).all()
        
        result = []
        for n in notices:
            result.append({
                'id': n.id,
                'title': n.title,
                'description': n.description,
                'priority': n.priority,
                'target_stream': n.target_stream,
                'target_year': n.target_year,
                'target_division': n.target_division,
                'attachment_path': n.attachment_path,
                'creator_id': n.creator_id,
                'created_at': n.created_at,
                'creator_email': n.creator.email if n.creator else 'Unknown'
            })
        return result
    finally:
        session.close()


def create_notice(title, description, priority, target_stream, target_year, target_division, attachment_path, creator_id):
    """Create a new notice in the database. Returns the created notice ID."""
    session = get_session()
    try:
        notice = Notice(
            title=title,
            description=description,
            priority=priority,
            target_stream=target_stream,
            target_year=target_year,
            target_division=target_division,
            attachment_path=attachment_path,
            creator_id=creator_id
        )
        session.add(notice)
        session.commit()
        return notice.id
    finally:
        session.close()


def delete_notice(notice_id, admin_id):
    """Delete a notice. Only the creator admin can delete."""
    session = get_session()
    try:
        notice = session.query(Notice).filter_by(id=notice_id, creator_id=admin_id).first()
        if notice:
            # Also delete related saved notices and read receipts
            session.query(SavedNotice).filter_by(notice_id=notice_id).delete()
            from database_schema import ReadReceipt
            session.query(ReadReceipt).filter_by(notice_id=notice_id).delete()
            session.delete(notice)
            session.commit()
            return True
        return False
    finally:
        session.close()
