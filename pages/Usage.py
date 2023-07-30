import streamlit as st

import components
import utils

st.markdown("# Usage 💸")
st.sidebar.markdown("# Usage 💸")

with st.sidebar:
    components.show_usage_stats()

period = st.radio("Period for usage", ["This week", "This month", "All time"], index=1, horizontal=True)
accumulated = st.checkbox("Accumulated", value=True)

if period == 'This week':
    df = st.session_state["UsageLogger"].get_week()
elif period == 'This month':
    df = st.session_state["UsageLogger"].get_month()
else:
    df = st.session_state["UsageLogger"].get_all_usage()

if accumulated:
    df['cost'] = df['cost'].cumsum()
    st.line_chart(data=df, x='time', y='cost')
else:
    st.bar_chart(data=df, x='time', y='cost')