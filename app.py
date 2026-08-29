import streamlit as st
import base64
import os
import re
import sys


# ============================================================
# PROJECT PATH
# ============================================================

# frontend/app.py
# We need the main project folder so that Python can find backend/

FRONTEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    FRONTEND_DIR
)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.rag_chat import ask_history_bot

from backend.database import (
    create_tables,
    get_or_create_user,
    create_chat,
    save_message,
    get_all_chats,
    get_messages,
    delete_chat
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Bharat Darshan",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

create_tables()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None


# ============================================================
# FILE PATHS
# ============================================================

BACKGROUND_IMAGE = os.path.join(
    FRONTEND_DIR,
    "temple_background.jpg"
)

USER_AVATAR = os.path.join(
    FRONTEND_DIR,
    "user_avatar.png"
)

BOT_AVATAR = os.path.join(
    FRONTEND_DIR,
    "bot_avatar.png"
)


# ============================================================
# BACKGROUND IMAGE
# ============================================================

def get_base64_image(image_path):

    if not os.path.exists(image_path):
        return ""

    with open(image_path, "rb") as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode()


background_image = get_base64_image(
    BACKGROUND_IMAGE
)


# ============================================================
# EMAIL VALIDATION
# ============================================================

def valid_email(email):

    pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    return re.match(
        pattern,
        email
    ) is not None


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    # ========================================================
    # LOGIN PAGE CSS
    # ========================================================

    st.markdown(
        f"""
        <style>

        html,
        body {{
            margin: 0 !important;
            padding: 0 !important;
        }}

        .stApp {{

            min-height: 100vh !important;

            background-image:
                url(
                    "data:image/jpeg;base64,{background_image}"
                ) !important;

            background-size: cover !important;

            background-position: center !important;

            background-repeat: no-repeat !important;

            background-attachment: fixed !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background: transparent !important;
        }}

        [data-testid="stMain"] {{
            background: transparent !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
        }}

        .block-container {{
            background: transparent !important;

            padding-top: 0 !important;

            padding-bottom: 40px !important;
        }}


        /* ====================================================
           LOGIN TITLE
           ==================================================== */

        .login-title {{

            text-align: center !important;

            font-family:
                Georgia, serif !important;

            font-size:
                58px !important;

            font-weight:
                700 !important;

            color:
                #5A3218 !important;

            margin-top:
                13vh !important;

            margin-bottom:
                8px !important;

            line-height:
                1.2 !important;

            background:
                transparent !important;

            border:
                none !important;

            box-shadow:
                none !important;
        }}


        /* ====================================================
           LOGIN LINE
           ==================================================== */

        .login-line {{

            width:
                330px !important;

            height:
                2px !important;

            background-color:
                #5A3218 !important;

            margin:
                0 auto 16px auto !important;

            padding:
                0 !important;

            border:
                none !important;

            box-shadow:
                none !important;
        }}


        /* ====================================================
           LOGIN SUBTITLE
           ==================================================== */

        .login-subtitle {{

            text-align:
                center !important;

            font-family:
                Arial, sans-serif !important;

            font-size:
                17px !important;

            color:
                #5A3218 !important;

            margin:
                0 0 25px 0 !important;

            padding:
                0 !important;

            background:
                transparent !important;

            border:
                none !important;

            box-shadow:
                none !important;
        }}


        /* ====================================================
           EMAIL INPUT
           ==================================================== */

        [data-testid="stTextInput"] {{

            max-width:
                430px !important;

            margin:
                30px auto 0 auto !important;
        }}

        [data-testid="stTextInput"] label {{

            color:
                #6b3f20 !important;

            font-family:
                Arial, sans-serif !important;

            font-weight:
                600 !important;
        }}

        [data-testid="stTextInput"] input {{

            background:
                rgba(
                    255,
                    248,
                    235,
                    0.80
                ) !important;

            background-color:
                rgba(
                    255,
                    248,
                    235,
                    0.80
                ) !important;

            color:
                #3b2415 !important;

            border:
                1px solid
                #8a6647 !important;

            border-radius:
                8px !important;

            box-shadow:
                none !important;
        }}

        [data-testid="stTextInput"] input:focus {{

            border-color:
                #6b3f20 !important;

            box-shadow:
                0 0 0 1px
                #6b3f20 !important;
        }}

        [data-testid="stTextInput"]
        input::placeholder {{

            color:
                #765a42 !important;
        }}


        /* ====================================================
           CONTINUE BUTTON
           ==================================================== */

        [data-testid="stButton"] > button {{

            background-color:
                #8a6647 !important;

            color:
                #ffffff !important;

            border:
                1px solid
                #8a6647 !important;

            border-radius:
                8px !important;

            box-shadow:
                none !important;
        }}

        [data-testid="stButton"] > button:hover {{

            background-color:
                #6b3f20 !important;

            border-color:
                #6b3f20 !important;

            color:
                #ffffff !important;
        }}


        /* ====================================================
           ERROR
           ==================================================== */

        [data-testid="stAlert"] {{

            max-width:
                430px !important;

            margin-left:
                auto !important;

            margin-right:
                auto !important;
        }}


        footer {{
            visibility:
                hidden !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN TITLE
    # ========================================================

    st.markdown(
        """
        <div class="login-title">
            Bharat Darshan
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # BROWN LINE
    # ========================================================

    st.markdown(
        """
        <div class="login-line"></div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SUBTITLE
    # ========================================================

    st.markdown(
        """
        <div class="login-subtitle">
            Explore the history of Ancient India
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # EMAIL INPUT
    # ========================================================

    email = st.text_input(
        "Email address",
        placeholder="Enter your email",
        key="login_email"
    )


    # ========================================================
    # CONTINUE BUTTON
    # ========================================================

    login_clicked = st.button(
        "Continue",
        use_container_width=True
    )


    # ========================================================
    # LOGIN PROCESS
    # ========================================================

    if login_clicked:

        clean_email = email.strip().lower()


        if not clean_email:

            st.error(
                "Please enter your email address."
            )


        elif not valid_email(clean_email):

            st.error(
                "Please enter a valid email address."
            )


        else:

            user_id = get_or_create_user(
                clean_email
            )

            st.session_state.logged_in = True

            st.session_state.user_email = (
                clean_email
            )

            st.session_state.user_id = (
                user_id
            )

            st.session_state.current_chat_id = (
                None
            )

            st.rerun()


    # ========================================================
    # STOP UNTIL LOGIN
    # ========================================================

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

user_id = st.session_state.user_id

user_email = st.session_state.user_email


# ============================================================
# CURRENT CHAT MESSAGES
# ============================================================

saved_messages = []


if st.session_state.current_chat_id is not None:

    saved_messages = get_messages(
        st.session_state.current_chat_id,
        user_id
    )


is_empty_chat = (
    len(saved_messages) == 0
)


# ============================================================
# MAIN APP CSS
# ============================================================

st.markdown(
    f"""
    <style>

    html,
    body {{
        margin: 0 !important;
        padding: 0 !important;
    }}


    /* ========================================================
       MAIN BACKGROUND
       ======================================================== */

    .stApp {{

        min-height:
            100vh !important;

        background-image:
            url(
                "data:image/jpeg;base64,{background_image}"
            ) !important;

        background-size:
            cover !important;

        background-position:
            center !important;

        background-repeat:
            no-repeat !important;

        background-attachment:
            fixed !important;
    }}

    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
    }}

    [data-testid="stMain"] {{
        background: transparent !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        background: transparent !important;
    }}

    .block-container {{

        background:
            transparent !important;

        max-width:
            1100px !important;

        padding-top:
            0.5rem !important;

        padding-bottom:
            5rem !important;
    }}


    /* ========================================================
       HEADER
       ======================================================== */

    [data-testid="stHeader"] {{

        background:
            transparent !important;

        box-shadow:
            none !important;
    }}


    /* ========================================================
       BOTTOM CHAT AREA
       ======================================================== */

    [data-testid="stBottom"] {{

        background:
            transparent !important;

        background-color:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}

    [data-testid="stBottom"] > div {{

        background:
            transparent !important;

        background-color:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}

    [data-testid="stBottomBlockContainer"] {{

        background:
            transparent !important;

        background-color:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {{

        background-color:
            #24140b !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}

    [data-testid="stSidebarContent"] {{

        background-color:
            #24140b !important;

        padding-top:
            0 !important;

        padding-left:
            10px !important;

        padding-right:
            10px !important;

        padding-bottom:
            10px !important;
    }}


    /* ========================================================
       SIDEBAR TITLE
       ======================================================== */

    .sidebar-title {{

        width:
            100% !important;

        text-align:
            center !important;

        font-family:
            Georgia, serif !important;

        font-size:
            25px !important;

        font-weight:
            700 !important;

        color:
            #f1c77e !important;

        background:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;

        padding:
            0 !important;

        margin-top:
            -18px !important;

        margin-bottom:
            30px !important;
    }}


    /* ========================================================
       NEW CHAT
       ======================================================== */

    [data-testid="stSidebar"]
    [data-testid="stButton"] > button {{

        box-shadow:
            none !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stButton"]:first-of-type
    > button {{

        width:
            100% !important;

        height:
            40px !important;

        min-height:
            40px !important;

        box-sizing:
            border-box !important;

        background-color:
            #8a6647 !important;

        color:
            #f7eee4 !important;

        border:
            1px solid
            #8a6647 !important;

        border-radius:
            8px !important;

        outline:
            none !important;

        box-shadow:
            none !important;

        font-family:
            Arial, sans-serif !important;

        font-size:
            14px !important;

        text-align:
            left !important;

        padding:
            7px 12px !important;

        margin:
            0 !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stButton"]:first-of-type
    > button:hover {{

        background-color:
            #a17a55 !important;

        border-color:
            #a17a55 !important;

        color:
            #ffffff !important;
    }}


    /* ========================================================
       DIVIDER
       ======================================================== */

    .sidebar-divider {{

        width:
            100% !important;

        height:
            1px !important;

        background:
            rgba(
                205,
                150,
                80,
                0.25
            ) !important;

        margin-top:
            22px !important;

        margin-bottom:
            8px !important;
    }}


    /* ========================================================
       RECENTS
       ======================================================== */

    .previous-chats-title {{

        width:
            100% !important;

        text-align:
            center !important;

        font-family:
            Arial, sans-serif !important;

        font-size:
            17px !important;

        font-weight:
            700 !important;

        color:
            #e8c78f !important;

        background:
            transparent !important;

        border:
            none !important;

        padding:
            5px 0 0 0 !important;

        margin:
            0 !important;
    }}

    .recents-bottom-space {{

        height:
            18px !important;

        min-height:
            18px !important;

        width:
            100% !important;

        background:
            transparent !important;
    }}


    /* ========================================================
       CHAT SPACING
       ======================================================== */

    .chat-row-marker {{

        height:
            18px !important;

        min-height:
            18px !important;

        width:
            100% !important;

        margin:
            0 !important;

        padding:
            0 !important;

        background:
            transparent !important;
    }}


    /* ========================================================
       CHAT ROW
       ======================================================== */

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"] {{

        width:
            100% !important;

        display:
            flex !important;

        align-items:
            center !important;

        background:
            transparent !important;

        margin:
            0 !important;

        padding:
            0 !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]
    [data-testid="stColumn"]:first-child {{

        flex:
            1 1 auto !important;

        width:
            auto !important;

        min-width:
            0 !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]
    [data-testid="stColumn"]:last-child {{

        flex:
            0 0 38px !important;

        width:
            38px !important;

        min-width:
            38px !important;
    }}


    /* ========================================================
       CHAT TITLE
       ======================================================== */

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]
    [data-testid="stColumn"]:first-child
    .stButton > button {{

        width:
            100% !important;

        min-width:
            100% !important;

        max-width:
            100% !important;

        box-sizing:
            border-box !important;

        background-color:
            #8a6647 !important;

        color:
            #f7eee4 !important;

        border:
            1px solid
            #8a6647 !important;

        border-radius:
            8px !important;

        box-shadow:
            none !important;

        outline:
            none !important;

        text-align:
            left !important;

        white-space:
            nowrap !important;

        overflow:
            hidden !important;

        text-overflow:
            ellipsis !important;

        padding:
            5px 12px !important;

        height:
            34px !important;

        min-height:
            34px !important;

        margin:
            0 !important;

        font-family:
            Arial, sans-serif !important;

        font-size:
            14px !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]
    [data-testid="stColumn"]:first-child
    .stButton > button:hover {{

        background-color:
            #a17a55 !important;

        border-color:
            #a17a55 !important;

        color:
            #ffffff !important;
    }}


    /* ========================================================
       THREE DOT BUTTON
       ======================================================== */

    [data-testid="stSidebar"]
    [data-testid="stPopover"] > button,

    [data-testid="stSidebar"]
    button[aria-haspopup="dialog"] {{

        width:
            34px !important;

        height:
            34px !important;

        min-width:
            34px !important;

        min-height:
            34px !important;

        max-width:
            34px !important;

        padding:
            0 !important;

        margin:
            0 !important;

        background-color:
            #8a6647 !important;

        color:
            #f7eee4 !important;

        border:
            1px solid
            #8a6647 !important;

        border-radius:
            8px !important;

        box-shadow:
            none !important;

        outline:
            none !important;

        opacity:
            0 !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]:hover
    [data-testid="stPopover"] > button,

    [data-testid="stSidebar"]
    [data-testid="stHorizontalBlock"]:hover
    button[aria-haspopup="dialog"] {{

        opacity:
            1 !important;
    }}

    [data-testid="stSidebar"]
    [data-testid="stPopover"] > button:hover,

    [data-testid="stSidebar"]
    button[aria-haspopup="dialog"]:hover {{

        background-color:
            #a17a55 !important;

        border-color:
            #a17a55 !important;

        color:
            #ffffff !important;
    }}


    /* ========================================================
       DELETE POPUP
       ======================================================== */

    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [role="dialog"][data-baseweb="popover"] {{

        background-color:
            #24140b !important;

        border:
            1px solid
            #765333 !important;

        border-radius:
            9px !important;

        box-shadow:
            0 8px 25px
            rgba(
                0,
                0,
                0,
                0.40
            ) !important;

        padding:
            5px !important;
    }}


    /* ========================================================
       DELETE BUTTON
       ======================================================== */

    [data-baseweb="popover"] button,
    [data-baseweb="popover"]
    .stButton > button,
    [role="dialog"]
    .stButton > button,
    [role="menu"] button {{

        width:
            100% !important;

        height:
            34px !important;

        background-color:
            #8a6647 !important;

        color:
            #f7eee4 !important;

        border:
            1px solid
            #8a6647 !important;

        border-radius:
            7px !important;

        box-shadow:
            none !important;

        text-align:
            left !important;

        padding:
            7px 12px !important;
    }}

    [data-baseweb="popover"] button:hover,
    [data-baseweb="popover"]
    .stButton > button:hover,
    [role="dialog"]
    .stButton > button:hover,
    [role="menu"] button:hover {{

        background-color:
            #a17a55 !important;

        border-color:
            #a17a55 !important;

        color:
            #ffffff !important;
    }}


    /* ========================================================
       HERO
       ======================================================== */

    .hero-title {{

        text-align:
            center !important;

        font-family:
            Georgia, serif !important;

        font-size:
            72px !important;

        font-weight:
            700 !important;

        color:
            #28160c !important;

        margin-top:
            6vh !important;

        margin-bottom:
            12px !important;
    }}

    .hero-divider {{

        text-align:
            center !important;

        font-family:
            Georgia, serif !important;

        font-size:
            22px !important;

        color:
            #7e4c1f !important;

        margin-bottom:
            20px !important;
    }}

    .hero-subtitle {{

        text-align:
            center !important;

        font-family:
            Arial, sans-serif !important;

        font-size:
            19px !important;

        color:
            #332217 !important;
    }}


    /* ========================================================
       CHAT MESSAGES
       ======================================================== */

    [data-testid="stChatMessage"] {{

        background:
            rgba(
                30,
                23,
                18,
                0.90
            ) !important;

        border:
            1px solid
            rgba(
                190,
                135,
                72,
                0.40
            ) !important;

        border-radius:
            15px !important;

        padding:
            15px !important;

        margin-bottom:
            10px !important;

        box-shadow:
            0 4px 16px
            rgba(
                0,
                0,
                0,
                0.20
            ) !important;
    }}

    [data-testid="stChatMessage"] p {{

        color:
            #f4e7d0 !important;

        font-size:
            16px !important;

        line-height:
            1.65 !important;
    }}

    [data-testid="stChatMessage"] li {{

        color:
            #f4e7d0 !important;
    }}

    [data-testid="stChatMessage"] strong {{

        color:
            #e8bb75 !important;
    }}


    /* ========================================================
       CHAT INPUT
       ======================================================== */

    [data-testid="stChatInput"] {{

        background:
            transparent !important;

        background-color:
            transparent !important;

        border:
            1px solid
            rgba(
                203,
                142,
                70,
                0.65
            ) !important;

        border-radius:
            17px !important;

        box-shadow:
            none !important;
    }}

    [data-testid="stChatInput"] textarea {{

        background:
            transparent !important;

        background-color:
            transparent !important;

        color:
            #f5ead8 !important;
    }}

    [data-testid="stChatInput"]
    textarea::placeholder {{

        color:
            #c2b29f !important;
    }}


    /* ========================================================
       FOOTER
       ======================================================== */

    footer {{
        visibility:
            hidden !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EMPTY CHAT SCROLL CONTROL
# ============================================================

if is_empty_chat:

    st.markdown(
        """
        <style>

        html,
        body {
            overflow: hidden !important;
        }

        [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
        }

        [data-testid="stMain"] {
            overflow: hidden !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # SIDEBAR TITLE
    # ========================================================

    st.markdown(
        """
        <div class="sidebar-title">
            Bharat Darshan
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "＋  New Chat",
        key="new_chat",
        use_container_width=True
    ):

        st.session_state.current_chat_id = None

        st.rerun()


    # ========================================================
    # DIVIDER
    # ========================================================

    st.markdown(
        """
        <div class="sidebar-divider"></div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # RECENTS
    # ========================================================

    st.markdown(
        """
        <div class="previous-chats-title">
            Recents
        </div>

        <div class="recents-bottom-space"></div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # USER-SPECIFIC CHAT HISTORY
    # ========================================================

    chats = get_all_chats(
        user_id
    )


    # ========================================================
    # DISPLAY CHATS
    # ========================================================

    for chat_id, title, created_at in chats:

        st.markdown(
            '<div class="chat-row-marker"></div>',
            unsafe_allow_html=True
        )


        # ====================================================
        # CHAT TITLE + MENU
        # ====================================================

        col_title, col_menu = st.columns(
            [0.88, 0.12],
            gap="small"
        )


        # ====================================================
        # CHAT TITLE
        # ====================================================

        with col_title:

            if st.button(
                title,
                key=f"chat_{chat_id}",
                use_container_width=True
            ):

                st.session_state.current_chat_id = (
                    chat_id
                )

                st.rerun()


        # ====================================================
        # THREE DOT MENU
        # ====================================================

        with col_menu:

            with st.popover(
                "⋯",
                use_container_width=False
            ):

                if st.button(
                    "Delete",
                    key=f"delete_{chat_id}",
                    use_container_width=True
                ):

                    delete_chat(
                        chat_id,
                        user_id
                    )

                    if (
                        st.session_state.current_chat_id
                        == chat_id
                    ):

                        st.session_state.current_chat_id = (
                            None
                        )

                    st.rerun()


# ============================================================
# HERO SECTION
# ============================================================

if is_empty_chat:

    st.markdown(
        """
        <div class="hero-title">
            Bharat Darshan
        </div>

        <div class="hero-divider">
            ────── ❖ ──────
        </div>

        <div class="hero-subtitle">
            Ask questions and explore the history of Ancient India.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DISPLAY CURRENT CHAT
# ============================================================

if not is_empty_chat:

    for role, content in saved_messages:

        # ====================================================
        # USER MESSAGE
        # ====================================================

        if role == "user":

            if os.path.exists(USER_AVATAR):

                with st.chat_message(
                    "user",
                    avatar=USER_AVATAR
                ):

                    st.markdown(
                        content
                    )

            else:

                with st.chat_message(
                    "user"
                ):

                    st.markdown(
                        content
                    )


        # ====================================================
        # ASSISTANT MESSAGE
        # ====================================================

        else:

            if os.path.exists(BOT_AVATAR):

                with st.chat_message(
                    "assistant",
                    avatar=BOT_AVATAR
                ):

                    st.markdown(
                        content
                    )

            else:

                with st.chat_message(
                    "assistant"
                ):

                    st.markdown(
                        content
                    )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask something about Ancient India..."
)


# ============================================================
# PROCESS NEW QUESTION
# ============================================================

if question:

    # ========================================================
    # CREATE NEW CHAT
    # ========================================================

    if st.session_state.current_chat_id is None:

        clean_question = question.strip()

        title = clean_question[:40]

        if len(clean_question) > 40:

            title += "..."

        st.session_state.current_chat_id = (
            create_chat(
                user_id,
                title
            )
        )


    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    save_message(
        st.session_state.current_chat_id,
        "user",
        question
    )


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    if os.path.exists(USER_AVATAR):

        with st.chat_message(
            "user",
            avatar=USER_AVATAR
        ):

            st.markdown(
                question
            )

    else:

        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )


    # ========================================================
    # GENERATE BOT RESPONSE
    # ========================================================

    if os.path.exists(BOT_AVATAR):

        with st.chat_message(
            "assistant",
            avatar=BOT_AVATAR
        ):

            with st.spinner(
                "Searching through Bharat Darshan..."
            ):

                answer = ask_history_bot(
                    question
                )

            st.markdown(
                answer
            )

    else:

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Searching through Bharat Darshan..."
            ):

                answer = ask_history_bot(
                    question
                )

            st.markdown(
                answer
            )


    # ========================================================
    # SAVE BOT RESPONSE
    # ========================================================

    save_message(
        st.session_state.current_chat_id,
        "assistant",
        answer
    )


    # ========================================================
    # REFRESH
    # ========================================================

    st.rerun()