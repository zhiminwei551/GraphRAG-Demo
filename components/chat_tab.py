import asyncio
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

from utils import (
    query_hku, query_msft, 
    load_hku_full_graph, load_msft_full_graph,
    extract_hku_subgraph, extract_msft_subgraph
)

def render_chat_tab(mode):

    st.markdown(
        """
        <style>
        .stButton > button {
            padding: 0.30rem 0.9rem;
            height: 2.1rem;
            line-height: 2.1rem;
            border-radius: 8px;
            white-space: nowrap;
        }

        div[data-testid="stChatInput"] { min-height: 3.5rem !important; max-height: 3.5rem !important; }

        div[data-testid="stChatInput"] textarea {
            min-height: 2.2rem !important;
            max-height: 2.2rem !important;
            overflow-y: auto !important;
            resize: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    if mode == "hku" and "hku_params" not in st.session_state:
        st.session_state.hku_params = {
            "mode": "local",
            "response_type": "Multiple Paragraphs",
            "top_k": 10,
            "chunk_top_k": 5
        }
    
    elif mode == "msft" and "msft_params" not in st.session_state:
        st.session_state.msft_params = {
            "community_level": 2,
            "response_type": "Multiple Paragraphs"
        }
    
    if "processing_query" not in st.session_state:
        st.session_state.processing_query = False
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
    
    if st.session_state.get("settings_open", False):
        graph_col, chat_col, settings_col = st.columns([3, 3, 1])
    else:
        graph_col, chat_col = st.columns([1, 1])
        settings_col = None
    
    with graph_col:
        st.markdown('<h3>🔗 Knowledge Graph</h3>', unsafe_allow_html=True)

        with st.container(height=500):
            if st.session_state.show_full_graph:
                if mode == "hku":
                    nodes_data, edges_data = load_hku_full_graph()
                else:
                    nodes_data, edges_data = load_msft_full_graph()
                
                if nodes_data and edges_data:
                    render_graph(nodes_data, edges_data)
                else:
                    st.info("📊 No graph data available. Please process documents first.")
            
            elif hasattr(st.session_state, "current_subgraph"):
                nodes_data, edges_data = st.session_state.current_subgraph

                if nodes_data and edges_data:
                    render_graph(nodes_data, edges_data)
                else:
                    st.info("📊 No subgraph data available for this query.")
    
    with chat_col:
        title_col, actions_col = st.columns([3, 2])

        with title_col:
            st.markdown('<h3>💬 Chat</h3>', unsafe_allow_html=True)
        with actions_col:

            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("🗑️ Clear", key=f"clear_chat_header_{mode}", use_container_width=True):
                    st.session_state.chat_history = []
                    st.session_state.show_full_graph = True
                    st.session_state.processing_query = False
                    st.session_state.pending_query = None

                    if hasattr(st.session_state, "current_subgraph"):
                        delattr(st.session_state, "current_subgraph")
                    
                    st.rerun()
            with b2:
                if st.button("⚙️ Settings", key=f"toggle_settings_{mode}", use_container_width=True):
                    st.session_state.settings_open = not st.session_state.get("settings_open", False)
                    st.rerun()
        
        with st.container(height=444):
            if st.session_state.chat_history or st.session_state.processing_query:

                for _, (q, a) in enumerate(st.session_state.chat_history):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 0.5rem;">
                        <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 18px; border-bottom-right-radius: 4px; max-width: 70%; font-size: 0.9rem;">
                            {q}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if a:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin-bottom: 0.5rem;">
                            <div style="background: #f1f5f9; color: #020617; padding: 0.5rem 1rem; border-radius: 18px; border-bottom-left-radius: 4px; max-width: 70%; font-size: 0.9rem;">
                                {a}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if st.session_state.processing_query and st.session_state.pending_query:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 0.5rem;">
                        <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 18px; border-bottom-right-radius: 4px; max-width: 70%; font-size: 0.9rem;">
                            {st.session_state.pending_query}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("🤔 Thinking...")
                
            else:
                st.markdown("""
                <div style="display: flex; align-items: center; justify-content: center; height: 350px; color: #9ca3af; text-align: center; flex-direction: column;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">💭</div>
                    <div style="font-size: 1.2rem; font-weight: 500; margin-bottom: 0.5rem;">Ready to chat!</div>
                    <div style="font-size: 0.9rem; opacity: 0.7;">Ask me anything about your documents</div>
                </div>
                """, unsafe_allow_html=True)
        
        message = st.chat_input(placeholder="Type your question here and press Enter...")
        
        if message and not st.session_state.processing_query:
            st.session_state.processing_query = True
            st.session_state.pending_query = message
            st.rerun()
    
    if settings_col is not None:
        with settings_col:
            st.markdown('<h3>⚙️ Settings</h3>', unsafe_allow_html=True)
            render_settings_panel(mode)
    
    if st.session_state.processing_query and st.session_state.pending_query:
        query_text = st.session_state.pending_query
        
        try:
            if mode == "hku":
                query_params = st.session_state.get("hku_params", {})
                query_mode = query_params.get("mode", "local")
                response_type = query_params.get("response_type", "Multiple Paragraphs")
                top_k = query_params.get("top_k", 10)
                chunk_top_k = query_params.get("chunk_top_k", 5)
                
                response, (entities, relationships) = asyncio.run(
                    query_hku(
                        query_text, 
                        mode=query_mode,
                        response_type=response_type,
                        top_k=top_k,
                        chunk_top_k=chunk_top_k
                    )
                )
                
                nodes_data, edges_data = extract_hku_subgraph(entities, relationships)
                
            else:
                query_params = st.session_state.get("msft_params", {})
                community_level = query_params.get("community_level", 2)
                response_type = query_params.get("response_type", "Multiple Paragraphs")
                
                response, context_data = query_msft(
                    query_text,
                    community_level=community_level,
                    response_type=response_type
                )
                
                nodes_data, edges_data = extract_msft_subgraph(context_data)
            
            st.session_state.chat_history.append((query_text, response))
            st.session_state.show_full_graph = False
            st.session_state.current_subgraph = (nodes_data, edges_data)
            
        except Exception as e:
            error_response = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append((query_text, error_response))
        
        finally:
            st.session_state.processing_query = False
            st.session_state.pending_query = None
            st.rerun()


def render_settings_panel(mode):
    with st.container(height=500):
        if mode == "hku":
            hku_mode = st.selectbox(
                "Query Mode",
                options=["local", "global", "mix"],
                index=["local", "global", "mix"].index(st.session_state.hku_params.get("mode", "local")),
                key="hku_mode_select"
            )
            
            response_type = st.selectbox(
                "Response Format",
                options=["Multiple Paragraphs", "Single Paragraph"],
                index=["Multiple Paragraphs", "Single Paragraph"].index(
                    st.session_state.hku_params.get("response_type", "Multiple Paragraphs")
                ),
                key="hku_response_type_select"
            )
            
            top_k = st.number_input(
                "Top K",
                min_value=1,
                max_value=50,
                value=st.session_state.hku_params.get("top_k", 10),
                step=1,
                key="hku_top_k_input"
            )
            
            chunk_top_k = st.number_input(
                "Chunk Top K",
                min_value=1,
                max_value=20,
                value=st.session_state.hku_params.get("chunk_top_k", 5),
                step=1,
                key="hku_chunk_top_k_input"
            )
            
            st.session_state.hku_params = {
                "mode": hku_mode,
                "response_type": response_type,
                "top_k": top_k,
                "chunk_top_k": chunk_top_k
            }
            
        else:
            community_level = st.selectbox(
                "Community Level",
                options=[0, 1, 2, 3, 4],
                index=[0, 1, 2, 3, 4].index(st.session_state.msft_params.get("community_level", 2)),
                key="msft_community_level_select"
            )
            
            response_type = st.selectbox(
                "Response Format",
                options=["Multiple Paragraphs", "Single Paragraph"],
                index=["Multiple Paragraphs", "Single Paragraph"].index(
                    st.session_state.msft_params.get("response_type", "Multiple Paragraphs")
                ),
                key="msft_response_type_select"
            )
            
            st.session_state.msft_params = {
                "community_level": community_level,
                "response_type": response_type
            }


def render_graph(nodes_data, edges_data):
    try:
        nodes = []
        for node_data in nodes_data:
            node = Node(
                id=node_data.get("id"),
                label=node_data.get("label"),
                size=20,
                color=node_data.get("color"),
                title=node_data.get("title")
            )
            nodes.append(node)
        
        edges = []
        for edge_data in edges_data:
            edge = Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                title=edge_data.get("title"),
                width=2
            )
            edges.append(edge)
        
        config = Config(directed=False)
        
        return agraph(nodes=nodes, edges=edges, config=config)
        
    except Exception as e:
        st.error(f"Error rendering graph: {str(e)}")
        return None

