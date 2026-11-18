"""Entry point: page setup, navigation, background and optional music."""
import base64

import streamlit as st

from game import init_state

st.set_page_config(page_title="Animal Guessing Game", page_icon="assets/favicon.png")
st.logo("assets/logo.svg", size="large")
init_state()

# Faint paw-print pattern behind a soft white content card. Sound effects on the page
# are played by hidden audio elements (only the sidebar music keeps its controls).
with open("assets/paws.svg", "rb") as f:
    paws = base64.b64encode(f.read()).decode()
st.markdown(f"""<style>
.stApp {{ background: url(data:image/svg+xml;base64,{paws}) #FAF7F0; }}
.block-container {{ background: rgba(255, 255, 255, .85); border-radius: 16px;
    margin-top: 1rem; padding: 2rem 2.5rem 3rem; }}
.block-container audio {{ position: absolute; width: 0; height: 0; opacity: 0; }}
</style>""", unsafe_allow_html=True)

page = st.navigation([
    st.Page("pages/play.py", title="Play", default=True),
    st.Page("pages/stats.py", title="Stats"),
])

# Music is off by default: browsers only allow sound after the user clicks something
if st.sidebar.toggle("Background music"):
    st.sidebar.audio("assets/music.wav", loop=True, autoplay=True)

page.run()
