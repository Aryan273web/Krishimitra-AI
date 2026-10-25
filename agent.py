import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from tools import fetch_mandi_prices

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing from .env file!")

# Initialize Groq LLM using active model endpoint
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    groq_api_key=groq_api_key,
    temperature=0.1
)

# Register Mandi Price Tool
tools = [fetch_mandi_prices]

# System Prompt
SYSTEM_PROMPT = """You are KrishiMitra (कृषि मित्र), an agricultural assistant helping farmers in India.

CRITICAL LANGUAGE & BEHAVIOR RULES:
1. MATCH THE USER'S LANGUAGE:
   - If the user speaks/types in a specific language or script (Hindi, Punjabi, Marathi, Kannada, Malayalam, Tamil, Telugu, etc.), ALWAYS reply strictly in that same language and native script.
   - If the user asks in English but mentions a specific Indian state (e.g., "Punjab", "Uttar Pradesh", "Maharashtra"), provide the response in English, but ALSO immediately follow it with the regional language translation (e.g., Punjabi for Punjab, Hindi for UP).
   
2. TOOL USAGE:
   - Call the `fetch_mandi_prices` tool whenever the user asks for mandi rates, crop prices, or market updates.
   - Always map regional crop and state names to their proper English names before passing them as arguments to the tool (e.g., "आलू" -> "Potato", "गेहूं" / "ਕਣਕ" -> "Wheat", "पंजाब" -> "Punjab").

3. FORMATTING:
   - Keep answers simple, practical, and clear for farmers.
   - State the Mandi name, Modal price per quintal, and per kg equivalent.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Construct Agent Executor
agent = create_tool_calling_agent(llm, tools, prompt)

# Export as 'agent_executor' so main.py imports it cleanly
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)