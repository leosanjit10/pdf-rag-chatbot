import time
from datetime import datetime

import streamlit as st

from ingest import build_vector_store
from query import ask_question, reset_qa_chain


st.set_page_config(
    page_title="PDF Intelligence Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #0f172a;
            --panel: #111827;
            --panel-soft: #1f2937;
            --muted: #94a3b8;
            --primary: #8b5cf6;
            --primary-soft: rgba(139, 92, 246, 0.15);
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --text: #e5e7eb;
            --border: rgba(148, 163, 184, 0.18);
        }

        .stApp {
            background: linear-gradient(180deg, #0b1120 0%, #111827 100%);
            color: var(--text);
        }

        .hero {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(14, 165, 233, 0.12));
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 2rem 2rem 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.24);
        }

        .hero h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.4rem;
            line-height: 1.1;
            color: #f8fafc;
        }

        .hero p {
            margin: 0;
            color: #dbeafe;
            font-size: 1rem;
            line-height: 1.6;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-top: 1rem;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.8rem;
            border: 1px solid var(--border);
            background: rgba(15, 23, 42, 0.5);
            color: #f8fafc;
        }

        .chip.success {
            background: rgba(34, 197, 94, 0.15);
            border-color: rgba(34, 197, 94, 0.35);
            color: #dcfce7;
        }

        .chip.primary {
            background: rgba(139, 92, 246, 0.18);
            border-color: rgba(139, 92, 246, 0.35);
            color: #ede9fe;
        }

        .metric-card {
            background: rgba(17, 24, 39, 0.8);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem;
            height: 100%;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 0.3rem;
        }

        .status-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.7rem;
        }

        .status-box strong {
            color: #f8fafc;
        }

        .source-card {
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            background: rgba(15, 23, 42, 0.55);
            margin-bottom: 0.8rem;
        }

        .tiny {
            color: var(--muted);
            font-size: 0.76rem;
        }

        .chat-bubble {
            border-radius: 18px;
        }

        [data-testid="stChatMessage"] {
            padding: 0.25rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_bytes(size_in_bytes: int) -> str:
    if size_in_bytes is None:
        return "0 KB"
    units = ["B", "KB", "MB", "GB"]
    value = float(size_in_bytes)
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    return f"{value:.1f} {units[index]}"


def get_timestamp() -> str:
    return datetime.now().strftime("%I:%M %p")


def render_badges() -> None:
    badge_html = """
    <div class="badge-row">
        <span class="chip success">✅ AI Ready</span>
        <span class="chip primary">✅ Knowledge Base Active</span>
        <span class="chip">✅ PDF Loaded</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)


def render_example_questions() -> None:
    examples = [
        "What is this document about?",
        "Summarize the document.",
        "What are the main findings?",
        "What conclusions were made?",
        "What recommendations are included?",
    ]

    st.caption("Try asking:")
    cols = st.columns(len(examples))
    for col, question in zip(cols, examples):
        if col.button(question, key=f"example_{question}", use_container_width=True):
            st.session_state.pending_prompt = question


def render_quick_actions() -> None:
    actions = {
        "📄 Summarize Document": "Provide a complete summary of this document.",
        "📌 Key Points": "List the key points from this document.",
        "❓ Suggested Questions": "Generate 10 useful questions users can ask about this document.",
        "📋 Extract Important Information": "Extract the most important information, conclusions, and recommendations from this document.",
    }

    for label, prompt in actions.items():
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            st.session_state.pending_prompt = prompt


def add_chat_message(role: str, content: str) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "timestamp": get_timestamp(),
        }
    )


def render_chat_history() -> None:
    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.caption(message["timestamp"])
            st.markdown(message["content"])


def render_sources(sources) -> None:
    if not sources:
        return

    with st.expander("📚 Sources", expanded=False):
        for index, doc in enumerate(sources, start=1):
            meta = getattr(doc, "metadata", {}) or {}
            source_name = meta.get("source", f"Document {index}")
            page_number = meta.get("page")
            preview = doc.page_content[:300].replace("\n", " ")

            st.markdown(f"<div class='source-card'>", unsafe_allow_html=True)
            st.markdown(f"**Source {index}:** {source_name}")
            if page_number is not None:
                st.caption(f"Page: {page_number + 1}")
            else:
                st.caption("Page: Not available")
            st.write(preview)
            st.markdown("</div>", unsafe_allow_html=True)


def process_pdf_with_progress(uploaded_file):
    processing_steps = [
        (0, "Reading PDF..."),
        (25, "Chunking Document..."),
        (50, "Creating Embeddings..."),
        (75, "Building FAISS Index..."),
        (100, "Complete ✅"),
    ]

    progress_bar = st.progress(0, text=processing_steps[0][1])
    status_text = st.empty()

    for percent, message in processing_steps:
        progress_bar.progress(percent, text=message)
        status_text.info(message)
        if percent < 100:
            time.sleep(0.4)

    summary = build_vector_store(uploaded_file)
    progress_bar.progress(100, text="Complete ✅")

    return summary


st.markdown(
    """
    <div class="hero">
        <h1>📚 PDF Intelligence Assistant</h1>
        <p>Upload documents, ask questions, generate summaries, and extract insights using AI-powered Retrieval Augmented Generation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
render_badges()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

if "doc_info" not in st.session_state:
    st.session_state.doc_info = {}

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""

with st.sidebar:
    st.header("📄 Document Workspace")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload a PDF to rebuild the vector store and refresh the RAG pipeline.",
    )

    if uploaded_file is not None:
        st.caption(f"Selected file: {uploaded_file.name}")

    with st.form("process_pdf_form"):
        submitted = st.form_submit_button("Process PDF", type="primary", use_container_width=True)

    if uploaded_file is not None and submitted:
        try:
            summary = process_pdf_with_progress(uploaded_file)
            reset_qa_chain()
            st.session_state.current_pdf = uploaded_file.name
            st.session_state.doc_info = {
                "file_name": uploaded_file.name,
                "file_size": uploaded_file.size,
                "total_pages": summary.get("pages", 0),
                "chunks_created": summary.get("chunks", 0),
                "embedding_model": summary.get("embedding_model", "all-MiniLM-L6-v2"),
                "vector_store_status": "Ready ✅",
            }
            st.session_state.messages = []
            st.success(f"Processed: {uploaded_file.name}. The chatbot is now using the new PDF.")
        except ValueError as exc:
            st.error(f"The PDF could not be processed: {exc}")
            st.session_state.current_pdf = None
            st.session_state.doc_info = {}
        except FileNotFoundError as exc:
            st.error(f"Vector store not found: {exc}")
            st.session_state.current_pdf = None
            st.session_state.doc_info = {}
        except Exception as exc:
            st.error(f"Processing failed. Please upload a valid PDF and try again. Details: {exc}")
            st.session_state.current_pdf = None
            st.session_state.doc_info = {}

    st.divider()

    st.markdown("### System Status")
    st.markdown("<div class='status-box'><strong>LLM Status:</strong> ✅ Ready</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-box'><strong>FAISS Status:</strong> ✅ Ready</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-box'><strong>Embedding Model:</strong> ✅ all-MiniLM-L6-v2</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-box'><strong>Document Loaded:</strong> " + ("✅ Yes" if st.session_state.current_pdf else "⏳ Waiting") + "</div>", unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = ""
        st.rerun()

    if st.session_state.current_pdf:
        st.markdown("### Active PDF")
        st.info(st.session_state.current_pdf)

    st.markdown("---")
    st.caption("Built with Streamlit • LangChain • FAISS • Groq")


if st.session_state.current_pdf is None:
    st.info("Upload a PDF and click Process PDF to build a new knowledge base.")
    render_example_questions()
else:
    doc_info = st.session_state.doc_info
    if doc_info:
        st.subheader("📊 Document Information")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("PDF Name", doc_info.get("file_name", "Unknown"))
        col2.metric("Pages", doc_info.get("total_pages", 0))
        col3.metric("Chunks", doc_info.get("chunks_created", 0))
        col4.metric("Status", "Ready ✅")

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("File Size", format_bytes(doc_info.get("file_size", 0)))
        col6.metric("Model", doc_info.get("embedding_model", "all-MiniLM-L6-v2"))
        col7.metric("Vector Store", doc_info.get("vector_store_status", "Ready ✅"))
        col8.metric("LLM", "Groq")

    render_quick_actions()
    render_example_questions()

render_chat_history()

pending_prompt = st.session_state.pending_prompt
if pending_prompt:
    st.session_state.pending_prompt = ""
    prompt = pending_prompt
else:
    prompt = st.chat_input("Ask a question about the uploaded PDF")

if prompt:
    if st.session_state.current_pdf is None:
        st.warning("Please upload and process a PDF before asking questions.")
    else:
        add_chat_message("user", prompt)
        render_chat_history()

        try:
            result = ask_question(prompt)
            answer = (
                result.get("answer")
                or result.get("result")
                or "I could not find an answer in this PDF."
            )
            sources = result.get("source_documents", [])

            with st.chat_message("assistant", avatar="🤖"):
                st.caption(get_timestamp())
                st.markdown(answer)
                render_sources(sources)

            add_chat_message("assistant", answer)

        except FileNotFoundError:
            with st.chat_message("assistant", avatar="🤖"):
                st.error("The knowledge base is missing. Please reprocess the PDF.")
            add_chat_message("assistant", "The knowledge base is missing. Please reprocess the PDF.")
        except ValueError as exc:
            with st.chat_message("assistant", avatar="🤖"):
                st.error(f"Configuration error: {exc}")
            add_chat_message("assistant", f"Configuration error: {exc}")
        except Exception as exc:
            with st.chat_message("assistant", avatar="🤖"):
                st.error(f"Something went wrong while answering: {exc}")
            add_chat_message("assistant", f"Something went wrong while answering: {exc}")

if not st.session_state.messages and st.session_state.current_pdf is not None:
    st.info("Ask a question to start the conversation.")


