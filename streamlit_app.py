import os
import hashlib
import logging
import re
import time
import shutil
import streamlit as st

from retriever import get_retriever
from agents import (
    answer_question,
    general_answer,
    summarize_document
)
from router import route_question
from create_vector_db import create_vector_db

logger = logging.getLogger(__name__)

# ---------------- Page Configuration ----------------

st.set_page_config(
    page_title="Inquiro | Multi-Agent Research Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- High-End Aesthetic & Custom CSS ----------------

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Obsidian Aurora Radial Canvas */
.stApp {
    background-color: #07090e;
    background-image:
        radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.18) 0px, transparent 50%),
        radial-gradient(at 95% 15%, rgba(79, 70, 229, 0.12) 0px, transparent 45%),
        radial-gradient(at 50% 90%, rgba(14, 116, 144, 0.08) 0px, transparent 50%),
        linear-gradient(180deg, #090d16 0%, #05070b 100%);
    background-attachment: fixed;
    color: #f1f5f9;
}

/* Frosted Glass Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(9, 13, 22, 0.75) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

/* Main Hero Banner */
.inquiro-hero {
    padding: 1.5rem 0 1.2rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    display: flex;
    align-items: center;
    gap: 1.25rem;
}
.inquiro-hero-text h1 {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.035em;
    background: linear-gradient(135deg, #ffffff 40%, #cbd5e1 75%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.15;
}
.inquiro-hero-text p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.35rem;
    font-weight: 400;
    letter-spacing: -0.01em;
}

/* Agent Routing Badges */
.agent-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.pill-rag {
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.25);
}
.pill-general {
    background: rgba(59, 130, 246, 0.1);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.25);
}
.pill-summary {
    background: rgba(245, 158, 11, 0.1);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.25);
}

/* Citation Block Styling */
.citation-card {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 11px 16px;
    margin: 8px 0;
    font-size: 0.88rem;
    color: #cbd5e1;
    transition: all 0.2s ease;
}
.citation-card:hover {
    border-color: rgba(99, 102, 241, 0.45);
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-1px);
}
.citation-num {
    display: inline-block;
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    color: white;
    font-weight: 700;
    font-size: 0.72rem;
    padding: 2px 7px;
    border-radius: 4px;
    margin-right: 8px;
}

