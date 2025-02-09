from channels.generic.websocket import AsyncWebsocketConsumer
from google.cloud import speech
from channels.db import database_sync_to_async
import asyncio
import json
import queue
import threading
import base64

class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Initializing connection...")
        self.client = speech.SpeechClient()
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
                sample_rate_hertz=8000,
                language_code="en-US",
                enable_automatic_punctuation=True,
            ),
            interim_results=True,
        )
        
        self.audio_queue = queue.Queue()
        self.stream_active = True
        await self.accept()
        print("WebSocket connected!")

    async def disconnect(self, close_code):
        self.stream_active = False
        print(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if text_data:
                print(f"Received text data: {text_data}")
                data = json.loads(text_data)
                if data.get('event') == 'start':
                    print("Stream started")
                    asyncio.create_task(self.process_audio_stream())
                elif data.get('event') == 'stop':
                    print("Stream stopped")
                    self.stream_active = False
                elif data.get('event') == 'media':
                    print("Received media event")
                    if 'payload' in data:
                        audio_data = base64.b64decode(data['payload'])
                        self.audio_queue.put(audio_data)
                        print("Queued audio data")
            elif bytes_data:
                print("Received raw bytes data")
                self.audio_queue.put(bytes_data)
                print("Queued raw bytes data")
        except Exception as e:
            print(f"Error in receive: {e}")

    async def process_audio_stream(self):
        print("Starting audio processing...")
        
        def request_generator():
            while self.stream_active:
                try:
                    # Non-blocking get with timeout
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                    print("Got audio chunk from queue")
                    yield speech.StreamingRecognizeRequest(
                        audio_content=audio_chunk
                    )
                except queue.Empty:
                    print("Queue empty, waiting for more audio...")
                    continue
                except Exception as e:
                    print(f"Error in generator: {e}")
                    break

        try:
            print("Starting speech recognition stream...")
            responses = self.client.streaming_recognize(
                self.streaming_config,
                request_generator()
            )
            print("Recognition stream started")

            for response in responses:
                if not self.stream_active:
                    break
                
                if response.results:
                    for result in response.results:
                        transcript = result.alternatives[0].transcript
                        is_final = result.is_final
                        
                        print(f"Transcript: {transcript} ({'final' if is_final else 'interim'})")
                        
                        await self.send(json.dumps({
                            'transcript': transcript,
                            'is_final': is_final
                        }))

                        if is_final:
                            await self.save_transcription(transcript)

        except Exception as e:
            print(f"Error in audio processing: {e}")
            print(f"Error details: {str(e)}")
            await self.send(json.dumps({
                'error': str(e)
            }))

    async def save_transcription(self, transcript):
        try:
            call_sid = self.scope['url_route']['kwargs']['call_sid']
            await database_sync_to_async(CallTranscription.objects.create)(
                transcript=transcript,
                call_sid=call_sid
            )
            print(f"Saved transcription: {transcript}")
        except Exception as e:
            print(f"Error saving transcription: {e}")