import os
from jira import JIRA


def get_jira_client():
    """
    Returns an authenticated JIRA client using environment variables:
      - JIRA_SERVER_URL
      - JIRA_EMAIL
      - JIRA_API_TOKEN
    """
    server = os.getenv("JIRA_SERVER_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not server or not email or not api_token:
        raise RuntimeError("Please set JIRA_SERVER_URL, JIRA_EMAIL, and JIRA_API_TOKEN in your env.")

    # Instantiate Jira client with server URL and basic auth
    jira = JIRA(server=server, basic_auth=(email, api_token))
    return jira


def fetch_current_sprint_issues(board_id: int):
    """
    Fetch all issues in the current active sprint for a given board,
    including the full changelog.

    Args:
        board_id: Numeric ID of the Scrum board.

    Returns:
        List[jira.resources.Issue]: Issues in the active sprint.
    """
    jira = get_jira_client()
    sprints = jira.sprints(board_id, state="active")
    if not sprints:
        return []
    active_sprint = sprints[0]
    jql = f'sprint = {active_sprint.id}'
    issues = jira.search_issues(jql, maxResults=1000, expand="changelog")
    return issues


def fetch_backlog_issues(project_key: str):
    """
    Fetch all issues in the backlog for a given project (no sprint assigned).

    Args:
        project_key: Key of the Jira project (e.g., "SCRUM").

    Returns:
        List[jira.resources.Issue]: Issues in the backlog.
    """
    jira = get_jira_client()
    # JQL: project matches and sprint is empty and not done
    jql = f'project = "{project_key}" AND sprint IS EMPTY AND statusCategory != Done'
    issues = jira.search_issues(jql, maxResults=1000)
    return issues


def fetch_issue_updates(issue_key: str, days: int = 1):
    """
    Fetch recent changelog updates for a single issue within the last `days`.

    Args:
        issue_key: Jira issue key (e.g., "SCRUM-123").
        days: Number of days in the past to look for updates.

    Returns:
        List[Dict]: Each entry contains issue, author, timestamp, field, from, to.
    """
    jira = get_jira_client()
    issue = jira.issue(issue_key, expand="changelog")
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    updates = []
    for history in issue.changelog.histories:
        when = datetime.strptime(history.created[:-5], "%Y-%m-%dT%H:%M:%S.%f")
        if when >= cutoff:
            for item in history.items:
                updates.append({
                    "issue": issue_key,
                    "author": history.author.displayName,
                    "timestamp": history.created,
                    "field": item.field,
                    "from": item.fromString,
                    "to": item.toString,
                })
    return updates
