import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto:wght@400;500&display=swap');

    body {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
    }

    .notice-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        padding: 20px;
        margin-bottom: 16px;
        transition: box-shadow 0.2s ease-in-out;
    }
    .notice-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .badge-red {
        background-color: #DC3545;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-yellow {
        background-color: #FFC107;
        color: #202124;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-green {
        background-color: #28A745;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 12px 24px;
        border-bottom: 1px solid #E0E0E0;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .navbar-brand {
        font-size: 1.4rem;
        font-weight: 700;
        color: #202124;
    }
    .profile-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        object-fit: cover;
        border: 2px solid #E0E0E0;
    }

    .fab-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #4285F4;
        color: white;
        font-size: 28px;
        border: none;
        box-shadow: 0 4px 12px rgba(66,133,244,0.4);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
    }
    .fab-button:hover {
        transform: scale(1.1);
    }

    .search-input {
        width: 100%;
        padding: 10px 16px;
        border-radius: 24px;
        border: 1px solid #E0E0E0;
        font-size: 0.95rem;
        outline: none;
        background: #F1F3F4;
    }
    .search-input:focus {
        border-color: #4285F4;
        box-shadow: 0 0 0 2px rgba(66,133,244,0.2);
    }

    .popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 2000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .popup-card {
        background: white;
        border-radius: 16px;
        padding: 32px;
        max-width: 480px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        border-top: 4px solid #DC3545;
    }

    .analytics-bar-bg {
        background: #E0E0E0;
        border-radius: 10px;
        height: 8px;
        width: 100%;
    }
    .analytics-bar-fill {
        height: 8px;
        border-radius: 10px;
        background: linear-gradient(90deg, #4285F4, #34A853);
    }

    .blue-tick {
        color: #4285F4;
        font-weight: bold;
    }
    .grey-tick {
        color: #9E9E9E;
    }

    [data-testid='stToolbar'], footer, #MainMenu {
        visibility: hidden;
    }
    
    .stApp > header {
        display: none;
    }
    
    .block-container {
        max-width: 900px;
    }

    .auth-container {
        max-width: 420px;
        margin: 60px auto;
        background: white;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .auth-title {
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        color: #202124;
        margin-bottom: 8px;
    }
    .auth-subtitle {
        font-size: 0.95rem;
        color: #5F6368;
        text-align: center;
        margin-bottom: 24px;
    }

    .notice-meta {
        font-size: 0.8rem;
        color: #5F6368;
        margin-top: 4px;
    }
    .notice-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #202124;
        margin: 8px 0 4px 0;
    }
    .notice-desc {
        font-size: 0.9rem;
        color: #3C4043;
        line-height: 1.5;
    }

    /* Tab styling for stTabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        color: #5F6368;
    }
    .stTabs [aria-selected="true"] {
        color: #4285F4;
        background-color: transparent;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .auth-container {
            padding: 24px 16px;
        }
        .auth-title {
            font-size: 1.5rem;
        }
        .top-navbar {
            padding: 12px 16px;
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
        .top-navbar .nav-title {
            font-size: 1.2rem;
        }
        .notice-card {
            padding: 16px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_priority_badge(priority):
    """Takes 'red', 'yellow', or 'green', returns HTML span with appropriate badge class."""
    if priority == 'red':
        return '<span class="badge-red">URGENT</span>'
    elif priority == 'yellow':
        return '<span class="badge-yellow">MODERATE</span>'
    elif priority == 'green':
        return '<span class="badge-green">GENERAL</span>'
    return '<span class="badge-green">GENERAL</span>'

def get_priority_emoji(priority):
    """Returns the priority emoji."""
    if priority == 'red':
        return '🔴'
    elif priority == 'yellow':
        return '🟡'
    elif priority == 'green':
        return '🟢'
    return '🟢'

def render_navbar(user_name, profile_pic_path=None):
    """Renders a top navbar using st.markdown."""
    import os
    import base64
    
    b64_img = None
    if profile_pic_path and os.path.exists(profile_pic_path):
        try:
            with open(profile_pic_path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            ext = profile_pic_path.split('.')[-1].lower()
            if ext == 'jpg':
                ext = 'jpeg'
            b64_img = f"data:image/{ext};base64,{b64}"
        except Exception:
            pass

    if b64_img:
        img_tag = f'<img src="{b64_img}" class="profile-icon" title="{user_name}">'
    else:
        img_tag = f'<div class="profile-icon" style="display:flex; align-items:center; justify-content:center; background:#E0E0E0; font-size:20px;" title="{user_name}">👤</div>'
        
    html = f"""
    <div class="top-navbar">
        <div class="navbar-brand">🏫 College Notice Board</div>
        <div style="display:flex; align-items:center; gap: 12px;">
            <span style="font-weight: 500; color: #202124;">{user_name}</span>
            {img_tag}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

STREAMS = ['BSc CS', 'BSc IT', 'Commerce', 'Arts']
YEARS = ['FY', 'SY', 'TY']
DIVISIONS = ['Div A', 'Div B']
ADMIN_PASSKEY = 'COLLEGE_ADMIN_2024'
