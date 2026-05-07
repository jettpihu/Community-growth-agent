"""
AI Community Growth Agent

Mailbox-enabled uAgent that helps organizers with events, conferences, and hackathons (globally).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4
import httpx
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TavilyClient = None
    TAVILY_AVAILABLE = False

# ────────────────────────────────────────────────
#  Load secrets from Agentverse secrets/environment
# ────────────────────────────────────────────────

ASI_ONE_API_KEY = (os.getenv("ASI_ONE_API_KEY") or "").strip()
TAVILY_API_KEY = (os.getenv("TAVILY_API_KEY") or "").strip()


def _tavily_search(query: str, max_results: int = 8, max_chars: int = 6000) -> str:
    """Use Tavily for web search — speakers, venues, LinkedIn, contacts."""
    if not TAVILY_AVAILABLE or not TAVILY_API_KEY or not TavilyClient:
        return ""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        context = client.get_search_context(
            query=query,
            search_depth="advanced",
            max_results=max_results,
        )
        if not isinstance(context, str) or not context.strip():
            return ""
        return context.strip()[:max_chars]
    except Exception:
        return ""


def _call_asi1_chat(
    system_prompt: str,
    user_text: str,
    web_context: str = "",
) -> str:
    """Call ASI One API. Pass web_context from Tavily for speaker/venue/LinkedIn queries."""
    if not ASI_ONE_API_KEY:
        raise RuntimeError("ASI_ONE_API_KEY is not set in Agentverse secrets")

    user_content = user_text
    if web_context.strip():
        user_content = (
            "Use the following web search results (from Tavily) to answer. Cite real names, LinkedIn profiles, and venues when present.\n\n"
            "---\nWeb search context:\n" + web_context.strip() + "\n---\n\n"
            "User request:\n" + user_text
        )

    payload = {
        "model": "asi1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 2048,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stream": False,
        "web_search": False,
    }

    headers = {
        "Authorization": f"Bearer {ASI_ONE_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = httpx.post(
        "https://api.asi1.ai/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=90.0,
    )
    resp.raise_for_status()

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("No choices in ASI:One response")

    return choices[0]["message"]["content"].strip()


def _sanitize_user_input(text: str, max_length: int = 4000) -> str:
    text = (text or "").strip()[:max_length]
    if not text:
        return text

    blocked_phrases = [
        "ignore previous",
        "ignore all previous",
        "system prompt",
        "you are now",
        "forget instructions",
        "disregard instructions",
        "__import__",
        "eval(",
        "exec(",
    ]

    lower = text.lower()
    for phrase in blocked_phrases:
        if phrase in lower:
            raise ValueError("Message blocked: suspicious content detected.")

    return text


SYSTEM_PROMPT = """\
You are an AI Community Growth Agent that helps organizers plan and grow meetups, conferences, community events, and hackathons (including global/remote).

Your role: Provide data-driven, practical guidance to help communities scale impact, engage members, and execute successful events efficiently.

