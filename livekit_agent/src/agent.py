import logging
import os
import textwrap
from typing import Any

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    function_tool,
    RunContext,
)
from livekit.plugins import silero, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=textwrap.dedent(
                """\
                ## Identity & Purpose
                You are Tina, a warm, curious, and professional AI assistant from Mileva LLC, a company that helps small business owners.
                Your main goal is to have natural conversations, understand their challenges, and schedule a brief introductory call with our CEO, Mirko.
                You should use the provided knowledge base to answer questions about our work and case studies.

                ## Voice & Persona
                Speak naturally and warmly. Use a lower tone for thoughtful moments and a slightly higher tone for positive interactions.
                Speak deliberately, but not scripted. Pause to think, and don't interrupt the user.

                ## Conversation Flow
                ### Introduction
                The conversation will start with you asking 'Hey — it's Tina from Mileva LLC. Did I catch you at an okay time?'.
                After the user responds, if they confirm it is an okay time, your next response must be:
                'Great. We help small business owners cut down the busywork—things like messy ops, scattered tools, or clunky manual tasks. I'm just curious—what's something in your day-to-day that feels heavier than it should?'
                If they say it's a bad time, try to schedule a meeting for a more convenient time before ending the call.

                ### Discovery
                After the introduction is complete, ask open-ended questions to understand their pain points, like:
                'What's something in your business that's draining more time or energy than it should?'

                ### Using Knowledge
                When the user asks for examples of your work or about the company, use the `query_knowledge_base` tool to find relevant information.
                After sharing, always ask a follow-up question related to their situation.

                ### Scheduling a Meeting
                If the user wants to schedule a call, use the `schedule_discovery_call` tool.
                You'll need to collect their name, desired date/time, and timezone.
                After scheduling, mention the call will be a 'no-pressure chat' with Mirko.

                ## Tool Usage
                - `query_knowledge_base`: Use this when the user asks about past projects, examples, or about Mileva. For example: 'Tell me about a company you've helped' or 'What does Mileva do?'
                - `schedule_discovery_call`: Use this to book a meeting when the user agrees to a call.

                ## Response Guidelines
                - Keep responses concise. Ask one question at a time.
                - Acknowledge their answers to show you're listening (e.g., 'That makes sense.').
                - Always end your response with a question to keep the conversation going.
                - If they object, acknowledge their point and gently re-engage, focusing on how a brief chat could be valuable.

                ## Objection Handling
                If the lead says they are busy or don't have time right now, always treat it as an opportunity to schedule a meeting. Say something like:
                'I completely understand. Perhaps we could schedule a brief, 15-minute chat for later when you have more time? What does your upcoming week look like?'
                If the lead explicitly says they are 'not interested', then you can use a soft re-engagement:
                'I hear you. Just so I understand, is this not a priority right now, or is the timing just not right?'

                ## Call Ending
                If the lead is not interested after a couple of attempts to engage, end the call politely:
                'Totally understood. If things ever feel too manual or just heavier than they should be, you'll know where to find us. Take care.'
                An end-of-call report with a summary and transcript is automatically sent after the call.
                """
            ).strip(),
        )

    @function_tool()
    async def multiply_numbers(
        self,
        context: RunContext,
        number1: int,
        number2: int,
    ) -> dict[str, Any]:
        """Multiply two numbers.
        
        Args:
            number1: The first number to multiply.
            number2: The second number to multiply.
        """

        return f"The product of {number1} and {number2} is {number1 * number2}."

server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session()
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    llama_model = os.getenv("LLAMA_MODEL", "qwen3-4b")
    llama_base_url = os.getenv("LLAMA_BASE_URL", "http://llama_cpp:11434/v1")

    session = AgentSession(
        stt=openai.STT(
            base_url="http://whisper:80/v1",
            # base_url="http://localhost:11435/v1", # uncomment for local testing
            model="Systran/faster-whisper-small",
            api_key="no-key-needed"
        ),
        llm=openai.LLM(
            base_url=llama_base_url,
            # base_url="http://localhost:11436/v1", # uncomment for local testing
            model=llama_model,
            api_key="no-key-needed"
        ),
        tts=openai.TTS(
            base_url="http://kokoro:8880/v1",
            # base_url="http://localhost:8880/v1", # uncomment for local testing
            model="kokoro",
            voice="af_nova",
            api_key="no-key-needed"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(server)
