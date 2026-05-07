"""Streamlit frontend for the HR Document Assistant."""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("APP_API_KEY", "")


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def _api(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{BACKEND_URL}{path}"
    return requests.request(method, url, headers=_headers(), timeout=120, **kwargs)


# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon=":robot_face:",
    layout="centered",
)
st.title("HR Policy Assistant Chatbot")

# ── Sidebar: Status ─────────────────────────────────────────────────
with st.sidebar:
    st.header("System Status")
    try:
        resp = _api("GET", "/health")
        health = resp.json()
        st.success(f"Backend: {health['status']}")
        if health.get("vector_store_ready"):
            st.info("Vector store: Ready")
        else:
            st.warning("Vector store: No documents ingested")
    except requests.ConnectionError:
        st.error("Backend unreachable")

# ── Upload ───────────────────────────────────────────────────────────
st.subheader("1. Upload an HR Policy Document")
uploaded_file = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"],
    key="file_uploader",
)

if uploaded_file is not None:
    if st.button("Upload & Ingest Document"):
        with st.spinner("Uploading..."):
            try:
                upload_resp = _api(
                    "POST",
                    "/upload",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                )
                upload_resp.raise_for_status()
                upload_data = upload_resp.json()
                st.success(f"Uploaded: {upload_data['filename']}")
            except requests.HTTPError as e:
                st.error(f"Upload failed: {e.response.text}")
                st.stop()
            except requests.ConnectionError:
                st.error("Cannot reach backend. Is it running?")
                st.stop()

        with st.spinner("Ingesting document into vector store..."):
            try:
                ingest_resp = _api(
                    "POST",
                    "/ingest",
                    params={"file_path": upload_data["file_path"]},
                )
                ingest_resp.raise_for_status()
                ingest_data = ingest_resp.json()
                st.success(f"Ingested: {ingest_data['message']}")
            except requests.HTTPError as e:
                st.error(f"Ingestion failed: {e.response.text}")
            except requests.ConnectionError:
                st.error("Cannot reach backend. Is it running?")

# ── Q&A ──────────────────────────────────────────────────────────────
st.subheader("2. Ask a Question")
question = st.text_input("Enter your question about HR policies", key="question_input")

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Getting answer..."):
            try:
                resp = _api("POST", "/ask", json={"question": question})
                resp.raise_for_status()
                data = resp.json()
                st.markdown(f"**Answer:** {data['answer']}")

                if data.get("sources"):
                    with st.expander("Sources"):
                        for src in data["sources"]:
                            st.markdown(f"- **Page {src['page']}**: {src['snippet'][:150]}...")
            except requests.HTTPError as e:
                error_detail = e.response.json().get("detail", e.response.text)
                if e.response.status_code == 400:
                    st.warning(error_detail)
                else:
                    st.error(f"Error: {error_detail}")
            except requests.ConnectionError:
                st.error("Cannot reach backend. Is it running?")
