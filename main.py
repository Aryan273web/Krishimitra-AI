import os
import re
import requests
from fastapi import FastAPI, Request, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

# Import your agent executor from agent.py
from agent import agent_executor

load_dotenv()

app = FastAPI(title="KrishiMitra Backend Engine")

# Enable CORS for web frontend (Streamlit / Web UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NGROK_BASE_URL = os.getenv("NGROK_BASE_URL", "https://disinfect-unelected-embassy.ngrok-free.dev")

# -------------------------------------------------------------
# 1. DIRECT API ENDPOINT (For Web App / Streamlit UI)
# -------------------------------------------------------------
@app.post("/api/chat-text")
async def chat_text(request: Request):
    """Handles standard text queries from web UI"""
    data = await request.json()
    user_input = data.get("prompt", "")
    
    if not user_input:
        return {"response": "Please provide a valid query."}

    try:
        result = agent_executor.invoke({"input": user_input})
        bot_response = result.get("output", "Could not process request.")
    except Exception as e:
        bot_response = f"Error processing query: {str(e)}"
        
    return {"response": bot_response}


# -------------------------------------------------------------
# 2. TELEGRAM BOT WEBHOOK ENDPOINT
# -------------------------------------------------------------
@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Telegram Webhook Handler with Clean Code-Block Formatting"""
    data = await request.json()
    
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_text = message.get("text", "")
    
    if chat_id and user_text:
        try:
            result = agent_executor.invoke({"input": user_text})
            bot_response = str(result.get("output", "Could not process request.")).strip()
        except Exception as e:
            bot_response = "Sorry, market servers are currently busy. Please try again."

        # Wrap Markdown tables inside code blocks for Telegram compatibility
        lines = bot_response.split('\n')
        formatted_lines = []
        in_table = False
        
        for line in lines:
            if line.strip().startswith('|'):
                if not in_table:
                    formatted_lines.append('```')
                    in_table = True
                formatted_lines.append(line)
            else:
                if in_table:
                    formatted_lines.append('```')
                    in_table = False
                formatted_lines.append(line)
        if in_table:
            formatted_lines.append('```')

        clean_response = '\n'.join(formatted_lines)

        # Dispatch back to Telegram
        telegram_url = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": clean_response,
            "parse_mode": "Markdown"
        }
        requests.post(telegram_url, json=payload)

    return {"status": "ok"}


# -------------------------------------------------------------
# 3. TWILIO PHONE CALL (IVR) ENDPOINTS
# -------------------------------------------------------------
@app.post("/webhook/ivr/welcome")
async def ivr_welcome():
    """Initial Greeting when caller connects to the helpline"""
    twiml = VoiceResponse()
    
    # Absolute URL destination avoids Twilio resolution timeouts
    process_voice_url = f"{NGROK_BASE_URL.rstrip('/')}/webhook/ivr/process-voice"
    
    gather = Gather(
        input="speech",
        action=process_voice_url,
        method="POST",
        language="hi-IN",
        speech_timeout="auto"
    )
    gather.say(
        "Namaste! Welcome to Krishi Mitra helpline. Please tell us which crop and state you want market rates for.", 
        voice="Polly.Aditi", 
        language="hi-IN"
    )
    
    twiml.append(gather)
    twiml.say("We did not hear any speech. Please call back. Thank you!", voice="Polly.Aditi", language="hi-IN")
    return Response(content=str(twiml), media_type="text/xml")


@app.post("/webhook/ivr/process-voice")
async def ivr_process_voice(SpeechResult: str = Form(default="")):
    """Processes spoken speech-to-text input over the phone call"""
    twiml = VoiceResponse()
    
    if not SpeechResult:
        twiml.say("Sorry, I could not hear your speech clearly. Please try calling again.", voice="Polly.Aditi", language="hi-IN")
        return Response(content=str(twiml), media_type="text/xml")

    try:
        # Pass transcribed voice text directly to LangChain Agent
        result = agent_executor.invoke({"input": SpeechResult})
        bot_response = str(result.get("output", "Could not fetch market data.")).strip()
        
        # Clean markdown formatting tags so Amazon Polly reads cleanly
        bot_response = re.sub(r'[\#\*\_\`\|]', '', bot_response)
        
        # Keep speech output concise to prevent call dropping
        if len(bot_response) > 300:
            bot_response = bot_response[:280] + "... and more."
            
    except Exception as e:
        bot_response = "Sorry, market services are currently busy. Please try again later."

    # Speak response to caller
    twiml.say(bot_response, voice="Polly.Aditi", language="hi-IN")
    twiml.say("Thank you for calling Krishi Mitra. Have a great day!", voice="Polly.Aditi", language="hi-IN")
    twiml.hangup()

    return Response(content=str(twiml), media_type="text/xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)