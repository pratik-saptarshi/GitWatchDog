from .github_api import get_commits, get_pull_requests, get_contributors, get_user_commits, get_user_prs, get_user_repos
from collections import Counter, defaultdict
from datetime import datetime, timezone
import pandas as pd

def detect_code_staleness(commits):
    # Map file/module to last commit date
    file_last_commit = defaultdict(lambda: None)
    for c in commits:
        files = c.files if hasattr(c, 'files') else []
        commit_date = c.commit.author.date
        if commit_date.tzinfo is None:
            commit_date = commit_date.replace(tzinfo=timezone.utc)
        for f in files:
            fname = f.filename if hasattr(f, 'filename') else str(f)
            if file_last_commit[fname] is None or commit_date > file_last_commit[fname]:
                file_last_commit[fname] = commit_date
    # Calculate staleness (days since last commit)
    now = datetime.now(timezone.utc)
    staleness = {fname: (now - last_date).days for fname, last_date in file_last_commit.items() if last_date}
    # Flag files/modules with high staleness
    stale_files = {fname: days for fname, days in staleness.items() if days > 30}  # e.g., >30 days
    return stale_files, staleness

def analyze_race_conditions(commits, prs):
    # Detect overlapping PRs and frequent edits to shared files
    # Step 1: Find files changed in each PR
    pr_files = {}
    for pr in prs:
        try:
            pr_files[pr.number] = set(f.filename for f in pr.get_files())
        except Exception:
            pr_files[pr.number] = set()
    # Step 2: Find PRs with overlapping files and time windows
    race_risk = {}
    for pr1 in prs:
        for pr2 in prs:
            if pr1.number >= pr2.number:
                continue
            # Check for file overlap
            overlap = pr_files[pr1.number] & pr_files[pr2.number]
            if overlap:
                # Check for overlapping open times
                open1, close1 = pr1.created_at, pr1.closed_at or pr1.updated_at
                open2, close2 = pr2.created_at, pr2.closed_at or pr2.updated_at
                if (open1 <= close2 and open2 <= close1):
                    for f in overlap:
                        race_risk[f] = race_risk.get(f, 0) + 1
    # Step 3: Frequent edits to shared files (from commits)
    file_edit_counts = {}
    for c in commits:
        files = c.files if hasattr(c, 'files') else []
        for f in files:
            fname = f.filename if hasattr(f, 'filename') else str(f)
            file_edit_counts[fname] = file_edit_counts.get(fname, 0) + 1
    # Combine risk scores
    for f, count in file_edit_counts.items():
        race_risk[f] = race_risk.get(f, 0) + count // 10  # weight frequent edits
    # Return top race risk hotspots
    top_race_risk = dict(sorted(race_risk.items(), key=lambda x: x[1], reverse=True)[:20])
    return top_race_risk

def analyze_ownership(commits, contributors):
    # Track file/module ownership, bus factor, orphaned files, contributor reliability
    file_owners = {}
    file_contribs = {}
    for c in commits:
        author = c.commit.author.name if hasattr(c.commit.author, 'name') else 'unknown'
        files = c.files if hasattr(c, 'files') else []
        for f in files:
            fname = f.filename if hasattr(f, 'filename') else str(f)
            file_contribs.setdefault(fname, set()).add(author)
            file_owners[fname] = file_owners.get(fname, {})
            file_owners[fname][author] = file_owners[fname].get(author, 0) + 1
    # Bus factor: number of unique contributors per file
    bus_factor = {fname: len(contribs) for fname, contribs in file_contribs.items()}
    # Orphaned files: files with no commits in last 90 days
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    orphaned_files = []
    for fname, owners in file_owners.items():
        last_commit = max([c.commit.author.date for c in commits if any(f.filename == fname for f in c.files)], default=None)
        if last_commit and (now - (last_commit.replace(tzinfo=timezone.utc) if last_commit.tzinfo is None else last_commit)).days > 90:
            orphaned_files.append(fname)
    # Contributor reliability: ratio of bug-fix commits to total commits
    reliability = {}
    for c in commits:
        author = c.commit.author.name if hasattr(c.commit.author, 'name') else 'unknown'
        msg = c.commit.message.lower()
        is_bugfix = any(kw in msg for kw in ['fix', 'bug', 'patch', 'error'])
        reliability.setdefault(author, {'total': 0, 'bugfix': 0})
        reliability[author]['total'] += 1
        if is_bugfix:
            reliability[author]['bugfix'] += 1
    reliability_score = {a: (v['bugfix'] / v['total'] if v['total'] else 0) for a, v in reliability.items()}
    return {
        'file_owners': file_owners,
        'bus_factor': bus_factor,
        'orphaned_files': orphaned_files,
        'reliability_score': reliability_score,
    }

def temporal_risk_prediction(trend_data):
    # Forecast future staleness/risk using simple time series (moving average)
    pr_trend = trend_data.get('pr_trend', {})
    commit_trend = trend_data.get('commit_trend', {})
    # Use last 6 months for prediction
    months = sorted(pr_trend.keys())[-6:]
    pr_counts = [pr_trend[m] for m in months]
    if pr_counts:
        avg = sum(pr_counts) / len(pr_counts)
        next_month_pred = avg  # naive prediction
    else:
        next_month_pred = 0
    # Predict risk for each file/module (stub: use staleness as proxy)
    predicted_risk = {}
    # If staleness available, use it
    staleness = trend_data.get('staleness', {})
    for fname, days in staleness.items():
        predicted_risk[fname] = days + (30 if next_month_pred < 1 else 0)
    return predicted_risk

