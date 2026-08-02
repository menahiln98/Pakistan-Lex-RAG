import streamlit as st
import os

from generate import generate_answer
from manage_documents import add_document, delete_document, restore_document, load_status

st.set_page_config(page_title="Pakistan Law Assistant", layout="wide")

CATEGORIES = [
    ("women", "Women's Rights", "Harassment, domestic violence, workplace"),
    ("children", "Children's Rights", "Abuse, protection, custody, education"),
    ("students", "Students' Rights", "Academic rights, institutional misconduct"),
    ("employees", "Employees' Rights", "Labour rights, wrongful termination"),
    ("minorities", "Religious Minorities", "Constitutional protections, discrimination"),
    ("defamation", "Defamation", "False accusations, reputation protection"),
]

st.markdown("""
<style>
.stApp { background-color: #F3EDE0; }
section[data-testid="stSidebar"] { background-color: #2B5749; }
section[data-testid="stSidebar"] * { color: #D4E8DF !important; }
h1 { font-family: 'Georgia', serif; color: #2B5749; text-align: center; }
.stButton button {
    background-color: #2B5749; color: #D4E8DF; border: none;
    border-radius: 6px; padding: 10px 14px; width: 100%; text-align: left;
}
.stButton button:hover { background-color: #3D7A63; }
.user-msg {
    background: #2B5749; color: #D4E8DF; border-radius: 8px;
    padding: 12px 16px; margin: 8px 0; max-width: 70%; margin-left: auto;
}
.assistant-msg {
    background: #FDFAF3; border: 1px solid #C9C0AD; border-radius: 8px;
    padding: 16px 20px; margin: 8px 0;
}
.notice-box {
    background: rgba(43,87,73,0.06); border: 1px solid #C9C0AD;
    border-radius: 6px; padding: 14px 18px; margin-bottom: 20px;
}
.assistant-msg p { margin: 4px 0 !important; }
.assistant-msg ul, .assistant-msg ol { margin: 4px 0 !important; padding-left: 20px !important; }
.assistant-msg li { margin: 2px 0 !important; }
.assistant-msg h1, .assistant-msg h2, .assistant-msg h3, .assistant-msg h4 {
    margin: 10px 0 4px 0 !important;
    padding: 0 !important;
}
.assistant-msg table {
    border-collapse: collapse !important;
    margin: 6px 0 !important;
}
.assistant-msg th, .assistant-msg td {
    padding: 6px 10px !important;
    border: 1px solid #C9C0AD !important;
}
.assistant-msg hr { margin: 8px 0 !important; }
.assistant-msg blockquote {
    margin: 6px 0 !important;
    padding: 4px 0 4px 12px !important;
    border-left: 3px solid #2B5749;
}
.assistant-msg { line-height: 1.5 !important; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

def submit_query(text):
    text = text.strip()
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.is_loading = True

with st.sidebar:
    st.markdown("### ⚖️ Pakistan Law\nAssistant")
    if st.button("New Consultation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("**Areas of Law**")
    for cat_id, label, _ in CATEGORIES:
        if st.button(label, key=f"sidebar_{cat_id}"):
            submit_query(f"Tell me about my rights under {label} and what legal protections are available to me.")
            st.rerun()
    st.markdown("---")
    st.caption("This assistant provides legal information, not legal advice. Consult a qualified advocate for court proceedings.")

if not st.session_state.messages:
    st.markdown("<h1>Pakistan Law Assistant</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="notice-box">
    <b>Important Notice</b><br>
    This assistant provides legal information based on Pakistani constitutional and statutory law,
    grounded in real retrieved documents. It does not provide legal advice.
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (cat_id, label, sub) in enumerate(CATEGORIES):
        with cols[i % 3]:
            if st.button(f"{label}\n\n{sub}", key=f"card_{cat_id}"):
                submit_query(f"Tell me about my rights under {label} and what legal protections are available to me.")
                st.rerun()
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-msg">\n\n{msg["content"]}\n\n</div>', unsafe_allow_html=True)

    if st.session_state.is_loading:
        with st.spinner("Retrieving legal provisions..."):
            last_user_msg = st.session_state.messages[-1]["content"]
            answer = generate_answer(last_user_msg, print_stream=False)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.is_loading = False
            st.rerun()

query_input = st.text_area("Describe your situation or ask about a specific law or right:", height=100, key="query_box")
if st.button("Submit", type="primary"):
    submit_query(query_input)
    st.rerun()

st.markdown("---")
st.subheader("Manage Documents")

status = load_status()
for file_id, info in status.items():
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    col1.write(file_id)
    col2.write(info["category"])
    col3.write(info["status"])
    if info["status"] == "active":
        if col4.button("Delete", key=f"del_{file_id}"):
            delete_document(file_id)
            st.rerun()
    else:
        if col4.button("Restore", key=f"res_{file_id}"):
            restore_document(file_id)
            st.rerun()

st.markdown("#### Add New Document")
uploaded = st.file_uploader("Upload a PDF", type="pdf")
category = st.selectbox("Category", [c[0] for c in CATEGORIES])
if st.button("Add Document") and uploaded:
    temp_path = os.path.join("data", "uploads_temp", uploaded.name)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    add_document(temp_path, category)
    os.remove(temp_path)
    st.success(f"Added {uploaded.name}")
    st.rerun()