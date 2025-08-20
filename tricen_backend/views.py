from django.http import HttpResponse
from django.http.response import FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.voice_response import VoiceResponse, Gather

import os
from dotenv import load_dotenv

import tempfile

import openai
from urllib.parse import urljoin

import logging

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

TRANSFER_NUMBER = os.getenv('TRANSFER_NUMBER')

@csrf_exempt
@require_POST
def handle_incoming_call(request):
    print("Incoming call received!")
    print(f"POST data: {request.POST}")
    
    response = VoiceResponse()
    
    # Create a Gather verb with specific parameters
    gather = Gather(
        input='speech',
        language='en-US',
        enhanced=True,  # Uses Twilio's enhanced speech recognition
        speechTimeout='auto',  # Automatically determines end of speech
        action='/api/voice/transcription_result/',  # Where to send the results
    )
    
    # Add prompts to the Gather
    gather.say("Hi, My Name is Tricen. What's your name?")
    # try:
    #     conversation = Conversation.objects.get(caller_id=call_sid)
    #     if conversation.needs_transfer:
    #         response.say("Connecting you with a representative. Please hold.")
    #         dial = response.dial()
    #         dial.number(TRANSFER_NUMBER)  # Replace with your support number
    #         return HttpResponse(str(response), content_type='text/xml')
    # except Conversation.DoesNotExist:
    #     pass  # If conversation doesn't exist, continue with normal flow
    
    # Add the Gather to the response
    response.append(gather)
    
    # If no input is received, redirect back to the start
    response.redirect('/api/voice/incoming/')
    
    print(f"Response: {str(response)}")
    return HttpResponse(str(response), content_type='text/xml')


load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

@csrf_exempt
@require_POST
def handle_transcription_result(request):
    speech_result = request.POST.get('SpeechResult')
    confidence = float(request.POST.get('Confidence', 0))
    call_sid = request.POST.get('CallSid')
    caller = request.POST.get('Caller')
    
    logger.debug(f"Received speech: {speech_result} with confidence: {confidence}")
    
    response = VoiceResponse()

    print(f"Speech result: {speech_result}")
    
    try:
        conversation = Conversation.objects.get(caller_id=call_sid)
        if conversation.needs_transfer:
            conversation.delete()
            response.say("Connecting you with a representative. Please hold.")
            dial = response.dial()
            dial.number(TRANSFER_NUMBER)

            # delete the conversation after transfer

            return HttpResponse(str(response), content_type='text/xml')
    except Conversation.DoesNotExist:
        pass  # If conversation doesn't exist, continue with normal flow

    if speech_result:
        try:
            # Get GPT response
            message = get_gpt_response(speech_result)
            print(f"GPT Response: {message}")
            

            #db changes start
            conversation, created = Conversation.objects.get_or_create(
                caller_id=call_sid,
                defaults={
                    'phone_number': caller,
                    'contentUser': '[]',
                    'contentAI': '[]'
                }
            )
            conversation.add_user_message(speech_result)
            conversation.add_ai_message(message)

            #db chages end
            
            # Generate TTS audio and save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            print(f"Created temp file: {temp_file.name}")
            
            tts_response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=message,
            )
            
            # Save the audio file
            tts_response.stream_to_file(temp_file.name)
            print(f"Saved audio to file: {temp_file.name}")
            
            # Get your server's base URL - should be your ngrok URL
            base_url = request.build_absolute_uri('/').rstrip('/')
            print(f"Base URL: {base_url}")
            
            # Create the audio URL
            audio_url = f"{base_url}/api/voice/audio/{os.path.basename(temp_file.name)}"
            print(f"Audio URL: {audio_url}")
            
            # Play the audio file
            response.play(audio_url)
            
            # After playing, gather next input
            gather = Gather(
                input='speech',
                language='en-US',
                enhanced=True,
                speechTimeout='auto',
                action='/api/voice/transcription_result/'
            )
            # gather.say("Please continue speaking, or hang up to end.")
            response.append(gather)
            
        except Exception as e:
            logger.error(f"Error in handle_transcription_result: {str(e)}", exc_info=True)
            response.say(f"I apologize, but I encountered an error: {str(e)}")
            response.redirect('/api/voice/incoming/')
    else:
        response.say("I didn't catch that clearly. Let's try again.")
        response.redirect('/api/voice/incoming/')
    
    logger.debug(f"Final TwiML response: {str(response)}")
    return HttpResponse(str(response), content_type='text/xml')

