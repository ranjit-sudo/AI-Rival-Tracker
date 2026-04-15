# AI Rival Tracker 🕵️‍♂️

Stop manually checking what your competitors are shipping. This tool automates the competitive intelligence process and transforms raw updates into a strategic game plan.

Give it a URL. It finds their changelog, blog, or news section, scrapes the latest content, compares it to your last check, and hands you a strategy brief with actual action items—not just a summary.

## 🚀 How it Works

- **URL Discovery:** Input a competitor domain; the tool automatically hunts for `/changelog`, `/blog`, `/updates`, or similar subdirectories.
- **Scraping & Storage:** It extracts the core content and saves a local baseline.
- **Differential Analysis:** On the next run, it identifies exactly what has changed since the last check.
- **AI Intelligence:** Sends the "diff" to GPT to generate a strategy brief covering threats, opportunities, and recommended tasks.

## 🛠 Prerequisites

Ensure you have the following installed:
- Python 3.11 or higher
- uv (Fast Python package installer)
- An OpenAI API key

### Install uv

```bash
# Check if you have it
uv --version

# If not, install it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## ⚙️ Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/ranjit-sudo/rival-tracker.git
cd AI Rival Tracker
```

**2. Install dependencies:**
```bash
uv add requests beautifulsoup4 openai python-dotenv rich lxml
```

**3. Configure Environment:**
```bash
cp .env.example .env
```
Open `.env` and add your OpenAI key:
```plaintext
OPENAI_API_KEY=sk-your-key-here
```

NOTE:
```text
I am using Ollama with the `qwen-coder 2.5b` variant locally and no frontier model, but you are free to use any model.
```

## 🏃 Running the Tracker

Launch the interactive CLI:
```bash
uv run python main.py
```

### Menu Options

| Option | Action |
| :--- | :--- |
| **1** | **Track a competitor** — Add a new URL or re-check an existing one. |
| **2** | **View tracking list** — See all competitors currently being monitored. |
| **3** | **Force re-analyze** — Generate a brief even if no new content was detected. |
| **4** | **Exit** |

## 📂 Project Structure

```plaintext
rival-tracker/
├── src/
│   └── rival_tracker/
│       ├── scraper.py       # Discovery and content extraction logic
│       ├── analyzer.py      # OpenAI GPT integration for strategy briefs
│       ├── storage.py       # Local JSON data management
│       ├── reporter.py      # Terminal UI and Markdown formatting
├── data/                    # Local JSON storage of scraped content
├── reports/                 # Generated Markdown strategy briefs
├── main.py                  # CLI Entry point
├── .env                     # Private API keys
├── .env.example             # Environment template
└── pyproject.toml           # Dependency and project configuration
```

## 📄 The Strategy Brief

Every analysis is saved to the `/reports` folder as a Markdown file. Each brief includes:

- **What's New:** Specific features or announcements detected.
- **Strategic Implications:** What their moves signal about their long-term roadmap.
- **Threats to Watch:** Changes that could directly steal your market share.
- **Opportunities:** Gaps they’ve left open for you to move into.
- **Recommended Actions:** 3 to 5 actionable "to-dos" for your team this week.
- **Urgency Level:** LOW / MEDIUM / HIGH / CRITICAL with reasoning.

## 💡 Pro Tips

**Recommended URLs for Testing:**
- stripe.com
- linear.app
- vercel.com
- github.com/blog

**Troubleshooting:**
- `ModuleNotFoundError`: Always use `uv run python main.py` to ensure you are within the correct virtual environment.
- **Empty Scrapes:** Some sites use heavy JavaScript or anti-bot measures. The tool reads raw HTML; if a site is a Single Page App (SPA), results may be limited.

## 🔒 Privacy & Security

- **Local Data:** All competitor data and history are stored locally in `/data`.
- **API Usage:** Only the text of the updates is sent to OpenAI.
- **Git Safety:** To prevent accidental data leaks, add the following to your `.gitignore`:

```plaintext
data/*.json
reports/*.md
.env
```

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute as you see fit.
