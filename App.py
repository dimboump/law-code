import streamlit as st

from config import APP_NAME
from modules.authentication import AuthenticationManager
from modules.conversation import ConversationHandler
from modules.session import SessionHandler
from modules.views import ViewsManager

st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
)

st.title(APP_NAME)

if "authentication_manager" not in st.session_state:
    st.session_state.authentication_manager = AuthenticationManager()

if "session_handler" not in st.session_state:
    st.session_state.session_handler = SessionHandler()

if "conversation_handler" not in st.session_state:
    st.session_state.conversation_handler = ConversationHandler()

# Always instantiate last
if "views_manager" not in st.session_state:
    st.session_state.views_manager = ViewsManager()

st.session_state.views_manager.get_main_view()
