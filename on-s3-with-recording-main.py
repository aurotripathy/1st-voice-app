# Verbatim from https://docs.livekit.io/agents/start/voice-ai/
# modified to include recording from https://docs.livekit.io/agents/ops/recording/
# attempt to use a sequence similar to 

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, JobContext
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
import os

# get these from the env variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
print(f'AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID}')
print(f'AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY}')

load_dotenv()

import logging
logger = logging.getLogger("recording-on-aws-s3")
logger.setLevel(logging.DEBUG)


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")


async def entrypoint(ctx: JobContext):

    # Set up text transcript recording (added)
   # Add the following code to the top, before calling ctx.connect()
    logger.debug(f'ctx.room.name: {ctx.room.name}')    

    logger.debug("creating egress request")
    req = api.RoomCompositeEgressRequest(
        room_name=ctx.room.name,
        audio_only=True,
        file_outputs=[api.EncodedFileOutput(
            file_type=api.EncodedFileType.OGG,
            filepath="livekit/my-room-test.ogg",
            s3=api.S3Upload(
                bucket="aurovoice",
                region="us-east-2",
                access_key=AWS_ACCESS_KEY_ID,
                secret=AWS_SECRET_ACCESS_KEY,
            ),
        )],
    )

    logger.debug("creating livekit api")
    lkapi = api.LiveKitAPI()
    logger.debug("starting egress")
    res = await lkapi.egress.start_room_composite_egress(req)

    # .. The rest of your entrypoint code follows ...

    await ctx.connect()

    logger.debug("creating session")
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    logger.debug(f"session created with id: {session}")

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        # room_input_options=RoomInputOptions(
        #     # LiveKit Cloud enhanced noise cancellation
        #     # - If self-hosting, omit this parameter
        #     # - For telephony applications, use `BVCTelephony` for best results
        #     # noise_cancellation=noise_cancellation.BVC(), 
        # ),
    )

    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )

    await lkapi.aclose()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
