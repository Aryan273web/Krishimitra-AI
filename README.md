 KrishiMitra AI — Multi-Channel Smart Agricultural Assistant

> **Hackathon Track:** Open Innovation Track  
> **Developer:** Aryan Agarwal (1st Year, Thapar Institute of Engineering & Technology)  
> **Domain:** Agriculture

 Problem Statement
Smallholder farmers in India often face severe information asymmetry regarding real-time commodity prices across regional mandis. Compounded by textual literacy barriers (~28% in rural agri-apps) and a lack of smartphone data access, existing digital solutions fail to reach the last mile.

 Solution Overview
**KrishiMitra AI** is a zero-barrier, multi-channel AI gateway that delivers real-time mandi prices, market intelligence, and agricultural advisory in the farmer's regional language:

-  Voice Helpline (Twilio IVR):** Feature-phone support allowing farmers to dial a dedicated number and receive live voice-guided crop rates.
-  Instant Messaging (Telegram Bot):** Fast query handling, automated price tables, and audio/voice-note processing.
   Web UI (Streamlit):** Lightweight dashboard for extension workers and cooperative leads.

---

## Tech Stack & Architecture
- **Backend Framework:** FastAPI (Asynchronous microservices engine)
- **AI Agent Framework:** LangChain & Groq Llama-3 models
- **Speech Synthesis:** Amazon Polly (`Aditi` Hindi/English voice engine)
- **Voice Integration:** Twilio Voice API & TwiML webhook routing
- **Data Source:** Real-time AGMARKNET portal data

---

##  Project Structure
```text
Krishimitra-backend/
├── main.py            # FastAPI entry point, Twilio IVR & Telegram webhooks
├── agent.py           # LangChain Groq AI agent routing logic
├── tools.py           # AGMARKNET live price fetching tools
└── requirements.txt   # Python dependencies
