import openai
from config import OPENAI_API_KEY
import base64
import json


openai.api_key = OPENAI_API_KEY
file_path = "/Users/jakexiang/Downloads/CameraDuels/most_recent_image.jpg"


def generate_caption(person_description, name):    
    try:
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that can analyze images and combine insights with text data provided to give a comprehensive response",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", 
                        "text": (
                            "{name} is in the image below. Create a short, light-hearted poem that captures both "
                            "what you can infer from the image and the information provided about {name}. Please "
                            "describe both the visual aspects and any relevant details from Bing's description.")
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            },
                        },
                        {
                            "type": "text",
                            "text": f"{person_description}"
                        },
                    ],
                },
            ],
            max_tokens=300,
        )
        caption = response.choices[0].message.content.strip()
        return caption
    except Exception as e:
        print(f"Error generating caption: {e}")
        return None
