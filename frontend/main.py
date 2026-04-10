import streamlit as st

st.set_page_config(
    page_title="Smart Memory System",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Smart Memory + Chat System")
st.markdown("""
Welcome to your intelligent memory system. 
This system doesn't just chat; it **remembers**, **learns**, and **connects** your personal information.

### 🎯 Core Features:
1. **Chat**: Talk to the AI. It will decide what to remember.
2. **Memory Vault**: View all the structured memories saved about you.
3. **Graph View**: See how your memories are connected through entities and relationships.

---
**User ID:** `123` (Default for this demo)
""")

if "user_id" not in st.session_state:
    st.session_state.user_id = "123"

st.sidebar.success("Select a page above.")
