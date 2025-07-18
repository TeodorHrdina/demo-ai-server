from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import socket
import sys
import requests

load_dotenv()

# Socket listening things
HOST = ''
PORT = 5000

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    listenSocket.bind((HOST, PORT))

except socket.error as message:
    print('Bind failed. Error Code : ' 
          + str(message[0]) + ' Message ' 
          + message[1])
    sys.exit()

print("Socket bound.")

# Posting responses things
postPort = 443
url = "https://localhost:"
headers = {"Content-type": "application/json"}
data = None

while (True):
    listenSocket.listen(9)

    connection, address = listenSocket.accept()
    print("Connected with " + address[0] + ":" + str(address[1]))

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


    # print(completion.choices[0].message.content)
    data = completion.choices[0].message.content
    response = requests.post(url + str(postPort), headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    listenSocket.close()