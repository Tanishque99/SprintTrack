import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import openai
import numpy as np
from jira import JIRAError
from jira_client import (
    fetch_current_sprint_issues,
    fetch_backlog_issues,
    fetch_issue_updates
)
from data_processing import (
    summarize_sprint_issues,
    summarize_backlog_issues,
    get_recent_updates,
    get_issue_updates_for_list
)

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit page config must be first
st.set_page_config(page_title="AI-Powered Jira Assistant", layout="wide")
st.title("🚀 AI-Powered Jira Assistant")

# Sidebar settings
with st.sidebar:
    st.header("🔧 Configuration")
    ROLE = st.selectbox("Select Your Role", ["Manager", "Scrum Master", "Developer", "Client"])
    JIRA_USER = st.text_input("Your Jira Identifier (display name/email/accountId)", "")
    BOARD_ID = st.number_input("Jira Board ID", min_value=1, step=1)
    PROJECT_KEY = st.text_input("Jira Project Key (for backlog)", "")
    st.markdown("---")
    feature = st.radio(
        "Choose Feature:", [
            "Sprint Summary",
            "Natural-Language Q&A",
            "Backlog Refinement",
            "Release Notes",
            "Test-Case Generation",
            "Risk & Dependency Analysis",
            "Retro & Sentiment Summary",
            "Ticket Triage & Labeling",
            "Estimation Coach",
            "Onboarding Documentation"
        ]
    )
    run = st.button("Run")

# Utility: embed and retrieval for RAG

def embed_texts(texts):
    resp = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [d['embedding'] for d in resp['data']]


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

# Main execution
if feature == "Natural-Language Q&A":
    question = st.text_input("Ask a question about Jira:")
    if st.button("Ask") and question:
        # Fetch data with error handling
        try:
            issues = fetch_current_sprint_issues(board_id=int(BOARD_ID))
        except JIRAError as e:
            st.error(f"Error fetching sprint issues for board {BOARD_ID}: {e}")
            st.stop()
        sprint_data = summarize_sprint_issues(issues)
        backlog_summary = []
        if PROJECT_KEY:
            try:
                backlog_issues = fetch_backlog_issues(project_key=PROJECT_KEY)
            except JIRAError as e:
                st.error(f"Error fetching backlog for project '{PROJECT_KEY}': {e}")
                st.stop()
            backlog_summary = summarize_backlog_issues(backlog_issues)
        # Build RAG corpus
        corpus = []
        for d in sprint_data:
            corpus.append({"source": d['key'], "text": d['summary']})
        for d in backlog_summary:
            corpus.append({"source": d['key'], "text": d['summary']})
        texts = [c['text'] for c in corpus]
        embeddings = embed_texts(texts)
        for i, emb in enumerate(embeddings):
            corpus[i]['embedding'] = emb
        # Embed question and retrieve top 3
        q_emb = embed_texts([question])[0]
        scores = [cosine_similarity(q_emb, c['embedding']) for c in corpus]
        top_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
        context = "\n".join([
            f"[{corpus[i]['source']}]: {corpus[i]['text']}" for i in top_idxs
        ])
        # LLM prompt
        prompt = (
            f"You are an AI assistant. Use the following context to answer the question.\n"
            f"Context:\n{context}\n"
            f"Question: {question}\n"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500
        )
        st.subheader("Answer")
        st.write(response.choices[0].message.content)

else:
    if run:
        # Fetch common data with error handling
        try:
            issues = fetch_current_sprint_issues(board_id=int(BOARD_ID))
        except JIRAError as e:
            st.error(f"Error fetching sprint issues for board {BOARD_ID}: {e}")
            st.stop()
        sprint_data = summarize_sprint_issues(issues)
        backlog_summary = []
        if PROJECT_KEY:
            try:
                backlog_issues = fetch_backlog_issues(project_key=PROJECT_KEY)
            except JIRAError as e:
                st.error(f"Error fetching backlog for project '{PROJECT_KEY}': {e}")
                st.stop()
            backlog_summary = summarize_backlog_issues(backlog_issues)
        # Recent updates for sprint
        issue_keys = [item['key'] for item in sprint_data]
        recent_updates = get_issue_updates_for_list(issue_keys, days=1)
        # Developer filter
        if ROLE.lower() == "developer":
            sprint_data = [i for i in sprint_data if i.get("assignee") == JIRA_USER]
        # Dispatch other features
        if feature == "Sprint Summary":
            prompt = f"Generate a {ROLE} sprint summary. Issues: {sprint_data}."
        elif feature == "Backlog Refinement":
            if not backlog_summary:
                st.error("Provide a valid project key for backlog refinement.")
                st.stop()
            prompt = f"Given backlog items: {backlog_summary}, suggest acceptance criteria, tasks, and story-point estimates."
        elif feature == "Release Notes":
            prompt = f"Draft release notes for completed sprint issues: {sprint_data}."
        elif feature == "Test-Case Generation":
            prompt = f"Generate test cases for these stories/bugs: {sprint_data}."
        elif feature == "Risk & Dependency Analysis":
            prompt = f"Analyze risks and dependencies in sprint issues: {sprint_data}."
        elif feature == "Retro & Sentiment Summary":
            prompt = f"Summarize retrospective sentiment based on updates: {recent_updates}."
        elif feature == "Ticket Triage & Labeling":
            new_issue = st.text_area("Paste new ticket description:")
            if new_issue:
                triage_prompt = f"Triage this ticket: {new_issue}. Suggest labels, priority, and assignment."
                try:
                    triage_resp = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": triage_prompt}],
                        max_tokens=500
                    )
                    st.subheader("Triage & Labeling")
                    st.write(triage_resp.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error during ticket triage: {e}")
                st.stop()
        elif feature == "Estimation Coach":
            prompt = f"Given past velocity and sprint issues: {sprint_data}, recommend a realistic sprint commitment."
        elif feature == "Onboarding Documentation":
            if not backlog_summary:
                st.error("Provide project key to generate onboarding docs.")
                st.stop()
            prompt = f"Create onboarding docs based on backlog: {backlog_summary}."
        # Call LLM for non-triage
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=600
            )
            st.subheader(feature)
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error during LLM call for {feature}: {e}")
    else:
        st.info("Configure settings, select a feature, then click Run (or Ask for Q&A).")
