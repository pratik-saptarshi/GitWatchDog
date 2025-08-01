from gitwatchdog.github_api import get_commits, get_pull_requests, get_contributors

def test_github_api():
    # Example test: check API returns lists
    commits = get_commits('octocat/Hello-World')
    prs = get_pull_requests('octocat/Hello-World')
    contributors = get_contributors('octocat/Hello-World')
    assert isinstance(commits, list)
    assert isinstance(prs, list)
    assert isinstance(contributors, list)
