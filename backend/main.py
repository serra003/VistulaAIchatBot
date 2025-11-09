from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import requests
import re
from dotenv import load_dotenv

load_dotenv("api.env")  # get the api from env file

app = FastAPI() # start fastapi app here

origins = [ # setting up cors here for frontend, will change it later to match alejandro's code
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    with open("../data/kb.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
except FileNotFoundError:
    kb = []
    
# load api keys     
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print("OPENROUTER_API_KEY loaded:", OPENROUTER_API_KEY is not None)
print("DEEPSEEK_API_KEY loaded:", DEEPSEEK_API_KEY is not None)


class Question(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Backend is working!"}

def match_kb(user_question: str):
    """
    Try to find an answer in the knowledge base that matches the user's question.
    """
    user_question_lower = user_question.lower().strip()
    user_words = set(re.findall(r"\b\w+\b", user_question_lower))

    stopwords = {    # stopwoords to ignore in questions (not mixing stuff up)
        "the", "is", "at", "where", "can", "i", "get", "to", "my", "a", "an",
        "on", "of", "for", "and", "how", "do", "you", "in", "office"
    }
    user_words = {w for w in user_words if w not in stopwords}

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greet in user_question_lower for greet in greetings):
        return "Hello! How may I help you?"

    best_match = None
    best_score = 0
    for item in kb:
        kb_words = set(re.findall(r"\b\w+\b", item.get("question", "").lower()))
        kb_words = {w for w in kb_words if w not in stopwords}
        overlap = len(user_words & kb_words)
        score = overlap / len(kb_words) if kb_words else 0

        keywords = [k.lower() for k in item.get("keywords", [])]
        if any(kw in user_question_lower for kw in keywords):
            score += 0.3

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score > 0.15:
        return best_match["answer"]
    return None

@app.post("/ask")
def ask_question(question: Question):
    user_question = question.question.strip()
    print("Received question:", user_question)

# attempt to get answer from the kb 
    kb_answer = match_kb(user_question)
    if kb_answer:
        print("Answer from KB:", kb_answer)
        return {"answer": kb_answer}

    # choose which api (ask bakr abt this)
    if OPENROUTER_API_KEY:
        url = "https://openrouter.ai/api/v1/chat/completions"
        api_key = OPENROUTER_API_KEY
        model = "gpt-4o-mini"
    elif DEEPSEEK_API_KEY:
        url = "https://api.deepseek.com/v1/chat/completions"
        api_key = DEEPSEEK_API_KEY
        model = "deepseek-chat"
    else:
        print("No API key set")
        return {"answer": "API key not found. Set DEEPSEEK_API_KEY or OPENROUTER_API_KEY."}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for Vistula University students."},
            {"role": "user", "content": user_question}
        ],
        "stream": False
    }
 
    # response handling, error messages etc
    try:
        print("Sending request to API...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print("Raw response status:", response.status_code)

        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError:
            return {"answer": f"API returned non-JSON response. Content starts with:\n{response.text[:500]}"}

        answer = None
        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0].get("message", {}).get("content")
        elif "result" in data:
            answer = data.get("result")

        if answer:
            print("Answer from API:", answer)
            return {"answer": answer.strip()}
        elif "error" in data:
            print("API error:", data["error"])
            return {"answer": f"API error: {data['error']}"}
        else:
            print("Unknown response structure:", data)
            return {"answer": "I don't know yet."}

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
        return {"answer": f"API request error: {e}"}