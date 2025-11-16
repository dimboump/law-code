import streamlit as st

from modules.conversation import ConversationHandler
from modules.session import SessionHandler
from modules.views import ViewsManager

ENV = "DEV"
APP_NAME = "Τσο και Law"

st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
)

st.title(APP_NAME)

if "session_handler" not in st.session_state:
    st.session_state.session_handler = SessionHandler()
    st.session_state.session_handler.create_session()

if "conversation_handler" not in st.session_state:
    st.session_state.conversation_handler = ConversationHandler()

# Always instantiate last
if "views_manager" not in st.session_state:
    st.session_state.views_manager = ViewsManager()

st.session_state.views_manager.get_main_view()
