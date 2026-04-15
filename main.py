# main.py

import sys
import json
from rich.console import Console
from rich.prompt import Prompt, Confirm

from src.rival_tracker.scraper import scrape_competitor
from src.rival_tracker.analyzer import detect_changes, generate_strategy_brief
from src.rival_tracker.storage import (
    save_scrape_result, 
    load_prev_result,
    get_all_tracked_urls
)
from src.rival_tracker.reporter import (
    display_welcome,
    display_scraping_status,
    display_change_summary,
    display_strategy_brief,
    display_tracked_urls,
    save_brief_to_file,
    display_error,
    display_success,
    display_info,
    console
)


def track_competitor(url: str, force_analyze: bool = False) -> None:
    """
    Main workflow for tracking a single competitor URL.
    
    This function orchestrates the entire pipeline:
    URL → Scrape → Compare → Analyze → Display → Save
    
    Parameters:
    - url: The competitor's URL to track
    - force_analyze: If True, run AI analysis even if nothing changed
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    display_scraping_status(url)
    
    # ─── 1: Load previous data ───────────────────────────────
    previous_data = load_prev_result(url)
    
    if previous_data:
        display_info(f"Found previous data from {previous_data.get('last_checked', 'unknown date')}")
    else:
        display_info("No previous data found - this is a first-time check")
    
    # ─── 2: Scrape current data ──────────────────────────────
    console.print("[dim]Fetching current content...[/]")
    current_data = scrape_competitor(url)
    
    if current_data is None:
        display_error(f"Could not scrape {url}. Check the URL and try again.")
        return
    
    # ─── 3: Detect changes ───────────────────────────────────
    changes = detect_changes(current_data, previous_data)
    display_change_summary(changes)
    
    # ─── 4: Decide whether to run AI analysis ────────────────
    # We run AI analysis if:
    # - It's the first time (need to establish baseline understanding)
    # - Something changed
    # - User explicitly asked for it
    should_analyze = (
        changes.get("is_first_check") or 
        changes.get("text_changed") or 
        len(changes.get("new_entries", [])) > 0 or
        force_analyze
    )
    
    if should_analyze:
        console.print("\n[bold]🤖 Running AI Analysis...[/]")
        brief = generate_strategy_brief(url, current_data, changes)
        
        display_strategy_brief(brief, url)
        
        # Ask if user wants to save the report
        if Confirm.ask("\n💾 Save this brief to a file?", default=True):
            file_path = save_brief_to_file(brief, url)
            display_success(f"Brief saved to: {file_path}")
    
    else:
        console.print("\n[yellow]No significant changes detected - skipping AI analysis.[/]")
        console.print("[dim]Use 'force' option to run analysis anyway.[/]")
    
    # ─── 5: Save current data for next comparison ────────────
    json_string = json.dumps(current_data, indent=2)
    save_scrape_result(url, json_string)
    display_success("Updated tracking data saved.")


def show_main_menu() -> str:
    """Display the main menu and get user's choice."""
    console.print("\n[bold]What would you like to do?[/]\n")
    console.print("  [cyan]1[/] - Track a competitor (add new or re-check existing)")
    console.print("  [cyan]2[/] - View all tracked competitors")
    console.print("  [cyan]3[/] - Force re-analyze a competitor (even if nothing changed)")
    console.print("  [cyan]4[/] - Exit\n")
    
    return Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="1")


def main():
    """
    Main application loop.
    
    We use a loop so the user can track multiple competitors
    in one session without restarting the tool.
    """
    display_welcome()
    
    while True: 
        choice = show_main_menu()
        
        if choice == "1":
            url = Prompt.ask("\n🌐 Enter competitor URL")
            if url.strip():
                track_competitor(url.strip())
            else:
                display_error("Please enter a valid URL")
        
        elif choice == "2":
            # Show all tracked competitors
            console.print("\n")
            tracked = get_all_tracked_urls()
            display_tracked_urls(tracked)
        
        elif choice == "3":
            # Force re-analyze
            tracked = get_all_tracked_urls()
            
            if not tracked:
                display_error("No competitors tracked yet. Add one first!")
            else:
                display_tracked_urls(tracked)
                url = Prompt.ask("\n🌐 Enter URL to re-analyze")
                if url.strip():
                    track_competitor(url.strip(), force_analyze=True)
        
        elif choice == "4":
            console.print("\n[bold cyan]👋 Goodbye! Stay ahead of the competition![/]\n")
            sys.exit(0)

        console.print("\n" + "─" * 50)


if __name__ == "__main__":
    main()