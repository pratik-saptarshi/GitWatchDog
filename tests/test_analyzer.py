from gitwatchdog.analyzer import analyze_repo

def test_analyze_repo():
    # Example test: check output keys
    results = analyze_repo('octocat/Hello-World')
    assert 'pr_trend' in results
    assert 'avg_response' in results
    assert 'top_contribs' in results
    assert 'drops' in results
    assert 'total_commits' in results
    assert 'total_prs' in results
