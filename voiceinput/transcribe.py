import io
import wave

import numpy as np

HALLUCINATION_PHRASES = {
    "",
    "thank you",
    "thank you.",
    "thanks.",
    "thanks for watching.",
    "thank you for watching.",
    "you",
    "bye.",
    "bye",
    "the end.",
    "...",
}


def _is_hallucination(text: str) -> bool:
    return text.lower().strip() in HALLUCINATION_PHRASES


def _audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    int16_audio = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_audio.tobytes())
    return buf.getvalue()


class GroqTranscriber:
    def __init__(self, api_key: str):
        import httpx
        self._api_key = api_key
        self._client = httpx.Client(timeout=30.0)

    def transcribe(self, audio: np.ndarray) -> str | None:
        wav_bytes = _audio_to_wav_bytes(audio)
        response = self._client.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": "whisper-large-v3", "response_format": "text", "language": "en"},
        )
        response.raise_for_status()
        text = response.text.strip()
        if _is_hallucination(text):
            return None
        return text


class LocalTranscriber:
    def __init__(self, model_size: str = "base.en"):
        from faster_whisper import WhisperModel
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio: np.ndarray) -> str | None:
        segments, _ = self.model.transcribe(audio, beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if _is_hallucination(text):
            return None
        return text


def create_transcriber(backend: str, model_size: str = "base.en", groq_api_key: str = ""):
    if backend == "groq":
        if not groq_api_key:
            raise RuntimeError("Groq API key required. Set GROQ_API_KEY or use --groq-api-key.")
        return GroqTranscriber(groq_api_key)
    return LocalTranscriber(model_size)
