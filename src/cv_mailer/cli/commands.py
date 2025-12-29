"""
CLI command handlers.
"""

import argparse
import logging
import sys

from cv_mailer.cli.app import CVMailer
from cv_mailer.cli.display import console, show_banner
from cv_mailer.config import Config

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(Config.LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="CV Mailer - Automate resume emailing to recruiters"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without actually sending emails"
    )
    parser.add_argument("--follow-ups", action="store_true", help="Send follow-up emails only")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument(
        "--repair-followups",
        action="store_true",
        help="Repair historical follow-up numbering issues in the local DB (use --dry-run to preview)",
    )
    parser.add_argument(
        "--new", action="store_true", help="Process new applications only (default)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Show banner
    show_banner()

    try:
        mailer = CVMailer()

        if args.stats:
            mailer.show_statistics()
        elif args.repair_followups:
            console.print("\n[bold]Repairing follow-up numbering...[/bold]")
            stats = mailer.tracker.repair_follow_up_numbers(dry_run=args.dry_run)
            if args.dry_run:
                console.print(
                    f"[yellow]DRY RUN:[/yellow] scanned={stats['applications_scanned']}, "
                    f"would_change={stats['applications_changed']}, "
                    f"would_update_rows={stats['rows_updated']}"
                )
            else:
                console.print(
                    f"[green]✓[/green] Repair complete: scanned={stats['applications_scanned']}, "
                    f"changed={stats['applications_changed']}, "
                    f"updated_rows={stats['rows_updated']}"
                )
        elif args.follow_ups:
            mailer.send_follow_ups(dry_run=args.dry_run)
        else:
            # Default: process new applications
            mailer.process_new_applications(dry_run=args.dry_run)
            if not args.dry_run:
                # Also check for follow-ups
                mailer.send_follow_ups(dry_run=False)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
