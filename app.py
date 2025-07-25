import streamlit as st
from transformers import pipeline
import os
from PyPDF2 import PdfReader
from datetime import date

st.set_page_config(page_title="Indian Legal AI Agent", layout="wide")

# Load summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Helper: summarize long text
def summarize_text(text):
    max_chunk = 1024
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    summary = " ".join([
        summarizer(chunk, max_length=120, min_length=30, do_sample=False)[0]["summary_text"]
        for chunk in chunks
    ])
    return summary

# Helper: read PDF
def read_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

# -----------------------------------
# Streamlit UI
st.title("⚖️ Indian Legal AI Agent")
tabs = st.tabs(["📑 Draft Contract", "🕵️ Review Contract", "📚 Summarize Judgment"])

# -----------------------------------
# TAB 1: Generate Contract
with tabs[0]:
    st.subheader("📄 Draft a Legal Contract")

    contract_type = st.selectbox("Choose contract type", ["NDA", "Rent Agreement"])
    party1 = st.text_input("Party 1 Name")
    party2 = st.text_input("Party 2 Name")
    location = st.text_input("Location")
    start_date = st.date_input("Start Date", value=date.today())
    duration = st.number_input("Duration (months)", min_value=1, max_value=60, value=12)

    if st.button("Generate Contract"):
        if contract_type == "NDA":
            contract = f"""
NON-DISCLOSURE AGREEMENT (NDA)

This Agreement is made between {party1} and {party2}, located in {location}, effective from {start_date} for a period of {duration} months.

The parties agree not to disclose confidential information. This agreement governs all disclosures, usage, and legal remedies in case of breach.

[Signature: {party1}] [Signature: {party2}]
"""
        else:
            contract = f"""
RENTAL AGREEMENT

This Agreement is made between Landlord {party1} and Tenant {party2}, for the property located in {location}, starting from {start_date} for a duration of {duration} months.

Rent and other conditions will be governed as per Indian Rental Act.

[Landlord: {party1}] [Tenant: {party2}]
"""
        st.text_area("📄 Generated Contract", contract, height=300)

# -----------------------------------
# TAB 2: Review Uploaded Contract
with tabs[1]:
    st.subheader("📋 Upload Contract for Clause Review")
    uploaded_file = st.file_uploader("Upload .txt or .pdf contract", type=["txt", "pdf"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        else:
            text = uploaded_file.read().decode("utf-8")

        st.text_area("📄 Uploaded Contract Text", text, height=300)

        if st.button("Review Missing Clauses"):
            expected_clauses = ["confidentiality", "termination", "governing law", "dispute resolution"]
            missing = []
            lower_text = text.lower()
            for clause in expected_clauses:
                if clause not in lower_text:
                    missing.append(clause)
            if missing:
                st.warning(f"⚠️ Missing clauses: {', '.join(missing)}")
            else:
                st.success("✅ All standard clauses are present.")

# -----------------------------------
# TAB 3: Summarize Judgment
with tabs[2]:
    st.subheader("📚 Summarize Indian Court Judgment")
    uploaded = st.file_uploader("Upload Judgment File (.txt or .pdf)", type=["txt", "pdf"])

    if uploaded:
        if uploaded.type == "application/pdf":
            text = read_pdf(uploaded)
        else:
            text = uploaded.read().decode("utf-8")

        st.text_area("📄 Judgment Text", text[:2000], height=300)

        if st.button("Summarize"):
            with st.spinner("Summarizing..."):
                summary = summarize_text(text)
            st.success("Summary generated below:")
            st.text_area("📑 Summary", summary, height=300)
