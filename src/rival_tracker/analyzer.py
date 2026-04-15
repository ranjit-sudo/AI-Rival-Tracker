import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv(override=True)

def get_openai_client() -> OpenAI:
    """ Create and return an OpenAI client """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY nahi mili! "
        )
    
    return OpenAI(api_key="ollama",base_url="http://localhost:11434/v1")


def detect_changes(current_data: dict, previous_data: dict | None) -> dict:
    """
    Compare current scrape with previous scrape to identify what's new.
    
    This is done BEFORE sending to AI to:
    1. Reduce tokens sent to AI
    2. Give AI focused information about changes only
    3. Make the analysis more precise
    """
    if previous_data is None:
        return {
            "is_first_check": True,
            "new_entries": current_data.get("entries", []),
            "text_changed": True,
            "change_summary": "First time checking this competitor - establishing baseline."
        }
    
    current_entries = current_data.get("entries", [])
    previous_entries = previous_data.get("content", {}).get("entries", [])
    
    previous_titles = {
        entry.get("title", "").lower() 
        for entry in previous_entries 
        if entry.get("title")
    }
    
    new_entries = []
    for entry in current_entries:
        title = entry.get("title", "").lower()
        if title and title not in previous_titles:
            new_entries.append(entry)
    
    current_text = current_data.get("raw_text", "")
    previous_text = previous_data.get("content", {}).get("raw_text", "")
    text_changed = current_text != previous_text
    
    return {
        "is_first_check": False,
        "new_entries": new_entries,
        "total_current_entries": len(current_entries),
        "total_previous_entries": len(previous_entries),
        "text_changed": text_changed,
        "last_checked": previous_data.get("last_checked", "Unknown"),
        "change_summary": f"Found {len(new_entries)} new entries since last check."
    }


def build_analysis_prompt(
    competitor_url: str,
    current_data: dict,
    changes: dict
) -> str:
    """ Build a detailed prompt for GPT """
    
    new_entries_text = ""
    if changes.get("new_entries"):
        new_entries_text = "\n\n## NEW ENTRIES DETECTED:\n"
        for i, entry in enumerate(changes["new_entries"][:10], 1): 
            new_entries_text += f"\n### Entry {i}\n"
            if entry.get("title"):
                new_entries_text += f"**Title:** {entry['title']}\n"
            if entry.get("date"):
                new_entries_text += f"**Date:** {entry['date']}\n"
            if entry.get("content"):
                new_entries_text += f"**Content:** {entry['content'][:300]}\n"
    
    raw_text_sample = current_data.get("raw_text", "")[:3000]
    
    if changes.get("is_first_check"):
        change_context = """
This is the FIRST TIME we're checking this competitor. 
Analyze what they currently offer and establish a baseline understanding.
Focus on: What is their current product positioning? What features do they highlight? 
What have they recently launched based on the content?
"""
    else:
        last_checked = changes.get("last_checked", "previously")
        new_count = len(changes.get("new_entries", []))
        change_context = f"""
We last checked this competitor on: {last_checked}
We found {new_count} new entries since then.
{'Text content has changed.' if changes.get('text_changed') else 'No major text changes detected.'}
Focus your analysis on WHAT IS NEW and what it means strategically.
"""
    
    prompt = f"""You are a competitive intelligence analyst helping a business owner understand what their competitor is doing.

## COMPETITOR: {competitor_url}
## PAGE ANALYZED: {current_data.get('scraped_url', competitor_url)}
## ANALYZED AT: {current_data.get('scraped_at', 'Now')}

## SITUATION:
{change_context}

{new_entries_text}

## RECENT CONTENT FROM THEIR PAGE:
{raw_text_sample}

---

## YOUR TASK - Generate a "Strategy Brief" with these EXACT sections:

### 📊 WHAT'S NEW
List the specific new features, announcements, or updates detected. 
Be concrete and specific - no vague language.
If this is a first check, describe what their current focus appears to be.

### 🎯 STRATEGIC IMPLICATIONS  
For each major update, explain:
- What problem are they solving for customers?
- What market signal does this send?
- Are they moving up-market, down-market, or sideways?

### ⚠️ THREATS TO WATCH
What in these updates could directly hurt my business?
What customer needs are they addressing that I might be ignoring?

### 💡 OPPORTUNITIES FOR ME
Based on what they're focusing on, what gaps can I exploit?
What are they NOT doing that I could do better?

### 🎬 RECOMMENDED ACTIONS
Give 3-5 specific, actionable things I should consider doing THIS WEEK 
in response to these competitor moves. Be specific, not generic.

### 📈 URGENCY LEVEL
Rate: LOW / MEDIUM / HIGH / CRITICAL
Explain why in 1-2 sentences.

Keep the entire brief scannable and actionable. Business owners are busy.
Use bullet points. Be direct. No filler words.
"""
    
    return prompt



def generate_strategy_brief(
    competitor_url: str,
    current_data: dict, 
    changes: dict
) -> str:
    """ Send data to Gemini and get back the strategy brief """

    client = get_openai_client()
    
    prompt = build_analysis_prompt(competitor_url, current_data, changes)
    
    print("[Analyzer] Sending to AI for analysis...")
    print(f"[Analyzer] Prompt length: {len(prompt)} characters")
    
    try:
        response = client.chat.completions.create(
            model="qwen2.5-coder:7b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior competitive intelligence analyst with 15 years of experience "
                        "helping startups and small businesses understand their competitive landscape. "
                        "You are direct, strategic, and action-oriented. You never waste words."
                    )
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,  
            max_tokens=2000,
        )
        
        brief = response.choices[0].message.content
        
        # Log token usage so user knows the cost
        usage = response.usage
        total = getattr(usage, "total_tokens", 0)
        prompt = getattr(usage, "prompt_tokens", 0)
        completion = getattr(usage, "completion_tokens", 0)

        print(f"[Analyzer] Tokens used: {total} (prompt: {prompt}, response: {completion})")
        
        return brief or "No analysis generated by the AI."
    
    except Exception as e:
        return f"[Error generating analysis]: {str(e)}"

