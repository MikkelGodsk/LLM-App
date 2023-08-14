import streamlit as st
import langchain as lc

import utils
import components

utils.setup()  # In case the app wasn't setup (just creates some folders if needed)
utils.login()
utils.ensure_logged_in()

add_ons = ["Persistent memory", "Python REPL", "Google", "Files", "Wikipedia", "CSV files", "Wolfram Alpha", "YouTube (OpenAI whisper)", "Human", "Google places", "Office 365", "Home automation"]
add_ons.sort()

# Get OpenAI API key
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

st.title("ChatGPT🤖")
st.sidebar.markdown("# Basic ChatGPT🤖")

# Setup usage logger
if "UsageLogger" not in st.session_state:
    st.session_state["UsageLogger"] = utils.UsageLogger()

# Sidebar
with st.sidebar:
    current_conversation_title = components.show_past_conversations()
    components.show_usage_stats()

# Setup conversation
if "Conversation" not in st.session_state:
    utils.setup_new_chat_memory(current_conversation_title)

# Settings
with st.expander("Settings"):
    col1, col2 = st.columns((5,5))
    with col1:
        st.session_state["model"] = st.selectbox("Select a model", ["gpt-3.5-turbo", "gpt-4"], disabled=st.session_state["Conversation"].started)
    with col2:
        st.session_state["temperature"] = st.select_slider("Randomness", options=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], value=0.5, disabled=st.session_state["Conversation"].started)     
    # st.multiselect for model properties (such as internet access, tools, persistent memory etc.)
    st.session_state["model_settings"] = st.multiselect("Select add-ons", add_ons, disabled=st.session_state["Conversation"].started)
    # Maybe warn if e.g. home automation and python are not selected at once. I imagine home automation would call python functions

# Chat
components.chat(utils.create_model)