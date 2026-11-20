"""
Edge TTS adapter for LiveKit Agents.
Uses Microsoft Edge's free TTS service — no API key required, unlimited usage.
"""

import io
import logging
import uuid
import edge_tts
import av
from livekit.agents import tts

logger = logging.getLogger("edge-tts-adapter")

SAMPLE_RATE = 24000
NUM_CHANNELS = 1


def _mp3_bytes_to_pcm(mp3_data: bytes) -> bytes:
    """Decode MP3 bytes to raw PCM s16le using PyAV."""
    container = av.open(io.BytesIO(mp3_data), format="mp3")
    resampler = av.AudioResampler(
        format="s16", layout="mono", rate=SAMPLE_RATE
    )
    pcm_chunks = []
    for frame in container.decode(audio=0):
        resampled = resampler.resample(frame)
        for r in resampled:
            pcm_chunks.append(r.to_ndarray().tobytes())
    container.close()
    return b"".join(pcm_chunks)


class EdgeTTS(tts.TTS):
    """LiveKit-compatible TTS using Microsoft Edge's free TTS engine."""

    def __init__(self, *, voice: str = "en-US-AriaNeural", rate: str = "+10%"):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=SAMPLE_RATE,
            num_channels=NUM_CHANNELS,
        )
        self._voice = voice
        self._rate = rate

    def synthesize(self, text: str, *, conn_options=None) -> "tts.ChunkedStream":
        return EdgeTTSStream(
            tts=self, input_text=text, voice=self._voice, rate=self._rate,
            conn_options=conn_options or self._sanitize_options(),
        )


class EdgeTTSStream(tts.ChunkedStream):
    def __init__(self, *, tts: EdgeTTS, input_text: str, voice: str, rate: str, conn_options):
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._voice = voice
        self._rate = rate

    async def _run(self, output_emitter):
        try:
            logger.info("EdgeTTS synthesizing: %s", self._input_text[:80])

            # Initialize the emitter before pushing any data
            output_emitter.initialize(
                request_id=str(uuid.uuid4()),
                sample_rate=SAMPLE_RATE,
                num_channels=NUM_CHANNELS,
                mime_type="audio/pcm",
            )

            communicate = edge_tts.Communicate(self._input_text, self._voice, rate=self._rate)
            mp3_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    mp3_data += chunk["data"]

            if not mp3_data:
                logger.warning("EdgeTTS returned no audio data")
                return

            logger.info("EdgeTTS got %d bytes of MP3, converting to PCM...", len(mp3_data))
            pcm_data = _mp3_bytes_to_pcm(mp3_data)

            if not pcm_data:
                logger.warning("EdgeTTS PCM conversion returned no data")
                return

            logger.info("EdgeTTS pushing %d bytes of PCM audio", len(pcm_data))

            # Push raw PCM bytes in chunks for smooth playback
            chunk_samples = SAMPLE_RATE // 5  # 200ms chunks
            chunk_bytes = chunk_samples * 2   # 16-bit = 2 bytes per sample

            for i in range(0, len(pcm_data), chunk_bytes):
                audio_chunk = pcm_data[i:i + chunk_bytes]
                if len(audio_chunk) > 0:
                    output_emitter.push(audio_chunk)

            logger.info("EdgeTTS audio pushed successfully")
        except Exception as e:
            logger.error("EdgeTTS error: %s", e, exc_info=True)
            raise
