import streamlit as st
import shutil, os
from datetime import datetime

import components
import utils

st.set_page_config(layout="wide")

utils.ensure_logged_in(show_text=True)
FILE_DIR = 'Files'

st.markdown("# Files 📄")
st.sidebar.markdown("# Files 📄")

with st.sidebar:
    st.metric("Disk usage: ", "{:.3f} GB".format(shutil.disk_usage(os.getcwd()).used/(1024**3)))
    st.metric("Free disk space: ", "{:.3f} GB".format(shutil.disk_usage(os.getcwd()).free/(1024**3)))
    st.metric("Total disk size: ", "{:.3f} GB".format(shutil.disk_usage(os.getcwd()).total/(1024**3)))
    # st.divider()
    pass  # Show file system?

# Upload files
st.markdown("## Upload files")
uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        if os.path.isfile(os.path.join(FILE_DIR, file_name)):
            st.error('File {:s} already exists'.format(file_name), icon="🚨")
        with open(os.path.join(FILE_DIR, file_name), 'wb') as f_obj:
            f_obj.write(uploaded_file.getbuffer())


# List current files: https://stackoverflow.com/questions/69492406/streamlit-how-to-display-buttons-in-a-single-line
st.divider()
st.markdown("## Current files")
fields = ["File name", "Date of modification", "File size", "Modify", "Download", "Delete"]
colms = st.columns((2,1,1,1,1,1))
for f, c in zip(fields, colms):
    c.write(f)

files = os.listdir(FILE_DIR)
for i, file in enumerate(files):
    col1, col2, col3, col4, col5, col6 = st.columns((2,1,1,1,1,1))  # File name, Date, Size, Download, Delete
    col1.write(file)  # File name
    file = os.path.join(FILE_DIR, file)
    col2.write(datetime.utcfromtimestamp(int(os.path.getmtime(file))))  # Date of modification
    col3.write("{:.3f} MB".format(os.path.getsize(file)/(1024**2)))
    with col4:
        modify = st.button("Modify", key=i+len(files))
    with col5:
        with open(file, 'rb') as f_obj:
            if modify:
                st.download_button("Download", data=f_obj.read(), file_name=file)
    with col6:
        if modify and st.button("Delete", key=i):
            os.remove(file)
            st.experimental_rerun()