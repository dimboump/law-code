import streamlit as st


class AuthenticationManager:
    def __init__(self):
        if not self.check_password():
            st.stop()

    def check_password(self):
        """Returns `True` if the user had the correct password."""

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["password"] == st.secrets["password"]:
                st.session_state["password_correct"] = True
                st.session_state["password"] = None  # don't store password
            else:
                st.session_state["password_correct"] = False

        if "password_correct" not in st.session_state:
            # First run, show input for password
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            return False
        elif not st.session_state["password_correct"]:
            # Password incorrect, show input + error
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.error("😕 Password incorrect")
            return False
        else:
            return True
