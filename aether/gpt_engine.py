from openai import OpenAI
import os

client = OpenAI(api_key="YOUR_OPENAI_API_KEY_HERE")
def call_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o", "gpt-4.1", etc.
        messages=[
            {"role": "system", "content": "You are a helpful AI agent."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()