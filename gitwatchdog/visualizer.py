import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

def visualize_results(results, show='all', use_streamlit=False):
    def show_plot():
        if use_streamlit:
            st.pyplot(plt.gcf())
        else:
            plt.show()
    if show in ('pr', 'all'):
        # PRs per month with anomaly highlight
        months = list(results['pr_trend'].keys())
        pr_counts = list(results['pr_trend'].values())
        colors = ['red' if m in results.get('drops', []) else 'blue' for m in months]
        plt.figure(figsize=(10,5))
        bars = plt.bar(months, pr_counts, color=colors)
        plt.title('PRs per Month (Red = Drop)')
        plt.xlabel('Month')
        plt.ylabel('PRs')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()
        show_plot()
    if show in ('contributors', 'all') and 'top_contribs' in results:
        # Top contributors as horizontal bar chart and pie chart
        contribs = results['top_contribs']
        names = [c[0] for c in contribs]
        counts = [c[1] for c in contribs]
        plt.figure(figsize=(8,4))
        sns.barplot(y=names, x=counts, orient='h', palette='viridis')
        plt.title('Top Contributors (Commits)')
        plt.xlabel('Commits')
        plt.tight_layout()
        show_plot()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=names, autopct='%1.1f%%', startangle=140)
        plt.title('Contributor Share')
        plt.tight_layout()
        show_plot()
    if show in ('response', 'all'):
        # Response time histogram
        if 'response_times' in results and results['response_times']:
            plt.figure(figsize=(8,4))
            sns.histplot(results['response_times'], bins=10, kde=True, color='green')
            plt.title('PR Response Times (hours)')
            plt.xlabel('Hours')
            plt.ylabel('Frequency')
            plt.tight_layout()
            show_plot()
        if results.get('avg_response'):
            print(f"Average PR response time: {results['avg_response']:.2f} hours")
    if show in ('anomalies', 'all'):
        # Anomalies
        if results.get('drops'):
            print(f"Activity drops detected in: {', '.join(results['drops'])}")
    if show in ('commits', 'all'):
        # Commit activity line chart (if available)
        if 'commit_trend' in results and results['commit_trend']:
            c_months = list(results['commit_trend'].keys())
            c_counts = list(results['commit_trend'].values())
            plt.figure(figsize=(10,5))
            plt.plot(c_months, c_counts, marker='o', color='purple')
            plt.title('Commits per Month')
            plt.xlabel('Month')
            plt.ylabel('Commits')
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()
            show_plot()
    if show in ('repos', 'all') and 'top_repos' in results:
        # Top repositories contributed to (user analysis)
        repo_names = [r[0] for r in results['top_repos']]
        repo_counts = [r[1] for r in results['top_repos']]
        plt.figure(figsize=(8,4))
        sns.barplot(y=repo_names, x=repo_counts, orient='h', palette='mako')
        plt.title('Top Repositories Contributed To')
        plt.xlabel('PRs')
        plt.tight_layout()
        show_plot()
    if show in ('staleness', 'all') and 'staleness' in results:
        # Visualize code staleness (days since last commit per file)
        staleness = results['staleness']
        if staleness:
            files = list(staleness.keys())
            days = list(staleness.values())
            # Show only top 20 by staleness
            top_idx = np.argsort(days)[-20:]
            top_files = [files[i] for i in top_idx]
            top_days = [days[i] for i in top_idx]
            plt.figure(figsize=(10,6))
            sns.barplot(y=top_files, x=top_days, orient='h', palette='rocket')
            plt.title('Code Staleness: Days Since Last Commit (Top 20 Files)')
            plt.xlabel('Days Since Last Commit')
            plt.tight_layout()
            show_plot()
        # Print summary of stale files
        if results.get('stale_files'):
            print("Stale modules (inactive >30 days):")
            for fname, days in results['stale_files'].items():
                print(f"- {fname}: {days} days")
            print("The tool flags modules with stale contributors—aligns with developer behavior modelling like TransRacer and SmallRace.")
    if show in ('race', 'all') and 'race_risk' in results:
        # Visualize race risk hotspots (stub)
        race_risk = results['race_risk']
        if race_risk:
            # Example: visualize as bar chart
            files = list(race_risk.keys())
            risks = list(race_risk.values())
            plt.figure(figsize=(10,6))
            sns.barplot(y=files, x=risks, orient='h', palette='flare')
            plt.title('Race Risk Hotspots')
            plt.xlabel('Risk Score')
            plt.tight_layout()
            show_plot()
    if show in ('ownership', 'all') and 'ownership' in results:
        ownership = results['ownership']
        # Bus factor visualization
        bus_factor = ownership.get('bus_factor', {})
        if bus_factor:
            files = list(bus_factor.keys())
            factors = list(bus_factor.values())
            top_idx = np.argsort(factors)[-20:]
            top_files = [files[i] for i in top_idx]
            top_factors = [factors[i] for i in top_idx]
            plt.figure(figsize=(10,6))
            sns.barplot(y=top_files, x=top_factors, orient='h', palette='crest')
            plt.title('Bus Factor (Unique Contributors per File)')
            plt.xlabel('Bus Factor')
            plt.tight_layout()
            show_plot()
        # Orphaned files
        orphaned = ownership.get('orphaned_files', [])
        if orphaned:
            print('Orphaned files (no commits in last 90 days):')
            for fname in orphaned:
                print(f'- {fname}')
        # Contributor reliability
        reliability = ownership.get('reliability_score', {})
        if reliability:
            names = list(reliability.keys())
            scores = [reliability[n] for n in names]
            plt.figure(figsize=(8,4))
            sns.barplot(x=names, y=scores, palette='Blues')
            plt.title('Contributor Reliability (Bugfix Ratio)')
            plt.ylabel('Bugfix Commits / Total Commits')
            plt.xticks(rotation=45)
            plt.tight_layout()
            show_plot()
    if show in ('prediction', 'all') and 'risk_prediction' in results:
        # Visualize temporal risk prediction (predicted risk per file/module)
        prediction = results['risk_prediction']
        if prediction:
            files = list(prediction.keys())
            risks = list(prediction.values())
            top_idx = np.argsort(risks)[-20:]
            top_files = [files[i] for i in top_idx]
            top_risks = [risks[i] for i in top_idx]
            plt.figure(figsize=(10,6))
            sns.barplot(y=top_files, x=top_risks, orient='h', palette='ch:s=.25,rot=-.25')
            plt.title('Predicted Risk (Next Month)')
            plt.xlabel('Predicted Risk Score')
            plt.tight_layout()
            show_plot()
    if show in ('risk', 'all') and 'risk_report' in results:
        print('Automated Anomaly & Risk Report:')
        print(results['risk_report'])
