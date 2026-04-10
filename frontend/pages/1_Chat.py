import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Chat", page_icon="💬")

st.title("💬 Chat with Smart Memory")

BACKEND_URL = "http://localhost:8000"
USER_ID = "123"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "decision" in message:
            st.caption(f"Decision: {message['decision']}")

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/events/prompt",
                    json={
                        "userId": USER_ID,
                        "promptText": prompt,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.markdown(data["response"])
                    st.caption(f"Decision: **{data['decision'].upper()}**")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": data["response"],
                        "decision": data["decision"]
                    })
                else:
                    st.error("Error from backend.")
            except Exception as e:
                st.error(f"Could not connect to backend: {e}")

# Sidebar Decision Logs
st.sidebar.title("Decision Logs")
try:
    logs_resp = requests.get(f"{BACKEND_URL}/decisions?userId={USER_ID}")
    if logs_resp.status_code == 200:
        logs = logs_resp.json()
        for log in reversed(logs):
            st.sidebar.info(f"**Prompt:** {log['prompt']}\n\n**Decision:** {log['decision']}")
except:
    st.sidebar.error("Could not load logs.")
