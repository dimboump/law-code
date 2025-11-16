import streamlit as st

from App import APP_NAME
from modules.models import gpt_models_to_df

st.set_page_config(page_title=f"Κόστος | {APP_NAME}")

st.table(gpt_models_to_df(), border=True)
