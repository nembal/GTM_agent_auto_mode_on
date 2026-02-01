"""Roundtable loop: ARTIST, BUSINESS, TECH take turns; same LLM, different prompts."""

import weave
from langchain_core.messages import HumanMessage, SystemMessage

from .llm import get_llm
from .personas import ROLES, get_persona

weave.init("viswanathkothe-syracuse-university/weavehacks")


@weave.op
def run_roundtable(
    topic: str,
    max_rounds: int = 2,
    seed_context: str | None = None,
):
    """
    Run the roundtable: each role (ARTIST, BUSINESS, TECH) speaks in turn for max_rounds.
    Same LLM, different system prompt per role. Optional seed_context (e.g. from Redis) prepended once.
    """
    llm = get_llm()
    transcript: list[dict[str, str]] = []

    initial = topic.strip()
    if seed_context and seed_context.strip():
        initial = f"Context:\n{seed_context.strip()}\n\nTopic: {topic.strip()}"

    for round_num in range(max_rounds):
        for role in ROLES:
            persona = get_persona(role)
            messages = [
                SystemMessage(content=persona),
                HumanMessage(content=initial),
            ]
            for entry in transcript:
                messages.append(
                    HumanMessage(content=f"[{entry['role'].upper()}] {entry['content']}")
                )
            messages.append(
                HumanMessage(content=f"Your turn as {role.upper()}. Reply in character.")
            )

            response = llm.invoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            transcript.append({"role": role, "content": content.strip()})

    # Summarizer agent: 3–5 actionable tasks for AI agents to run campaigns autonomously; cost-conscious; max 10–15 lines.
    summarizer_system = """You are a summarizer for an AI execution layer. Given the roundtable transcript, output 3–5 actionable GTM tasks that AI agents can carry out autonomously (no human hand-holding).
Constraints:
- Tasks must be executable by AI agents (clear, automatable steps).
- Prefer low-cost, high-return options (avoid expensive or vague tasks).
- Output must be at most 10–15 lines total.
No preamble—only this format:
Do this first: [one concrete, autonomous, cost-conscious task]
Do this next: [...]
Do this third: [...]
(Do this fourth / Do this fifth only if needed; keep total to 3–5 tasks and 10–15 lines.)"""

    transcript_text = "\n\n".join(
        f"[{e['role'].upper()}] {e['content']}" for e in transcript
    )
    summary_messages = [
        SystemMessage(content=summarizer_system),
        HumanMessage(content=f"Roundtable transcript:\n\n{transcript_text}\n\nOutput 3–5 actionable tasks in the required format (max 10–15 lines)."),
    ]
    summary_response = llm.invoke(summary_messages)
    summary = (
        summary_response.content
        if hasattr(summary_response, "content")
        else str(summary_response)
    ).strip()

    return {"transcript": transcript, "summary": summary}
