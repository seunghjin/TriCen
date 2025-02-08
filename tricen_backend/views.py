from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.voice_response import VoiceResponse, Gather

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
    gather.say("Please speak your message. I will transcribe it for you.")
    
    # Add the Gather to the response
    response.append(gather)
    
    # If no input is received, redirect back to the start
    response.redirect('/api/voice/incoming/')
    
    print(f"Response: {str(response)}")
    return HttpResponse(str(response), content_type='text/xml')

@csrf_exempt
@require_POST
def handle_transcription_result(request):
    # Get the speech recognition results
    speech_result = request.POST.get('SpeechResult')
    confidence = request.POST.get('Confidence')
    
    print(f"Transcription received: {speech_result}")
    print(f"Confidence: {confidence}")
    
    response = VoiceResponse()
    
    if speech_result:
        # Read back what was transcribed
        response.say(f"I heard: {speech_result}")
        
        # Start another Gather for continuous conversation
        gather = Gather(
            input='speech',
            language='en-US',
            enhanced=True,
            speechTimeout='auto',
            action='/api/voice/transcription_result/'
        )
        gather.say("Please continue speaking, or hang up to end.")
        response.append(gather)
    else:
        response.say("I didn't catch that. Let's try again.")
        response.redirect('/api/voice/incoming/')
    
    return HttpResponse(str(response), content_type='text/xml')