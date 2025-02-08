from openai import OpenAI
from pydub import AudioSegment
import simpleaudio as sa
import io
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Generate streaming response
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world! This is a streaming test.",
)

# Create an in-memory byte buffer
audio_data = io.BytesIO()
for chunk in response.iter_bytes():  # Stream chunks
    audio_data.write(chunk)

# Load the audio into an AudioSegment (MP3 format)
audio_data.seek(0)
audio_segment = AudioSegment.from_file(audio_data, format="mp3")

# Convert AudioSegment to raw audio data
raw_data = audio_segment.raw_data

# Play the audio using simpleaudio
play_obj = sa.play_buffer(raw_data, num_channels=audio_segment.channels,
                          bytes_per_sample=audio_segment.sample_width,
                          sample_rate=audio_segment.frame_rate)

# Wait for playback to finish
play_obj.wait_done()
