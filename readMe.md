# TriCen
### HackDuke 2025
### By: Haruta Otaki, Satvik Matta, Seung Hyun Jin

## Inspiration
The rise in mental health crises invites individuals to reach out to hotlines and support groups. The main issue arises when there are not enough operators available to make sure each person's voice is heard. People who are put on hold will most likely hang up, leading to bottled feelings and amplified negative feelings and emotions. Due to this dilemma, we see an even greater rising, if not constant, rate of crises of mental health.

## What it does

Our application makes sure to keep a caller from hanging up by having an AI assistant act like an understanding and empathetic human while an operator becomes available. While doing so, the conversation between the two parties is recorded and transcribed. Both transcription and summary of the conversation become available to the operator so that they have the most up-to-date information about the caller when they are ready to take over. The data then proceeds to be deleted from the database to protect the caller's privacy rights.  

## How we built it

We mainly used Twilio API to facilitate calling and speech-to-text functionalities due to its cost-efficient nature for transcription and calls. We then utilized OpenAI's GPT 4o Turbo Model to take the conversations from the user to generate highly effective responses and summarize information for the operator. Finally, we leveraged OpenAI's text-to-speech (tts-1) model with a calm soothing "alloy" voice to relay the message back to the caller over the Twilio API.

```python
response = VoiceResponse()
 
gather = Gather(
        input='speech',
        language='en-US',
        enhanced=True,  # Uses Twilio's enhanced speech recognition
        speechTimeout='auto', 
        action='/api/voice/transcription_result/',  
)
```

## Challenges we ran into

The first challenge that we ran into was connecting web sockets to the Twilio API for answering incoming calls. This proved to be particularly difficult as the different technologies had distinct favorability for versions of dependencies. The second obstacle was relaying the text-to-speech transcription in chunks to achieve responses in real-time for the caller. With too much time in between responses, we would lose the inspiration of having a human-like responder. The last hurdle was incorporating the concept of warm transfers: connecting a third party to the preexisting call between the caller and the AI model. This proved to be difficult because we had to maintain information from the start of the conversation to the current moment when the caller was being transferred. To accomplish this, we created a dashboard allowing operators to click and see a quick summary of the problem, the full transcript of the conversation, and details of the caller.

## Accomplishments that we're proud of

One of our biggest accomplishments revolved around the idea of linking all the data together, keeping it from leaking or deteriorating while transcribing and creating overall summaries for each ongoing call. The biggest accomplishment, however, was scraping up a working demo within 24 hours with only 3 members. By the submission deadline, we successfully designed the entire workflow—from dialing the number to receiving real help—all while ensuring a polished front end.

## What we learned

We learned how fun software engineering is within a small time stamp alongside friends who understand each other's strengths and weaknesses. As most of our team had first-time hackers, we found ourselves wanting to do more and would join another hackathon in the blink of an eye. Lastly, we learned how to use different technologies and how to connect them to construct a real product.

## What's next for TriCen
The possibilities are endless. Our design showcases just one of countless applications for this tech stack. A slight adjustment to the prompt could seamlessly redirect calls to an insurance provider, collect critical details when emergency responders are overwhelmed, or grant global access to healthcare resources with a simple phone call. The potential is vast, and we’re eager to see where this project leads.