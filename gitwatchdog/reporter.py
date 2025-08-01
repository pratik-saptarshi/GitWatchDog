import pandas as pd
from .api import export_json, export_csv


def export_report(results, filename):
    # Export PR trend
    pr_df = pd.DataFrame(list(results["pr_trend"].items()), columns=["Month", "PRs"])
    pr_df.to_csv(filename.replace(".md", "_prs.csv"), index=False)

    # Export top contributors
    contrib_df = pd.DataFrame(results["top_contribs"], columns=["Contributor", "Commits"])
    contrib_df.to_csv(filename.replace(".md", "_contributors.csv"), index=False)

    # Export advanced metrics
    export_json(results, filename.replace('.md', '.json'))
    export_csv(results, filename.replace('.md', '.csv'))

    # Export summary markdown
    with open(filename, "w") as f:
        f.write(f"# GitWatchdog Report\n\n")
        f.write(f"Total commits: {results['total_commits']}\n")
        f.write(f"Total PRs: {results['total_prs']}\n")
        f.write(f"Average PR response time: {results['avg_response']:.2f} hours\n")
        f.write(f"Top contributors: {', '.join([c[0] for c in results['top_contribs']])}\n")
        if results["drops"]:
            f.write(f"Activity drops detected in: {', '.join(results['drops'])}\n")
