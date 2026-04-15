from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime
from pathlib import Path


console = Console()


def display_welcome():
    """Show a welcome banner when the tool starts."""
    console.print(
        Panel(
            Text("🚀 AI Rival Tracker", justify="center", style="bold cyan"),
            subtitle="Track what your competitors are launching",
            style="cyan",
            padding=(1, 4)
        )
    )


def display_scraping_status(url: str):
    """Show what we're currently doing."""
    console.print(f"\n[bold yellow]🕷️  Scraping:[/] {url}")


def display_change_summary(changes: dict):
    """Show a quick summary of what changed."""
    console.print("\n[bold]📋 Change Detection Results:[/]")
    
    if changes.get("is_first_check"):
        console.print("[green]  ✓ First time tracking this competitor - saving baseline[/]")
    else:
        new_count = len(changes.get("new_entries", []))
        last_checked = changes.get("last_checked", "Unknown")
        
        console.print(f"  Last checked: [dim]{last_checked}[/]")
        
        if new_count > 0:
            console.print(f"  [bold green]✓ {new_count} new entries found![/]")
        else:
            console.print("  [yellow]No new structured entries detected[/]")
            
        if changes.get("text_changed"):
            console.print("  [blue]ℹ Page content has changed since last check[/]")


def display_strategy_brief(brief: str, competitor_url: str):
    """ Display the AI-generated strategy brief beautifully """
    console.print("\n")
    console.print(
        Panel(
            f"[bold]Competitor:[/] {competitor_url}\n"
            f"[bold]Generated:[/] {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            title="[bold cyan]📊 Strategy Brief[/]",
            style="cyan"
        )
    )
    
    md = Markdown(brief)
    console.print(md)


def display_tracked_urls(tracked: list[dict]):
    """ Show all URLs currently being tracked in a nice table """
    if not tracked:
        console.print("[yellow]No competitors tracked yet. Add one to get started![/]")
        return
    
    table = Table(
        title="Currently Tracked Competitors",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Competitor URL", style="white", min_width=30)
    table.add_column("Last Checked", style="dim", min_width=20)
    
    for item in tracked:
        table.add_row(
            item.get("url", "Unknown"),
            item.get("last_checked", "Never")
        )
    
    console.print(table)


def save_brief_to_file(brief: str, competitor_url: str) -> str:
    """ Save the strategy brief to a markdown file """

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    safe_url = competitor_url.replace("https://", "").replace("http://", "")
    safe_url = "".join(c if c.isalnum() or c in "-." else "_" for c in safe_url)
    safe_url = safe_url[:50]  # Limit length
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{safe_url}_{timestamp}.md"
    file_path = reports_dir / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Competitor Strategy Brief\n\n")
        f.write(f"**Competitor:** {competitor_url}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        f.write(brief)
    
    return str(file_path)


def display_error(message: str):
    """Display an error message in red."""
    console.print(f"\n[bold red]❌ Error:[/] {message}")


def display_success(message: str):
    """Display a success message in green."""
    console.print(f"\n[bold green]✅[/] {message}")


def display_info(message: str):
    """Display an informational message."""
    console.print(f"[dim]ℹ {message}[/]")