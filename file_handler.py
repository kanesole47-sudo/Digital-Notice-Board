# file_handler.py
# Purpose: Dedicated File I/O Module for uploads and downloads

import os
import streamlit as st
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR_PROFILES = os.path.join(BASE_DIR, 'uploads', 'profile_pics')
UPLOAD_DIR_ATTACHMENTS = os.path.join(BASE_DIR, 'uploads', 'notice_attachments')

ALLOWED_ATTACHMENT_TYPES = ['pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'gif']
ALLOWED_PROFILE_TYPES = ['png', 'jpg', 'jpeg', 'gif']

def ensure_upload_dirs():
    """Create upload directories if they don't exist"""
    os.makedirs(UPLOAD_DIR_PROFILES, exist_ok=True)
    os.makedirs(UPLOAD_DIR_ATTACHMENTS, exist_ok=True)

def save_uploaded_file(uploaded_file, category='attachment'):
    """
    Save an uploaded file to the appropriate directory.
    category: 'attachment' or 'profile'
    Returns the saved file path or None on failure.
    """
    ensure_upload_dirs()
    if uploaded_file is None:
        return None
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = uploaded_file.name.split('.')[-1].lower()
    
    if category == 'profile':
        if ext not in ALLOWED_PROFILE_TYPES:
            st.error(f'Invalid file type: .{ext}. Allowed: {ALLOWED_PROFILE_TYPES}')
            return None
        save_dir = UPLOAD_DIR_PROFILES
    else:
        if ext not in ALLOWED_ATTACHMENT_TYPES:
            st.error(f'Invalid file type: .{ext}. Allowed: {ALLOWED_ATTACHMENT_TYPES}')
            return None
        save_dir = UPLOAD_DIR_ATTACHMENTS
    
    filename = f'{timestamp}_{uploaded_file.name}'
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath

def get_file_icon(filename):
    """Returns appropriate emoji icon based on file extension"""
    if filename is None:
        return ''
    ext = filename.split('.')[-1].lower()
    icons = {
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️', 'gif': '🖼️',
    }
    return icons.get(ext, '📎')

def render_download_button(file_path, key_suffix='', compact=False):
    """Renders a Streamlit download button for the given file path"""
    if file_path and os.path.exists(file_path):
        filename = os.path.basename(file_path)
        icon = get_file_icon(filename)
        ext = filename.split('.')[-1].upper()
        label = f'{icon} {ext}' if compact else f'{icon} ⬇️ {filename}'
        with open(file_path, 'rb') as f:
            file_data = f.read()
        st.download_button(
            label=label,
            data=file_data,
            file_name=filename,
            key=f'download_{filename}_{key_suffix}'
        )
        return True
    return False

def validate_file_type(uploaded_file, category='attachment'):
    """Validates if the uploaded file has an allowed extension"""
    if uploaded_file is None:
        return True
    ext = uploaded_file.name.split('.')[-1].lower()
    allowed = ALLOWED_PROFILE_TYPES if category == 'profile' else ALLOWED_ATTACHMENT_TYPES
    return ext in allowed