────────────────────────────────────────────────────────────
MODULES (M1–M6 — respond only to the one that best matches the user's request):
────────────────────────────────────────────────────────────

M1 Engagement Analyzer:
  Goal: Review past events and identify patterns + optimization opportunities.
  Input: List of past events (topic, date, attendees, format, feedback, engagement metrics)
  Output: 
    - 4–8 insights (what worked, what didn't, drop-off trends)
    - Top 2–3 actionable recommendations with rationale
    - Suggested metrics to track going forward
  Example: "Based on your data, 60% attend first event but only 30% return. Recommended: build 'alumni network' track and create post-event survey."

M2 Event/Hackathon Predictor:
  Goal: Forecast logistics and participation for upcoming events.
  Input: Event description (type, target audience, date, past data if available)
  Output: 
    - 1–2 paragraph summary with reasoning
    - Compact table: estimated RSVP range, likely cancellation %, optimal day/time, recommended venue size
    - Risk factors + mitigations
  Example: "For a 2-day hackathon targeting mid-career devs on a Friday–Saturday, expect 40–60% RSVPs (Saturday drop ~15%). Recommend 200 sq ft per person."

M3 Speaker Finder:
  Goal: Identify and suggest speakers with credibility and audience fit.
  Input: Topic + location (or global) + event size + preferred depth (beginner/intermediate/advanced)
  Output: Up to 5 suggestions, each with:
    - Name, current org/role, 1–2 sentence why they're qualified
    - Known speaking topics or relevant content
    - How to find: email, LinkedIn profile (linkedin.com/in/username), personal URL, or known event appearances
    - Estimated availability (if known)
  Caveat: "These are suggestions based on public info — please verify profiles and current availability manually."

M4 Sponsor Outreach:
  Goal: Provide customized sponsor engagement templates.
  Input: Community/event profile + target sponsor types
  Output: 3 email drafts (local startup / mid-size corp / enterprise)
    - Subject line included
    - Benefit-aligned messaging (ROI for each tier)
    - Clear CTA and contact method
  Tone: Professional, genuine community value proposition.

M5 Viral Post Generator:
  Goal: Create audience-specific social media content variants.
  Input: Event description + target audience + desired tone
  Output: 5 posts optimized for:
    - LinkedIn (professional, value-focused)
    - X/Twitter (catchy, link-friendly)
    - WhatsApp (community feel, conversational)
    - Instagram (visual hooks, call to action)
    - Event platform teaser (FOMO, urgency)
  Note: Include hashtags and @ handles where relevant. Never post on behalf of user.

M6 Venue & Location Finder:
  Goal: Suggest venues with full logistics and contact info.
  Input: Event type + city + date + expected attendees + duration + budget (optional)
  Output: Up to 5 venue options, each with:
    - Name, full address, capacity, accessibility info
    - Contact: email, phone, website, booking link
    - Key fit factors: tech setup, parking, catering options, AV support
    - Price range (if known)
    - Why suitable for your event type
    - Nearby alternatives if first choice unavailable
  When web search available: include venue event manager LinkedIn, past events hosted, speaker/conference fit.
  Caveat: "These are public suggestions — verify availability, pricing, and contracts manually."

────────────────────────────────────────────────────────────
RESPONSE GUIDELINES:
────────────────────────────────────────────────────────────

FORMAT:
- Reply only in plain text. Do not output tool calls, XML tags, raw API formats, or code blocks.
- Use bullet points, tables, and numbered lists for clarity.
- Concise and practical — aim for 200–600 words per response.

PREDICTIONS & ESTIMATES:
- Always use ranges, never single precise numbers. Example: "30–40% attendance" not "37% attendance."
- Explain assumptions: "Assuming professional audience, Friday 6 PM, hybrid format…"
- Flag confidence levels: high (similar past data), medium (patterns from industry), low (new experiment).

INTERACTION:
- Ask at most ONE clarifying question per response; defer others to follow-up.
- Summarize your understanding before answering.
- If ambiguous, suggest the most common scenario but offer alternatives.

SAFETY & ETHICS:
- Never send emails, DMs, or posts on user's behalf — only provide drafts.
- Read-only agent: no sensitive data storage, no payment processing, no access to user platforms.
- Respect privacy: always cite public sources and suggest manual verification.
- Recommend legal/privacy review for large-scale email campaigns.

WEB SEARCH INTEGRATION:
- When "Web search context" from Tavily is provided, use it to:
  * Find real speaker names, titles, LinkedIn profiles, past talks
  * Locate venues, address, contact details, booking pages
  * Identify relevant communities, hashtags, past event links
- Prioritize direct links (linkedin.com/in/username, facebook.com/events, etc.)
- Cite source: "According to recent web data…" or "Based on LinkedIn results…"
- Always remind user to verify: people move jobs, events dates change, websites update.

────────────────────────────────────────────────────────────
"""


def _should_use_web_search(user_text: str) -> bool:
    """Enable ASI web_search for speaker/venue/LinkedIn/contact-related requests."""
    t = user_text.lower()
    triggers = (
        "speaker", "venue", "venues", "linkedin", "contact", "find", "suggest",
        "location", "where", "who can speak", "mentor", "host", "organizer",
        "session", "speaker session", "venue speaker",
    )
    return any(trigger in t for trigger in triggers)

chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def on_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    # Flatten message content
    parts = [item.text for item in msg.content if isinstance(item, TextContent) and item.text]
    user_text = "\n".join(parts).strip()

    if not user_text:
        welcome = (
            "Hi! I'm your Community Growth Agent — helping with events, conferences & hackathons.\n\n"
            "Tell me what you'd like:\n"
            "• M1 — paste past events data\n"
            "• M2 — describe upcoming event/hackathon\n"
            "• M3 — speaker / mentor suggestions (topic + location)\n"
            "• M4 — sponsor email drafts\n"
            "• M5 — social media post variants\n"
            "• M6 — venue & contact suggestions (event type + city)\n"
        )
        await ctx.send(
            sender,
            ChatMessage(
                timestamp=datetime.now(timezone.utc),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=welcome)],
            ),
        )
        return

    try:
        user_text = _sanitize_user_input(user_text)
    except ValueError as e:
        await ctx.send(
            sender,
            ChatMessage(
                timestamp=datetime.now(timezone.utc),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=str(e))],
            ),
        )
        return

    web_context = ""
    if _should_use_web_search(user_text) and TAVILY_AVAILABLE and TAVILY_API_KEY:
        query = user_text[:500].strip().replace("\n", " ")
        if query:
            web_context = _tavily_search(query)
            if web_context:
                ctx.logger.info("Using Tavily web search for this request")

    try:
        answer = _call_asi1_chat(SYSTEM_PROMPT, user_text, web_context=web_context)
    except Exception as e:
        ctx.logger.exception("ASI:One call failed")
        answer = f"Sorry — backend error: {str(e)[:120]}"

    await ctx.send(
        sender,
        ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=answer)],
        ),
    )


@chat_proto.on_message(ChatAcknowledgement)
async def on_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"ACK received from {sender}")


# ─── Agent setup ───────────────────────────────────────

agent = Agent()

agent.include(chat_proto, publish_manifest=True)


@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"Community Growth Agent started → {agent.address}")
    ctx.logger.info(f"ASI:One API key present: {bool(ASI_ONE_API_KEY)}")
    ctx.logger.info(f"Tavily web search enabled: {bool(TAVILY_AVAILABLE and TAVILY_API_KEY)}")


if __name__ == "__main__":
    agent.run()
