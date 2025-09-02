import streamlit as st

from components.chat_tab import render_chat_tab
from components.documents_tab import render_documents_tab

st.set_page_config(
    page_title="GraphRAG Demo",
    page_icon="icon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "mode" not in st.session_state:
    st.session_state.mode = "msft"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_full_graph" not in st.session_state:
    st.session_state.show_full_graph = True
if "settings_open" not in st.session_state:
    st.session_state.settings_open = False

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 0.8rem;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        width: 10rem;
        height: 2.5rem;
        border-radius: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #6366f1 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center;">GraphRAG Demonstration</h1>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 3])

with col2:
    st.session_state.mode = st.radio(
        "Select Mode", 
        options=["msft", "hku"], 
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

tab1, tab2 = st.tabs(["📄 Documents", "💬 Chat"])

with tab1:
    render_documents_tab(st.session_state.mode)

with tab2:
    render_chat_tab(st.session_state.mode)

