import streamlit as st
from gitwatchdog.analyzer import analyze_repo, analyze_user
from gitwatchdog.visualizer import visualize_results
from gitwatchdog.github_api import get_user_data

st.title('GitWatchdog Interactive Dashboard')

mode = st.sidebar.selectbox('Analysis Mode', ['Repository', 'User'])
input_val = st.sidebar.text_input('GitHub Repo (owner/repo)' if mode == 'Repository' else 'GitHub Username')
token = st.sidebar.text_input('GitHub Token (optional)', type='password')
show_options_repo = ['all', 'pr', 'contributors', 'response', 'anomalies', 'commits', 'repos', 'staleness', 'race', 'ownership', 'prediction', 'risk']
show_options_user = ['all', 'pr', 'commits', 'repos', 'response', 'staleness', 'prediction', 'risk']
show = st.sidebar.selectbox('Show', show_options_repo if mode == 'Repository' else show_options_user)
show_json = st.sidebar.checkbox('Show raw JSON results')

if st.sidebar.button('Analyze'):
    with st.spinner('Analyzing...'):
        if mode == 'Repository' and input_val:
            results = analyze_repo(input_val, token)
        elif mode == 'User' and input_val:
            user_obj = get_user_data(input_val, token)
            if isinstance(user_obj, dict) and 'error' in user_obj:
                st.error(f"GitHub API error: {user_obj['error']} (status: {user_obj.get('status')})")
                st.stop()
            results = analyze_user(input_val, token)
            if not results or results.get('total_commits', 0) == 0:
                st.warning('User found, but no public activity or repositories.')
                st.stop()
        else:
            st.warning('Please enter a valid input.')
            st.stop()
    st.success('Analysis complete!')
    tabs = st.tabs(["Summary", "Visualizations", "Report"])
    with tabs[0]:
        st.header('Key Metrics')
        if mode == 'Repository':
            st.metric('Total Commits', results.get('total_commits', 0))
            st.metric('Total PRs', results.get('total_prs', 0))
            st.metric('Top Contributors', ', '.join([c[0] for c in results.get('top_contribs', [])]))
        else:
            st.metric('Total Commits', results.get('total_commits', 0))
            st.metric('Total PRs', results.get('total_prs', 0))
            st.metric('Top Repositories', ', '.join([r[0] for r in results.get('top_repos', [])]))
        st.metric('Average PR Response Time (hrs)', f"{results.get('avg_response', 0):.2f}")
        if show_json:
            st.write('Raw Results')
            st.json(results)
    with tabs[1]:
        st.header('Visualizations')
        visualize_results(results, show, use_streamlit=True)
    with tabs[2]:
        st.header('Automated Risk & Anomaly Report')
        if 'risk_report' in results:
            st.code(results['risk_report'])
        else:
            st.info('No risk report available for this analysis.')
