import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue
import sys

SAMPLE_RATE = 16000
BLOCK_DURATION = 5  # seconds per caption chunk

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())

def main():
    print("Loading model...")
    model = WhisperModel("base", compute_type="int8")

    print("Listening... Speak now.")
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback
    ):
        buffer = np.empty((0, 1), dtype=np.float32)

        while True:
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data))

            if len(buffer) >= SAMPLE_RATE * BLOCK_DURATION:
                audio_chunk = buffer[:SAMPLE_RATE * BLOCK_DURATION]
                buffer = buffer[SAMPLE_RATE * BLOCK_DURATION:]

                segments, _ = model.transcribe(
                    audio_chunk.flatten(),
                    language="en"
                )

                for segment in segments:
                    print("CAPTION:", segment.text.strip())

if __name__ == "__main__":
    main()
