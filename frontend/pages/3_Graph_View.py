import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Graph View", page_icon="🕸️", layout="wide")

st.title("🕸️ Knowledge Graph View")

BACKEND_URL = "http://localhost:8000"
USER_ID = "123"

def create_graph(data):
    net = Network(height="600px", width="100%", bgcolor="#f8f9fb", font_color="#333333", directed=True)
    
    # Configure physics for better layout
    net.force_atlas_2based()
    
    for node in data["nodes"]:
        color = "#4e79a7" if node["title"] == "PERSON" else "#f28e2b"
        net.add_node(node["id"], label=node["label"], title=f"Type: {node['title']}", color=color, size=25)
        
    for edge in data["edges"]:
        net.add_edge(edge["from"], edge["to"], label=edge["label"], title=edge["title"], width=2)
        
    # Save and read with encoding handling
    path = "graph.html"
    net.save_graph(path)
    return path

try:
    response = requests.get(f"{BACKEND_URL}/graph/data?userId={USER_ID}")
    if response.status_code == 200:
        data = response.json()
        if not data["nodes"]:
            st.info("💡 **No entities extracted yet.**")
            st.markdown("""
            The graph is built from personal facts the AI saves. Try telling the AI something about yourself!
            
            **Try these messages in Chat:**
            - "I am a software engineer"
            - "I work at Google in London"
            - "My friend's name is Mansi"
            - "I love hiking and reading sci-fi books"
            """)
        else:
            st.success(f"Showing {len(data['nodes'])} entities and {len(data['edges'])} relationships.")
            graph_path = create_graph(data)
            with open(graph_path, 'r', encoding='utf-8') as f:
                html_data = f.read()
            components.html(html_data, height=650)
            os.remove(graph_path)
    else:
        st.error("Could not load graph data.")
except Exception as e:
    st.error(f"Error: {e}")
