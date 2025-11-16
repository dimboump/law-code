from uuid import uuid4

import streamlit as st


class SessionHandler:
    def create_session(self):
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid4())

    def clear_state(self):
        st.session_state.clear()
        st.rerun()
