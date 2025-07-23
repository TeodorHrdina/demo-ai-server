from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI()

class ChatRequest(BaseModel):
    charName: str
    emotion: str
    chatHistory: list
    userCommunication: str

@app.post("/api/chatted")
async def chatted(request: ChatRequest):
    openRouterApiKey = os.getenv("OPENROUTER_API_KEY")

    if not openRouterApiKey:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")

    client = OpenAI(
        api_key=openRouterApiKey,
        base_url="https://openrouter.ai/api/v1/",
    )

    messages = [
        {"role": "system", "content": f"You are a character named {request.charName} and you now feel {request.emotion}. Please output a new response this character would give in a response attribute based on the given chat history and add a json parameter named emotion that can only have variables: Flirty, Sad, Angry, Happy and Disgusted."}
    ]

    for entry in request.chatHistory:
        messages.append(entry)

    messages.append({"role": "user", "content": request.userCommunication})

    try:
        completion = client.chat.completions.create(
            model="mistralai/mistral-nemo",
            response_format={"type": "json_object"},
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_data = json.loads(completion.choices[0].message.content)
    return response_data
