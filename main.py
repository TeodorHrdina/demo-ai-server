from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

jsonObject :dict = json.load(open("sample-request.json"))
openRouterApiKey = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=openRouterApiKey,
    base_url="https://openrouter.ai/api/v1/",
)
messages = [{"role": "system", "content": "You are a character named " +  jsonObject["charName"] + " and you now feel " + jsonObject["emotion"] + ". Please output a new response this character would give in a response attribute based on the given chat history and add a json parameter named emotion that can only have variables: Flirty, Sad, Angry, Happy and Disgusted."}]

for entry in jsonObject["chatHistory"]:
    messages.append(entry)
    
messages.append({"role": "user", "content": jsonObject["userCommunication"]})    
completion = client.chat.completions.create(
    model="mistralai/mistral-nemo",
    response_format={ "type": "json_object" },
    messages=messages
)


print(completion.choices[0].message.content)