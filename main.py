from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    charName: str
    emotion: str
    chatHistory: list
    userCommunication: str
    stream: bool = False

async def generate_stream(client, messages):
    try:
        stream = client.chat.completions.create(
            model=os.getenv("CHAT_MODEL", "mistralai/mistral-nemo"),
            messages=messages,
            stream=True,
            timeout=60
        )
        
        collected_content = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected_content += content
                yield f"data: {json.dumps({'content': content, 'type': 'chunk'})}\n\n"
        
        try:
            response_data = json.loads(collected_content)
            if not isinstance(response_data, dict) or "response" not in response_data:
                yield f"data: {json.dumps({'content': json.dumps({'response': 'Server was unable to get a response. Please try again or adjust your query.', 'emotion': 'Happy'}), 'type': 'final'})}\n\n"
            else:
                if "emotion" not in response_data or response_data["emotion"] not in ["Flirty", "Sad", "Angry", "Happy", "Disgusted"]:
                    response_data["emotion"] = "Happy"
                yield f"data: {json.dumps({'content': json.dumps(response_data), 'type': 'final'})}\n\n"
        except json.JSONDecodeError:
            yield f"data: {json.dumps({'content': json.dumps({'response': 'Server was unable to get a response. Please try again or adjust your query.', 'emotion': 'Happy'}), 'type': 'final'})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'content': json.dumps({'response': 'Server was unable to get a response. Please try again or adjust your query.', 'emotion': 'Happy'}), 'type': 'final'})}\n\n"

@app.post("/api/chatted")
async def chatted(request: ChatRequest):
    openRouterApiKey = os.getenv("OPENROUTER_API_KEY")

    if not openRouterApiKey:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")

    client = OpenAI(
        api_key=openRouterApiKey,
        base_url="https://openrouter.ai/api/v1/",
    )

    system_prompt = os.getenv("SYSTEM_PROMPT", "You are a character named {charName} and you now feel {emotion}. Please output a new response this character would give in a response attribute based on the given chat history and add a json parameter named emotion that can only have variables: Flirty, Sad, Angry, Happy and Disgusted.")
    
    messages = [
        {"role": "system", "content": system_prompt.format(charName=request.charName, emotion=request.emotion)}
    ]

    for entry in request.chatHistory:
        messages.append(entry)

    messages.append({"role": "user", "content": request.userCommunication})

    if request.stream:
        return StreamingResponse(
            generate_stream(client, messages),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    try:
        completion = client.chat.completions.create(
            model=os.getenv("CHAT_MODEL", "mistralai/mistral-nemo"),
            response_format={"type": "json_object"},
            messages=messages,
            timeout=60
        )
        
        response_content = completion.choices[0].message.content
        
        if not response_content or response_content.strip() == "":
            return {
                "response": "Server was unable to get a response. Please try again or adjust your query.",
                "emotion": "Happy"
            }
        
        try:
            response_data = json.loads(response_content)
            
            if not isinstance(response_data, dict) or "response" not in response_data:
                return {
                    "response": "Server was unable to get a response. Please try again or adjust your query.",
                    "emotion": "Happy"
                }
            
            if "emotion" not in response_data or response_data["emotion"] not in ["Flirty", "Sad", "Angry", "Happy", "Disgusted"]:
                response_data["emotion"] = "Happy"
            
            return response_data
            
        except json.JSONDecodeError:
            return {
                "response": "Server was unable to get a response. Please try again or adjust your query.",
                "emotion": "Happy"
            }
            
    except Exception as e:
        return {
            "response": "Server was unable to get a response. Please try again or adjust your query.",
            "emotion": "Happy"
        }
