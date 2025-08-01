import os
from dotenv import load_dotenv
from github import Github, GithubException

load_dotenv()

def get_github_token(token=None):
    return token or os.getenv('GITHUB_TOKEN')

# Example: get repo data
def get_repo_data(repo_full_name, token=None):
    g = Github(get_github_token(token))
    repo = g.get_repo(repo_full_name)
    return repo

# Get commits
def get_commits(repo_full_name, token=None):
    repo = get_repo_data(repo_full_name, token)
    return list(repo.get_commits())

# Get pull requests
def get_pull_requests(repo_full_name, token=None, state='all'):
    repo = get_repo_data(repo_full_name, token)
    return list(repo.get_pulls(state=state))

# Get contributors
def get_contributors(repo_full_name, token=None):
    repo = get_repo_data(repo_full_name, token)
    return list(repo.get_contributors())

def get_user_data(username, token=None):
    g = Github(get_github_token(token))
    try:
        user = g.get_user(username)
        return user
    except GithubException as e:
        return {'error': str(e), 'status': getattr(e, 'status', None)}

# Get user events (commits, PRs, issues)
def get_user_events(username, token=None):
    user = get_user_data(username, token)
    if user is None or isinstance(user, dict):
        return [], user if isinstance(user, dict) else None
    return list(user.get_events()), None

# Get user repositories
def get_user_repos(username, token=None):
    user = get_user_data(username, token)
    if user is None or isinstance(user, dict):
        return [], user if isinstance(user, dict) else None
    return list(user.get_repos()), None

# Get user PRs across repos
def get_user_prs(username, token=None):
    repos, error = get_user_repos(username, token)
    if error:
        return [], error
    prs = []
    for repo in repos:
        try:
            prs.extend(list(repo.get_pulls(state='all')))
        except Exception:
            continue
    return prs, None

# Get user commits across repos
def get_user_commits(username, token=None):
    repos, error = get_user_repos(username, token)
    if error:
        return [], error
    commits = []
    for repo in repos:
        try:
            commits.extend(list(repo.get_commits(author=username)))
        except Exception:
            continue
    return commits, None
