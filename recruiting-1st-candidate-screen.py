from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

def read_instructions():
    with open("instructions.txt", "r") as f:
        return f.read().strip()


def read_jd():  # job description
    with open("jd-nurse-qual.txt", "r") as f:
        return f.read()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=read_instructions() + "\n" + read_jd())

tts=cartesia.TTS(
      model="sonic-english",
      voice="c2ac25f9-ecc4-4f56-9095-651354df60c0",
      speed=0.8,
      emotion=["curiosity:highest", "positivity:high"],
   )

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM.with_cerebras(
            model="llama-3.3-70b",
        ),
        tts=tts,
        vad=silero.VAD.load(), # VAD is voice activity detection
        turn_detection=MultilingualModel(),
    )
    print(f"session created with id: {session}")

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance.",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
