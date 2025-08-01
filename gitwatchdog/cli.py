import click
from .analyzer import analyze_repo, analyze_user
from .visualizer import visualize_results
from .reporter import export_report

@click.group()
def main():
    """GitWatchdog CLI"""
    pass

@main.command()
@click.option('--repo', help='GitHub repo in owner/name format')
@click.option('--user', help='GitHub username for user-level analysis')
@click.option('--token', default=None, help='GitHub personal access token for authenticated requests')
@click.option('--export', default=None, help='Export report to file')
@click.option('--show', type=click.Choice(['pr', 'contributors', 'response', 'anomalies', 'commits', 'repos', 'staleness', 'race', 'ownership', 'prediction', 'risk', 'all'], case_sensitive=False), default='all', help='Select which graph or stat to show')
def analyze(repo, user, token, export, show):
    if repo:
        results = analyze_repo(repo, token)
    elif user:
        results = analyze_user(user, token)
    else:
        click.echo('Please provide either --repo or --user')
        return
    visualize_results(results, show)
    if export:
        export_report(results, export)

if __name__ == '__main__':
    main()