@csrf_exempt
def serve_audio(request, filename):
    """Serve the audio file"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    logger.debug(f"Attempting to serve audio file: {file_path}")
    
    if os.path.exists(file_path):
        logger.debug(f"File exists, serving: {file_path}")
        try:
            # Open the file and create the response
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type='audio/mpeg')
            
            # Delete the file after it's served
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
            
            return response
        except Exception as e:
            logger.error(f"Error serving audio file: {str(e)}", exc_info=True)
            return HttpResponse("Error serving audio file", status=500)
    else:
        logger.error(f"Audio file not found: {file_path}")
        return HttpResponse("Audio file not found", status=404)


def get_gpt_response(user_input):
    """
    Sends user input to OpenAI's Chat API and returns a response.
    """
    try:
        messages = [
            {"role": "system", "content": "You are a compassionate and supportive mental health professional. Keep your responses very brief (maximum 2-3 sentences) and conversational, as they will be spoken over the phone. Avoid lists or lengthy explanations. Focus on empathy and one key supportive message."},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Error with OpenAI API: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

from django.http import JsonResponse
from .models import Conversation
from django.core.exceptions import ObjectDoesNotExist

def get_conversations(request):
    try:
        conversations = Conversation.objects.all()
        data = [{
            'caller_id': conv.caller_id,
            'phone_number': conv.phone_number,
            'contentUser': conv.get_user_content(),
            'contentAI': conv.get_ai_content(),
            'timestamp': conv.timestamp.isoformat()
        } for conv in conversations]
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error in get_conversations: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_conversation(request, caller_id):
    try:
        # Get single conversation by caller_id
        conversation = Conversation.objects.get(caller_id=caller_id)
        
        # Get the conversation content
        contentUser = conversation.get_user_content()
        contentAI = conversation.get_ai_content()

        # Build the conversation script
        overall_script = ""
        for i in range(len(contentUser)):
            overall_script += f"User: {contentUser[i]}\n"
            if i < len(contentAI):
                overall_script += f"AI: {contentAI[i]}\n"

        # Get summary from GPT
        system_prompt = """Your one goal is to provide a brief summary of the conversation. 
            Your output should have the following format: 
            'Name: [name], Small_Description: [small description of the problem the user is having], 
            Summary: [summary of overall conversation, make sure to include key details and turning points if any]' 
            Do not include any other information in your response."""
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": overall_script}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        summary = response.choices[0].message.content

        # Parse the summary
        try:
            parsed_summary = summary.split(", ")
            name = parsed_summary[0].split(": ")[1]
            small_description = parsed_summary[1].split(": ")[1]
            summary = parsed_summary[2].split(": ")[1]
        except IndexError:
            # Handle malformed summary gracefully
            name = "Unknown"
            small_description = "Conversation in progress"
            summary = "Unable to generate summary"

        return JsonResponse({
            'name': name,
            'small_description': small_description,
            'summary': summary,
            'conversation': {
                'user_messages': contentUser,
                'ai_messages': contentAI
            }
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({
            'error': f'Conversation with ID {caller_id} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'An error occurred while retrieving the conversation'
        }, status=500)

@csrf_exempt
def initiate_transfer(request, call_sid):
    try:
        # Create a TwiML response
        response = VoiceResponse()
        
        # Add transfer message
        response.say("Transferring you to a human representative. Please hold.")
        
        # Implement the transfer
        dial = response.dial()
        # Replace with your actual support number
        dial.number(TRANSFER_NUMBER)
        
        # Update the conversation status if needed
        conversation = Conversation.objects.get(caller_id=call_sid)
        conversation.needs_transfer = True
        conversation.transfer_reason = "Manual transfer initiated from dashboard"
        conversation.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Transfer initiated',
            'twiml': str(response)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)