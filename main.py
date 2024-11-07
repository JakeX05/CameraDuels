from image_processing import load_image, generate_image_description
from openai_helper import generate_caption
from airtable import get_person_info
from slack import get_channel_info
from slack import get_latest_message_and_image, download_image, replace_user_ids_with_names, extract_username, send_message, get_latest_message_ts, send_threaded_message
import os
import requests
from PIL import Image


def main(image_path):
    # Load image
    image = load_image(image_path)
    if image is None:
        print("Failed to load image.")
        return

    message, image_url = get_latest_message_and_image("C032FEPFWUE")
    message_timestamp = get_latest_message_ts("C032FEPFWUE")
    
    if message:
        print(f"Latest message: {message}")
    else:
        print("No recent message found.")
    
    # If an image URL is present, download the image
    if image_url:
        output_file = "most_recent_image.jpg"
        download_image(image_url, output_file)
    else:
        print("No recent image found.")

    formatted_message = replace_user_ids_with_names(message)
    name = extract_username(formatted_message)
    print(name)

    person_info = get_person_info(name)
    
    #Generate caption based on the description
    caption = generate_caption(person_info, name)
    print("Generated Caption:", caption)

    #send_threaded_message("C032FEPFWUE", caption, message_timestamp)

    

if __name__ == "__main__":
    # Replace this path with your actual image path
    main("/Users/jakexiang/Downloads/BingBong.jpg")