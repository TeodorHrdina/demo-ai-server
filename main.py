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

completion = client.chat.completions.create(
    model="mistralai/mistral-nemo",
    messages=[
        {"role": "assistant", "content": "You are a helpful animal fact dispenser."},
        {
            "role": "user",
            "content": "Give me random animal fun fact.",
        },
    ],
)


print(completion.choices[0].message.content)