# Community Growth Agent

![uAgents](https://img.shields.io/badge/uAgents-mailbox--enabled-blue)
![Events](https://img.shields.io/badge/events-conferences%20%26%20hackathons-green)
![Web search](https://img.shields.io/badge/web%20search-Tavily-orange)
![Read-only](https://img.shields.io/badge/read--only-no%20sensitive%20data-lightgrey)
![Python](https://img.shields.io/badge/python-3.10+-blue)

An AI assistant that helps **event organizers** plan and grow meetups, conferences, community events, and hackathons — locally or globally. Ask in plain language; it suggests speakers, venues, sponsor emails, social posts, and more. It never sends emails or posts for you — it only gives drafts and suggestions.

---

## 🎯 What it does

**Six specialized modules (M1–M6):**

| Module | Purpose | Use when… |
|--------|---------|-----------|
| **M1** — Engagement Analyzer | Review past events and identify optimization opportunities | You want insights from past attendance/feedback data |
| **M2** — Event/Hackathon Predictor | Forecast RSVP, timing, venue size, and no-shows | Planning an upcoming event and need logistics estimates |
| **M3** — Speaker Finder | Identify speakers with credibility, topics, and contact info | You're assembling a speaker lineup |
| **M4** — Sponsor Outreach | Generate customized sponsor email templates (tiered) | You need compelling sponsor pitches |
| **M5** — Viral Post Generator | Create 5 social media variants (LinkedIn, X, WhatsApp, Instagram, event page) | You want quick, audience-tailored promotion |
| **M6** — Venue & Location Finder | Suggest venues with capacity, contact, accessibility, and fit | You're scouting event locations |

---

## 📋 How to use

### Quick start

1. **Identify your need:** Which of the 6 modules matches your request?
2. **Provide context:** Paste relevant data (past events, attendee counts, preferences, location, budget).
3. **Ask in plain language:** Example: *"Suggest 5 speakers for a DevOps meetup in Bangalore; include LinkedIn if you can."*
4. **Review & customize:** Agent provides drafts/suggestions; you verify contacts and make final decisions.

### Example queries

| **Module** | **You might ask…** |
|------------|-------------------|
| **M1** | *Review these past events: [paste list]. What should we improve?* |
| **M2** | *I'm planning a 2-day hackathon in June with 150 target attendees. Predict turnout and suggest venue size.* |
| **M3** | *Suggest 5 speakers for our AI community event in London. Include LinkedIn profiles if available.* |
| **M4** | *Create sponsor email drafts for our conference — one for local startups, one for enterprise.* |
| **M5** | *Generate 5 social post variants for our AI meetup (LinkedIn, Twitter, WhatsApp, Instagram, Facebook).* |
| **M6** | *Find venues in Delhi for a 100-person workshop on cloud security. Suggest 3–5 options.* |

---

## 🛠 Tech stack

| Layer | Technology |
|-------|------------|
| **Agent runtime** | [uAgents](https://docs.fetch.ai/agents/uagents/) (mailbox-enabled) |
| **LLM** | [ASI:One](https://api.asi1.ai) (OpenAI-compatible chat completions) |
| **Web search** | [Tavily](https://tavily.com) (advanced search context) |
| **HTTP client** | `httpx` |
| **Language** | Python 3.10+ |

**Data flow:**
```
User message → [Sanitize & routing] → [Tavily search if needed] → 
ASI:One (asi1 model, text-only) → Plain-text reply
```

Web search is triggered by keywords like "speaker," "venue," "LinkedIn," "contact." Responses remain text-only (no links embedded in LLM output).

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip or poetry
- API keys (see Configuration)

### Clone & setup

```bash
git clone https://github.com/jettpihu/Community-growth-agent.git
cd Community-growth-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file or set these environment variables in Agentverse secrets:

```bash
# Required: ASI:One API key (get from https://api.asi1.ai)
export ASI_ONE_API_KEY="your-api-key-here"

# Optional: Tavily API key for web search (get from https://tavily.com)
export TAVILY_API_KEY="your-tavily-key-here"
```

**Note:** If `TAVILY_API_KEY` is not set, web search is disabled but agent still works without it.

---

## 🚀 Running the agent

### Local development

```bash
python agent.py
```

The agent will log:
- Startup address and status
- ASI:One API key presence
- Tavily web search availability

### Deploy to Agentverse

1. Go to [Agentverse](https://agentverse.ai)
2. Create a new mailbox agent
3. Copy `agent.py` code into the Agentverse editor
4. Set secrets: `ASI_ONE_API_KEY` and optionally `TAVILY_API_KEY`
5. Deploy and enable mailbox

### Integration examples

**Via chat protocol (uAgents network):**
```python
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

# Send a question to the Community Growth Agent
async def ask_agent(agent_address, question):
    msg = ChatMessage(content=[TextContent(type="text", text=question)])
    await ctx.send(agent_address, msg)
```

---

## 💡 Best practices

### For accurate results, provide:

1. **M1 (Engagement):** Exact attendee counts, feedback or survey data, event format (online/in-person/hybrid)
2. **M2 (Prediction):** Target audience, past event patterns (if any), date/time, event format
3. **M3 (Speakers):** Topic depth level, location, audience size, prior speaker/format preferences
4. **M4 (Sponsors):** Community size/demographics, event type, ROI metrics you can promise
5. **M5 (Posts):** Target audience demographic, brand tone, urgency (FOMO vs. educational)
6. **M6 (Venues):** Capacity needed, budget range, amenities required (AV, catering, WiFi, parking)

### Limitations & disclaimers

- **Suggestions, not guarantees:** Always verify speaker availability, venue quotes, and contact info manually before organizing.
- **Read-only:** Agent never accesses your email, social accounts, or payment systems. You control all outreach.
- **Public data only:** Suggestions are based on publicly available information. Verify via LinkedIn, venue websites, or direct contact.
- **No real-time updates:** Speaker contact info, venue availability, or pricing may change; always double-check.

---

## 🔒 Security & privacy

- **No data storage:** Agent does not log or store user queries, event data, or personal information.
- **Tavily integration:** When enabled, web search uses Tavily's search results (read-only, public info only).
- **No automatic action:** Agent provides drafts only. User manually sends emails, posts, or confirmations.
- **Input sanitization:** Blocks suspicious input patterns (SQL injection, prompt injection attempts).

---

## 📚 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"ASI_ONE_API_KEY is not set"** | Set `ASI_ONE_API_KEY` in environment or Agentverse secrets. Get API key from [api.asi1.ai](https://api.asi1.ai). |
| **No web search results** | Ensure `TAVILY_API_KEY` is set in environment. Web search is optional; agent still works without it. |
| **Agent not responding** | Check logs for API errors. Verify network connectivity. Restart agent. |
| **Poor suggestion quality** | Provide more context (past data, specific constraints, audience profile). Be specific in your query. |
| **"Message blocked: suspicious content detected"** | Your query contains potential injection patterns. Rephrase without keywords like "ignore previous" or "system prompt." |

---

## 📝 Requirements

See [requirements.txt](requirements.txt) for full dependency list. Key packages:

- `uagents` — Agent runtime
- `httpx` — HTTP requests  
- `tavily-python` — Web search (optional)

---

## 📄 License

[Your License Here] — Update as needed

---

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue or pull request!

---

## 📞 Support

- **Documentation:** [uAgents docs](https://docs.fetch.ai/agents/uagents/)
- **ASI:One API:** [api.asi1.ai](https://api.asi1.ai)
- **Tavily:** [tavily.com](https://tavily.com)

---

## Prerequisites

- **Python 3.10+**
- **ASI:One API key** — [ASI:One](https://api.asi1.ai) (required)
- **Tavily API key** — [Tavily](https://tavily.com) (optional; enables real web search for speakers/venues/LinkedIn)

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ASI_ONE_API_KEY` | Yes | API key for ASI:One chat completions (`https://api.asi1.ai/v1`) |
| `TAVILY_API_KEY` | No | API key for Tavily; if set, speaker/venue/contact queries use live web search |

Example (Agentverse secrets or local `.env`):

```bash
export ASI_ONE_API_KEY="your_asi_one_key"
export TAVILY_API_KEY="your_tavily_key"   # optional
```

---

## Installation & run

```bash
# Clone (or navigate to the repo)
cd "path/to/repo"

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install uagents uagents_core httpx tavily-python

# Set env vars (see above), then run the agent
python agent.py
```

Without `tavily-python` or `TAVILY_API_KEY`, the agent still runs; speaker/venue/LinkedIn queries will not use web search.

---

## Project layout

```
.
├── agent.py      # uAgent + chat protocol; Tavily search + ASI:One chat
└── README.md

---

## ⚠️ PR Testing (Intentional, Reversible)

This repository includes a deliberately failing test used only for PR and CI validation.

- File: `tests/test_agent.py`
- Purpose: Demonstrate CI failure and PR checks without modifying core functionality.
- Action: Remove or update this test before merging into the `main` branch.

Use this to validate your agent's behavior when handling PRs and CI failures.

```

---

## License

MIT (or your chosen license).
