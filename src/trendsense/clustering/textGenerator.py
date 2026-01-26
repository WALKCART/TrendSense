from openai import OpenAI
import pandas as pd
from transformers import pipeline
import torch
import os
from dotenv import load_dotenv
load_dotenv()

key = ''
'''with open('api_key.txt', 'r') as file:
    key += file.read()'''

# client = OpenAI(api_key=key)
client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)

device = 'mps' if torch.backends.mps.is_available() else 'cpu'

def warm_up():
    try:
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": ""}]
        )
        print("Model warmed up.")
    except Exception as e:
        print(f"Warmup failed: {e}")

def get_chatbot_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

    return response

def get_title(info: str):
    prompt = 'The following are the summaries of multiple news articles'
    prompt += 'Give me a title in 2-10 words that best describes this collection of articles.'
    prompt += 'Make sure to give me only the title and nothign else.\n\n'
    prompt += info
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content

    return response