/* Full Width Retrieved Document Passage Container */
.passage-box {
    width: 100% !important;
    box-sizing: border-box !important;
    background: rgba(0, 0, 0, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    color: #e2e8f0 !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
    letter-spacing: -0.01em !important;
    white-space: normal !important;
    word-break: break-word !important;
    margin-bottom: 1rem !important;
}

/* Sidebar Specs */
.metric-badge {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 12px;
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    margin-bottom: 7px;
    font-size: 0.82rem;
    color: #94a3b8;
}
.metric-val {
    color: #38bdf8;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}

/* Input & Chat Containers */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 14px !important;
    margin-bottom: 14px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.25);
}
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: rgba(13, 19, 31, 0.85) !important;
    backdrop-filter: blur(16px) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(99, 102, 241, 0.5) !important;
    box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.25);
}
</style>""", unsafe_allow_html=True)

# ---------------- Custom Inquiro Vector Mark ----------------

LOGO_SVG_SIDEBAR = (
    '<svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect width="36" height="36" rx="9" fill="url(#inq-grad-sb)" />'
    '<circle cx="18" cy="18" r="9" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="2 3"/>'
    '<polygon points="18,10 21,18 18,26 15,18" fill="#ffffff"/>'
    '<circle cx="18" cy="18" r="2.2" fill="#38BDF8"/>'
    '<defs>'
    '<linearGradient id="inq-grad-sb" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">'
    '<stop stop-color="#4F46E5"/>'
    '<stop offset="0.6" stop-color="#0284C7"/>'
    '<stop offset="1" stop-color="#06B6D4"/>'
    '</linearGradient>'
    '</defs>'
    '</svg>'
)

LOGO_SVG_HERO = (
    '<svg width="44" height="44" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect width="36" height="36" rx="10" fill="url(#inq-grad-hr)" />'
    '<circle cx="18" cy="18" r="9" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="2 3"/>'
    '<polygon points="18,10 21,18 18,26 15,18" fill="#ffffff"/>'
    '<circle cx="18" cy="18" r="2.2" fill="#38BDF8"/>'
    '<defs>'
    '<linearGradient id="inq-grad-hr" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">'
    '<stop stop-color="#4F46E5"/>'
    '<stop offset="0.6" stop-color="#0284C7"/>'
    '<stop offset="1" stop-color="#06B6D4"/>'
    '</linearGradient>'
    '</defs>'
    '</svg>'
)


def get_full_document_text():
    from langchain_community.document_loaders import PyPDFLoader
    text = ""
    if os.path.exists("data"):
        for file in sorted(os.listdir("data")):
            if file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join("data", file))
                pages = loader.load()
                for page in pages:
                    text += page.page_content + "\n\n"
    return text


def build_retrieval_context(results):
    context_parts = []
    references = []
    reference_map = {}

    for doc, score in results:
        filename = os.path.basename(doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page", 0) + 1
        key = (filename, page)

        if key not in reference_map:
            reference_map[key] = len(references) + 1
            references.append((reference_map[key], filename, page))

        source_number = reference_map[key]
        context_parts.append(
            f"[Source {source_number}]\n{doc.page_content.strip()}"
        )
        logger.debug(
            "Retrieved source=%s page=%d score=%.4f",
            filename,
            page,
            score,
        )

    return "\n\n".join(context_parts), references


def clean_chunk_text(text: str) -> str:
    """Removes single line breaks from multi-column PDFs while preserving paragraphs."""
    # Replace hyphenated line breaks (e.g., 'algo-\nrithm' -> 'algorithm')
    cleaned = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Convert single newlines inside sentences to spaces
    cleaned = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned)
    return cleaned.strip()


def show_general_answer(question):
    with st.chat_message("assistant", avatar="🧭"):
        status = st.empty()
        status.markdown('<span style="color: #94a3b8; font-size:0.9rem;">⚡ Consulting Foundation Model...</span>', unsafe_allow_html=True)

        start = time.time()
        answer = general_answer(question)
        elapsed = time.time() - start

        status.empty()
        st.markdown('<div class="agent-pill pill-general">🌐 General Knowledge Agent</div>', unsafe_allow_html=True)

        placeholder = st.empty()
        text = ""
        for word in answer.split():
            text += word + " "
            placeholder.markdown(text + "▌")
            time.sleep(0.007)

        placeholder.markdown(text)
        st.caption(f"⚡ Latency: `{elapsed:.2f}s` | Engine: Foundation LLM")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "type": "GENERAL",
        "latency": f"{elapsed:.2f}s"
    })


# ---------------- State Initialization ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever" not in st.session_state:
    try:
        st.session_state.retriever = get_retriever()
    except (FileNotFoundError, RuntimeError, ValueError):
        st.session_state.retriever = None


# ---------------- Sidebar Navigation ----------------

with st.sidebar:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:1.6rem; padding-bottom:1rem; border-bottom:1px solid rgba(255,255,255,0.06);">'
        f'{LOGO_SVG_SIDEBAR}'
        f'<div>'
        f'<h3 style="margin:0; font-size:1.15rem; font-weight:700; color:#fff; letter-spacing:-0.02em;">Inquiro</h3>'
        f'<p style="margin:0; font-size:0.75rem; color:#64748b;">Multi-Agent Research Assistant</p>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<p style='font-size:0.8rem; font-weight:600; text-transform:uppercase; color:#64748b; margin-bottom:6px;'>Knowledge Base</p>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload research literature (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        os.makedirs("data", exist_ok=True)
        upload_signature = tuple(
            sorted(
                (file.name, hashlib.sha256(file.getvalue()).hexdigest())
                for file in uploaded_files
            )
        )

        if upload_signature != st.session_state.get("upload_signature"):
            for file in uploaded_files:
                with open(os.path.join("data", file.name), "wb") as output_file:
                    output_file.write(file.getbuffer())

            try:
                with st.spinner("Indexing vector embeddings into FAISS..."):
                    create_vector_db("data")

                st.session_state.retriever = get_retriever()
                st.session_state.upload_signature = upload_signature
                st.toast("Corpus indexed into Inquiro memory", icon="✅")
            except (OSError, ValueError, RuntimeError) as error:
                st.error(f"Vectorization failed: {error}")

    # Active Documents Counter
    if os.path.exists("data") and any(f.endswith(".pdf") for f in os.listdir("data")):
        pdf_count = len([f for f in os.listdir("data") if f.endswith(".pdf")])
        st.markdown(
            f'<div class="metric-badge">'
            f'<span>Active Papers</span>'
            f'<span class="metric-val">{pdf_count} Ingested</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Purge DB", use_container_width=True):
            if os.path.exists("data"):
                for file in os.listdir("data"):
                    if file.endswith(".pdf"):
                        os.remove(os.path.join("data", file))
            if os.path.exists("vectorstore"):
                shutil.rmtree("vectorstore")
            st.session_state.retriever = None
            st.session_state.upload_signature = None
            st.rerun()

    with col_btn2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='font-size:0.8rem; font-weight:600; text-transform:uppercase; color:#64748b;'>Engine Specifications</p>", unsafe_allow_html=True)

    st.markdown(
        '<div class="metric-badge"><span>Architecture</span><span class="metric-val">Router + RAG Swarm</span></div>'
        '<div class="metric-badge"><span>Vector Store</span><span class="metric-val">FAISS / Dense Index</span></div>'
        '<div class="metric-badge"><span>Grounded Verification</span><span class="metric-val">Active</span></div>'
        '<div class="metric-badge"><span>Citation Tracking</span><span class="metric-val">Exact Page Map</span></div>',
        unsafe_allow_html=True
    )


# ---------------- Main Stage Header ----------------

st.markdown(
    f'<div class="inquiro-hero">'
    f'{LOGO_SVG_HERO}'
    f'<div class="inquiro-hero-text">'
    f'<h1>Inquiro</h1>'
    f'<p>An AI-Powered Multi-Agent Research Assistant.</p>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)


# Render Past Chat Messages
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🧭"
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("type") == "RAG":
            st.markdown('<div class="agent-pill pill-rag">🔬 Document RAG Agent</div>', unsafe_allow_html=True)
        elif message.get("type") == "GENERAL":
            st.markdown('<div class="agent-pill pill-general">🌐 General Knowledge Agent</div>', unsafe_allow_html=True)
        elif message.get("type") == "SUMMARY":
            st.markdown('<div class="agent-pill pill-summary">📑 Synthesis Agent</div>', unsafe_allow_html=True)

        st.markdown(message["content"])

        if "latency" in message:
            st.caption(f"⚡ Latency: `{message['latency']}`")


# ---------------- Chat Input & Inference Pipeline ----------------

question = st.chat_input("Ask a question about the papers, general knowledge, or type 'summarize'...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    has_documents = (
        st.session_state.retriever is not None
        and os.path.exists("data")
        and any(file.lower().endswith(".pdf") for file in os.listdir("data"))
    )
    route = route_question(question, has_documents=has_documents)
    logger.info("Selected agent route=%s has_documents=%s", route, has_documents)

    # 1. SUMMARY ROUTE
    if route == "SUMMARY":
        if not os.path.exists("data") or not any(file.endswith(".pdf") for file in os.listdir("data")):
            st.error("Please upload PDF files first before requesting a synthesis.")
            st.stop()

        with st.chat_message("assistant", avatar="🧭"):
            status = st.empty()
            status.markdown('<span style="color: #94a3b8; font-size:0.9rem;">📑 Reading corpus and synthesizing paper summary...</span>', unsafe_allow_html=True)

            start = time.time()
            try:
                full_text = get_full_document_text()
                answer = summarize_document(full_text)
            except (OSError, ValueError, RuntimeError) as error:
                logger.exception("Document summarization failed")
                status.empty()
                st.error(f"Summarization pipeline error: {error}")
                st.stop()

            elapsed = time.time() - start
            status.empty()

            st.markdown('<div class="agent-pill pill-summary">📑 Synthesis Agent</div>', unsafe_allow_html=True)
            st.markdown(answer)
            st.caption(f"⚡ Latency: `{elapsed:.2f}s` | Scope: Complete Document Corpus")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "type": "SUMMARY",
            "latency": f"{elapsed:.2f}s"
        })

    # 2. GENERAL ROUTE
    elif route == "GENERAL":
        show_general_answer(question)

    # 3. RAG ROUTE
    elif route == "RAG":
        retriever = st.session_state.retriever

        if retriever is None:
            st.error("Vector database is uninitialized. Upload a paper first.")
            st.stop()

        try:
            results = retriever.similarity_search_with_score(question, k=3)
        except (RuntimeError, ValueError) as error:
            logger.exception("FAISS retrieval failed")
            st.error(f"Retrieval error: {error}")
            st.stop()

        if not results:
            st.warning("No relevant passages matching your query criteria were found.")
            st.stop()

        best_score = results[0][1]
        THRESHOLD = 1.2

        if best_score > THRESHOLD:
            st.info("The uploaded papers lack sufficient context to ground this query accurately.")
            st.stop()

        docs = [doc for doc, score in results]
        context, references = build_retrieval_context(results)

        with st.chat_message("assistant", avatar="🧭"):
            status = st.empty()
            status.markdown('<span style="color: #94a3b8; font-size:0.9rem;">🔍 Inspecting vector chunks & synthesizing grounded answer...</span>', unsafe_allow_html=True)

            start = time.time()
            answer = answer_question(question, context)
            elapsed = time.time() - start
            status.empty()

            st.markdown('<div class="agent-pill pill-rag">🔬 Document RAG Agent</div>', unsafe_allow_html=True)

            placeholder = st.empty()
            text = ""
            for word in answer.split():
                text += word + " "
                placeholder.markdown(text + "▌")
                time.sleep(0.007)

            placeholder.markdown(text)

            used = sorted(set(int(x) for x in re.findall(r"\[(\d+)\]", answer)))

            if used:
                st.markdown("<div style='margin-top: 1.2rem; font-size: 0.85rem; font-weight:700; color:#94a3b8; text-transform:uppercase;'>Verified Citations</div>", unsafe_allow_html=True)
                for number, filename, page in references:
                    if number in used:
                        st.markdown(
                            f'<div class="citation-card">'
                            f'<span class="citation-num">[{number}]</span>'
                            f'<b>{filename}</b> &mdash; <span style="color:#94a3b8;">Page {page}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

            with st.expander("🔎 View Retrieved Document Passages"):
                for i, doc in enumerate(docs, 1):
                    filename = os.path.basename(doc.metadata.get("source", "Unknown"))
                    page = doc.metadata.get("page", 0) + 1
                    cleaned_content = clean_chunk_text(doc.page_content)

                    st.markdown(f"**Chunk #{i}: `{filename}` (Page {page})**")
                    st.markdown(
                        f'<div class="passage-box">{cleaned_content}</div>',
                        unsafe_allow_html=True
                    )

            st.caption(f"⚡ Latency: `{elapsed:.2f}s` | Semantic Similarity Threshold: `Passed`")

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "type": "RAG",
            "latency": f"{elapsed:.2f}s"
        })