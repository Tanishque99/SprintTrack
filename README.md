# 🧠 AI-Powered Jira Assistant

A Streamlit-based dashboard that integrates Jira and OpenAI to deliver AI-driven insights and automation for Agile teams. Features include sprint summaries, natural-language Q&A (with RAG), backlog refinement, release notes, test-case generation, risk analysis, retrospectives, ticket triage, estimation coaching, and onboarding documentation.

---

## 🚀 Features

- **Sprint Summary**: Role-aware (Manager, Scrum Master, Developer, Client) summaries of active sprint progress.
- **Natural-Language Q&A**: Ask free-form questions about Jira data; uses retrieval-augmented generation (RAG) to answer with context.
- **Backlog Refinement**: Suggests acceptance criteria, sub-tasks, and story-point estimates.
- **Release Notes**: Auto-generates polished release notes from completed issues.
- **Test-Case Generation**: Produces outlines for test cases from stories or bugs.
- **Risk & Dependency Analysis**: Highlights blockers and cross-issue dependencies.
- **Retro & Sentiment Summary**: Summarizes retrospective inputs and team sentiment.
- **Ticket Triage & Labeling**: Auto-labels tickets with priority, tags, and suggested assignees.
- **Estimation Coach**: Recommends realistic sprint commitments based on historical data.
- **Onboarding Documentation**: Generates onboarding guides from existing backlog.

---

## 📦 Repository Structure

```
├── app.py                 # Main Streamlit app
├── jira_client.py         # Jira API wrapper
├── data_processing.py     # Issue normalization and summaries
├── llm_client.py          # OpenAI integration
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── .env.example           # Template for environment config
```

---

## ⚙️ Prerequisites

- Python 3.9+
- Jira Cloud account with API access
- OpenAI API key

---

## 🔧 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/ai-jira-assistant.git
   cd ai-jira-assistant
   ```

2. **Set up a virtual environment** (optional)

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:

   ```
   JIRA_SERVER_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=you@yourcompany.com
   JIRA_API_TOKEN=your_jira_api_token
   OPENAI_API_KEY=your_openai_api_key
   ```

---

## 🚀 Usage

Launch the dashboard:

```bash
streamlit run app.py
```

Visit the URL (usually `http://localhost:8501`) in your browser. Use the sidebar to input your role, board ID, project key, and feature selection.

---

## 🧩 Key Modules

### `jira_client.py`

- `get_jira_client()`: Auth via environment
- `fetch_current_sprint_issues(board_id)`
- `fetch_backlog_issues(project_key)`
- `fetch_issue_updates(issue_key, days)`

### `data_processing.py`

- `summarize_sprint_issues(issues)`
- `summarize_backlog_issues(issues)`
- `get_recent_updates(...)`
- `get_issue_updates_for_list(keys, days)`

### `llm_client.py`

- `generate_sprint_summary(...)`
- Other LLM helpers for task-specific prompts

---

