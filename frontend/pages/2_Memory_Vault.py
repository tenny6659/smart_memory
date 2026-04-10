import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Memory Vault", page_icon="🗄️")

st.title("🗄️ Memory Vault")

BACKEND_URL = "http://localhost:8000"
USER_ID = "123"

try:
    response = requests.get(f"{BACKEND_URL}/memories?userId={USER_ID}")
    if response.status_code == 200:
        memories = response.json()
        if not memories:
            st.info("No memories saved yet. Start chatting!")
        else:
            # Display memories as cards
            cols = st.columns(2)
            for idx, memory in enumerate(memories):
                with cols[idx % 2]:
                    with st.container(border=True):
                        st.subheader(f"Memory #{memory['id']}")
                        st.write(f"**Text:** {memory['text']}")
                        st.markdown(f"**Category:** `{memory['category']}`")
                        st.write(f"**Importance:** {memory['importance_score']:.2f}")
                        st.write(f"**Timestamp:** {memory['timestamp'][:19]}")
                        
                        if st.button(f"Find Neighbors for #{memory['id']}", key=f"btn_{memory['id']}"):
                            n_resp = requests.get(f"{BACKEND_URL}/memories/{memory['id']}/neighbors")
                            if n_resp.status_code == 200:
                                n_data = n_resp.json()
                                if n_data["neighbors"]:
                                    for n in n_data["neighbors"]:
                                        st.caption(f"→ Neighbor {n['id']}: {n['text']} ({n['relation']})")
                                else:
                                    st.caption("No neighbors found for this memory.")
    else:
        st.error("Could not load memories from backend.")
except Exception as e:
    st.error(f"Error: {e}")
