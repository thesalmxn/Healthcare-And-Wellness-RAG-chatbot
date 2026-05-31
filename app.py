import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat.chat import build_chain

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health & Wellness Assistant",
    page_icon="🌿",
    layout="centered"
)

# ── Sidebar with settings ──────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Language preference
    st.subheader("Language")
    lang_preference = st.radio(
        "Preferred language:",
        ["Auto-detect", "Greek", "English"],
        help="Auto-detect will respond in the language you ask"
    )
    
    st.divider()
    
    # Sample queries
    st.subheader("📝 Sample Queries")
    
    with st.expander("🇬🇷 Greek Examples"):
        st.markdown("""
        - Τι βοηθάει τον ύπνο;
        - Πώς μπορώ να μειώσω το άγχος;
        - Ποιες συνήθειες βελτιώνουν την πέψη;
        - Πώς να ενισχύσω την ενέργειά μου;
        - Ποια είναι τα οφέλη της χαλάρωσης;
        """)
    
    with st.expander("🇬🇧 English Examples"):
        st.markdown("""
        - What wellness practices help with stress?
        - Which habits improve digestion?
        - How do I improve sleep quality?
        - What are the benefits of mindful breathing?
        - How can I support immune health?
        """)
    
    st.divider()
    
    # About section
    st.subheader("ℹ️ About")
    st.caption("""
    This chatbot provides information about Greek health and wellness topics 
    based on 350+ documents. Always consult a healthcare professional 
    before acting on health advice.
    """)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────
st.title("🌿 Health & Wellness Assistant")
st.caption("Ask me anything about health & wellness remedies and advices.")
st.divider()

# ── Load chain once and cache it ───────────────────────────────────────────
@st.cache_resource
def get_chain():
    return build_chain()

chain = get_chain()

# ── Chat history ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat input ─────────────────────────────────────────────────────────────
if question := st.chat_input("Ask about health & wellness..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = chain.invoke(question)
        st.markdown(answer)
        
        # Add helpful feedback buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("👍", key=f"like_{len(st.session_state.messages)}"):
                st.success("Thanks for the feedback!")
        with col2:
            if st.button("👎", key=f"dislike_{len(st.session_state.messages)}"):
                st.warning("Feedback noted. We'll improve!")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Footer ─────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ This chatbot provides educational information only. Always consult a healthcare professional before acting on health advice.")