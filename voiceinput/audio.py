import threading

import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, silence_threshold: float = 500.0):
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def _callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        with self._lock:
            self._chunks.append(indata.copy())

    def start(self) -> None:
        with self._lock:
            self._chunks = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray | None:
        if self._stream is None:
            return None
        self._stream.stop()
        self._stream.close()
        self._stream = None

        with self._lock:
            if not self._chunks:
                return None
            audio = np.concatenate(self._chunks, axis=0).flatten()

        rms = np.sqrt(np.mean(audio**2)) * 32768  # scale to int16 range for threshold
        if rms < self.silence_threshold:
            return None

        return audio
