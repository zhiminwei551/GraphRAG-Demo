import streamlit as st
from utils import list_files, save_uploaded_file, delete_file, process_files


def render_documents_tab(mode):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 File Management")
        
        with st.container(height=500):
            files = list_files(mode)
            
            if not files:
                st.info("📋 No documents found. Please upload files.")
            else:
                st.success(f"📊 {len(files)} file(s) ready for processing")
                
                for i, file in enumerate(files):
                    file_col1, file_col2 = st.columns([13, 1])
                    with file_col1:
                        st.text(f"📄 {file}")
                    with file_col2:
                        if st.button("🗑️", key=f"delete_{file}_{mode}", help=f"Delete {file}"):
                            delete_file(file, mode)
                            st.success(f"✅ Deleted {file}")
                            st.rerun()
    
    with col2:
        st.subheader("📤 Upload Documents")

        with st.container(height=211):
            uploaded_file = st.file_uploader(
                "Choose a text file", 
                type=["txt"], 
                key=f"uploader_{mode}",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                save_uploaded_file(uploaded_file, mode)
                st.success(f"✅ File uploaded successfully!")
                st.rerun()
        
        st.subheader("⚙️ Document Processing")

        with st.container(height=211):
            files = list_files(mode)
            disabled = len(files) == 0
            
            if disabled:
                st.warning("⚠️ No files to process. Please upload documents first.")
            else:
                st.info(f"🔄 Ready to process {len(files)} file(s) using {mode.upper()} mode")
            
            if st.button(
                f"🚀 Process with {mode.upper()}", 
                disabled=disabled,
                use_container_width=True,
            ):
                with st.spinner(f"🔄 Processing {len(files)} document(s)..."):
                    
                    process_files(mode)
                    st.success("🎉 Processing completed!")
                    
                    if "chat_history" in st.session_state:
                        st.session_state.chat_history = []
                    if "show_full_graph" in st.session_state:
                        st.session_state.show_full_graph = True
                    if hasattr(st.session_state, "current_subgraph"):
                        delattr(st.session_state, "current_subgraph")

