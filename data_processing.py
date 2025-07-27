from datetime import datetime, timedelta
from jira_client import fetch_issue_updates


def summarize_sprint_issues(issues):
    """
    Summarize a list of sprint issues into key fields.

    Args:
        issues (List[jira.resources.Issue]): Issues fetched with changelog expanded.

    Returns:
        List[Dict]: Each dict contains key, summary, status, assignee, story_points, labels, updated.
    """
    sprint_summary = []
    for issue in issues:
        f = issue.fields
        sprint_summary.append({
            "key": issue.key,
            "summary": f.summary,
            "status": f.status.name,
            "assignee": f.assignee.displayName if f.assignee else "Unassigned",
            # Adjust this custom field ID for story points if different
            "story_points": getattr(f, "customfield_10002", None),
            "labels": list(f.labels) if f.labels else [],
            "updated": f.updated,
        })
    return sprint_summary


def summarize_backlog_issues(issues):
    """
    Summarize backlog issues (not yet assigned to a sprint).

    Args:
        issues (List[jira.resources.Issue]): Issues in the backlog.

    Returns:
        List[Dict]: Each dict contains key, summary, priority, reporter, labels, created.
    """
    backlog_summary = []
    for issue in issues:
        f = issue.fields
        backlog_summary.append({
            "key": issue.key,
            "summary": f.summary,
            "priority": f.priority.name if f.priority else None,
            "reporter": f.reporter.displayName if f.reporter else None,
            "story_points": getattr(f, "customfield_10002", None),
            "labels": list(f.labels) if f.labels else [],
            "created": f.created,
        })
    return backlog_summary


def get_recent_updates(issues, days=1):
    """
    Extract recent changelog entries for issues already fetched with changelog.

    Args:
        issues (List[jira.resources.Issue]): Issues with `.changelog` attribute.
        days (int): Number of days to look back for updates.

    Returns:
        List[Dict]: Each dict contains issue, author, timestamp, field, from, to.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent_updates = []

    for issue in issues:
        for history in issue.changelog.histories:
            when = datetime.strptime(history.created[:-5], "%Y-%m-%dT%H:%M:%S.%f")
            if when >= cutoff:
                for item in history.items:
                    if item.field in ("status", "comment"):
                        recent_updates.append({
                            "issue": issue.key,
                            "author": history.author.displayName,
                            "timestamp": history.created,
                            "field": item.field,
                            "from": item.fromString,
                            "to": item.toString,
                        })
    return recent_updates


def get_issue_updates_for_list(issue_keys, days=1):
    """
    Fetch recent changelog updates for a list of issue keys by calling fetch_issue_updates.

    Args:
        issue_keys (List[str]): List of issue keys (e.g., ["SCRUM-123"]).
        days (int): Number of days to look back for updates.

    Returns:
        List[Dict]: Aggregated updates for all provided issues.
    """
    updates = []
    for key in issue_keys:
        updates.extend(fetch_issue_updates(issue_key=key, days=days))
    return updates