def generate_risk_report(results):
    # Summarize staleness, race risk, ownership gaps, anomalies
    report = []
    # Staleness summary
    stale_files = results.get('stale_files', {})
    if stale_files:
        report.append(f"Stale modules (>30 days inactivity): {len(stale_files)}")
        for fname, days in list(stale_files.items())[:10]:
            report.append(f"  - {fname}: {days} days")
    # Race risk summary
    race_risk = results.get('race_risk', {})
    if race_risk:
        report.append(f"Race risk hotspots: {len(race_risk)} files/modules")
        for fname, score in list(race_risk.items())[:10]:
            report.append(f"  - {fname}: risk score {score}")
    # Ownership gaps
    ownership = results.get('ownership', {})
    orphaned = ownership.get('orphaned_files', []) if ownership else []
    if orphaned:
        report.append(f"Orphaned files (no commits in last 90 days): {len(orphaned)}")
        for fname in orphaned[:10]:
            report.append(f"  - {fname}")
    # Anomalies
    drops = results.get('drops', [])
    if drops:
        report.append(f"Activity drops detected in: {', '.join(drops)}")
    # Reliability
    reliability = ownership.get('reliability_score', {}) if ownership else {}
    if reliability:
        top_reliable = sorted(reliability.items(), key=lambda x: x[1], reverse=True)[:5]
        report.append("Top reliable contributors (bugfix ratio):")
        for name, score in top_reliable:
            report.append(f"  - {name}: {score:.2f}")
    # Prediction
    prediction = results.get('risk_prediction', {})
    if prediction:
        report.append("Temporal risk prediction (sample):")
        for fname, pred in list(prediction.items())[:5]:
            report.append(f"  - {fname}: predicted risk {pred}")
    return '\n'.join(report)

def analyze_repo(repo_full_name, token=None):
    commits = get_commits(repo_full_name, token)
    prs = get_pull_requests(repo_full_name, token)
    contributors = get_contributors(repo_full_name, token)

    # PRs per month
    pr_months = [pr.created_at.strftime('%Y-%m') for pr in prs]
    pr_trend = Counter(pr_months)

    # Response times
    response_times = []
    for pr in prs:
        if pr.closed_at:
            delta = pr.closed_at - pr.created_at
            response_times.append(delta.total_seconds() / 3600)  # hours
    avg_response = sum(response_times) / len(response_times) if response_times else None

    # Top contributors
    contrib_counts = {c.login: c.contributions for c in contributors}
    top_contribs = sorted(contrib_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Anomaly detection (simple drop in PRs)
    months = sorted(pr_trend.keys())
    drops = []
    for i in range(1, len(months)):
        if pr_trend[months[i]] < pr_trend[months[i-1]] * 0.5:
            drops.append(months[i])

    # Commit activity per month
    commit_months = [c.commit.author.date.strftime('%Y-%m') for c in commits]
    commit_trend = Counter(commit_months)

    # Code staleness detection
    stale_files, staleness = detect_code_staleness(commits)
    race_risk = analyze_race_conditions(commits, prs)
    ownership_metrics = analyze_ownership(commits, contributors)
    risk_prediction = temporal_risk_prediction({'pr_trend': pr_trend, 'commit_trend': commit_trend})
    risk_report = generate_risk_report({
        'staleness': staleness,
        'race_risk': race_risk,
        'ownership': ownership_metrics,
        'prediction': risk_prediction,
        'drops': drops,
    })
    results = {
        'pr_trend': pr_trend,
        'avg_response': avg_response,
        'top_contribs': top_contribs,
        'drops': drops,
        'total_commits': len(commits),
        'total_prs': len(prs),
        'response_times': response_times,
        'commit_trend': commit_trend,
        'stale_files': stale_files,
        'staleness': staleness,
        'race_risk': race_risk,
        'ownership': ownership_metrics,
        'risk_prediction': risk_prediction,
        'risk_report': risk_report,
    }
    return results

def analyze_user(username, token=None):
    commits, commit_error = get_user_commits(username, token)
    prs, pr_error = get_user_prs(username, token)
    repos, repo_error = get_user_repos(username, token)
    if commit_error or pr_error or repo_error:
        return {'error': commit_error or pr_error or repo_error}

    # PRs per month
    pr_months = [pr.created_at.strftime('%Y-%m') for pr in prs]
    pr_trend = Counter(pr_months)

    # Commit activity per month
    commit_months = [c.commit.author.date.strftime('%Y-%m') for c in commits]
    commit_trend = Counter(commit_months)

    # Top repos contributed to
    repo_counts = Counter([pr.base.repo.name for pr in prs])
    top_repos = repo_counts.most_common(5)

    # Response times (if user is repo owner)
    response_times = []
    for pr in prs:
        if pr.closed_at and pr.user.login == username:
            delta = pr.closed_at - pr.created_at
            response_times.append(delta.total_seconds() / 3600)
    avg_response = sum(response_times) / len(response_times) if response_times else None

    # Anomaly detection (drop in PRs)
    months = sorted(pr_trend.keys())
    drops = []
    for i in range(1, len(months)):
        if pr_trend[months[i]] < pr_trend[months[i-1]] * 0.5:
            drops.append(months[i])

    # Code staleness detection
    stale_files, staleness = detect_code_staleness(commits)
    results = {
        'pr_trend': pr_trend,
        'commit_trend': commit_trend,
        'top_repos': top_repos,
        'avg_response': avg_response,
        'drops': drops,
        'total_commits': len(commits),
        'total_prs': len(prs),
        'response_times': response_times,
        'stale_files': stale_files,
        'staleness': staleness,
    }
    return results
