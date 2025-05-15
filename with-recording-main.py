# Verbatim from https://docs.livekit.io/agents/start/voice-ai/
# modified to include recording from https://docs.livekit.io/agents/ops/recording/

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

# added for recording
from livekit import api
from datetime import datetime
import json

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")


async def entrypoint(ctx: agents.JobContext):

    # Set up text transcript recording (added)
   # Add the following code to the top, before calling ctx.connect()
    
    async def write_transcript():
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"./transcript_{ctx.room.name}_{current_date}.json"
        with open(filename, 'w') as f:
            json.dump(session.history.to_dict(), f, indent=2)
            
        print(f"**** Transcript for {ctx.room.name} saved to {filename} ****")

    ctx.add_shutdown_callback(write_transcript)

    # .. The rest of your entrypoint code follows ...


    await ctx.connect()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

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
        instructions="Greet the user and offer your assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
