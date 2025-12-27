"""
Rich console display utilities for CLI.
"""

from contextlib import contextmanager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@contextmanager
def show_progress(total: int, description: str):
    """Context manager for progress display."""
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
    ) as progress:
        task = progress.add_task(description, total=total)

        class ProgressUpdater:
            def advance(self, n: int = 1):
                progress.update(task, advance=n)

        yield ProgressUpdater()


def show_statistics(stats: dict):
    """Display application statistics."""
    table = Table(title="Application Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Applications", str(stats["total_applications"]))
    table.add_row("Total Emails Sent", str(stats["total_emails_sent"]))
    table.add_row("Follow-ups Sent", str(stats["follow_ups_sent"]))

    console.print("\n")
    console.print(table)

    # Status breakdown
    status_table = Table(title="Status Breakdown")
    status_table.add_column("Status", style="cyan")
    status_table.add_column("Count", style="magenta")

    for status, count in stats["by_status"].items():
        status_table.add_row(status.replace("_", " ").title(), str(count))

    console.print("\n")
    console.print(status_table)


def show_banner():
    """Display application banner."""
    console.print(
        Panel.fit(
            "[bold cyan]CV Mailer[/bold cyan]\nAutomated Resume Email System", border_style="cyan"
        )
    )
