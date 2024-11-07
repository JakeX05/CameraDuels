import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import certifi
import ssl
import re

SLACK_TOKEN = os.getenv("SLACK_API_KEY")
CHANNEL_ID = "C032FEPFWUE"

ssl_context = ssl.create_default_context(cafile=certifi.where())
client = WebClient(token=SLACK_TOKEN, ssl=ssl_context)

def get_latest_message_and_image(channel_id):
    try:
        response = client.conversations_history(channel=channel_id, limit=1)
        message = response['messages'][0]['text']
        image_url = None

        # Check if there is a file attached to the latest message
        if 'files' in response['messages'][0]:
            file_info = response['messages'][0]['files'][0]
            if file_info['mimetype'].startswith("image"):
                image_url = file_info['url_private']
        
        return message, image_url

    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        return None, None

def download_image(url, output_path):
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }
    response = requests.get(url, headers=headers, verify=certifi.where())
    
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
        print(f"Image downloaded and saved as {output_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}, Message: {response.text}")

# Function to post a message in a Slack channel
def post_message_to_channel(channel_id, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "channel": channel_id,
        "text": text
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    if not data.get("ok"):
        print(f"Error posting message: {data.get('error')}")
    else:
        print("Message posted successfully.")


def get_channel_info():
    """Retrieve channel names and IDs from Slack."""
    url = "https://slack.com/api/conversations.list"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP request errors
        channels_data = response.json()

        if channels_data.get("ok"):
            channels = channels_data.get("channels", [])
            channel_info = {channel['name']: channel['id'] for channel in channels}
            return channel_info
        else:
            print("Error fetching channels:", channels_data.get("error"))
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_user_name(user_id):
    """Fetches the user's display name based on the user ID."""
    try:
        response = client.users_info(user=user_id)
        user_name = response["user"]["profile"]["display_name"] or response["user"]["profile"]["real_name"]
        return user_name
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")
        return None

def replace_user_ids_with_names(message_text):
    """Replaces user IDs (e.g., <@U031LLCTLF4>) in message text with the corresponding user names."""
    words = message_text.split()
    for i, word in enumerate(words):
        if word.startswith("<@") and word.endswith(">"):
            user_id = word[2:-1]  # Extract the user ID without "<@...>"
            user_name = get_user_name(user_id)
            if user_name:
                words[i] = f"@{user_name}"  # Replace the ID with the actual user name

    return " ".join(words)

def extract_username(text):
    # Look for the @ mention and capture the words after it as the name
    match = re.search(r"@([A-Za-z]+\s[A-Za-z]+)", text)
    
    if match:
        # Return only the name captured after @
        return match.group(1)
    return None

def send_message(channel_id, text):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        return response  # Optional: return response to check status
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        return None

def get_latest_message_ts(channel_id):
    try:
        # Fetch the latest message from the specified channel
        response = client.conversations_history(channel=channel_id, limit=1)
        messages = response.get("messages", [])
        
        if not messages:
            print("No messages found in the channel.")
            return None

        latest_message_ts = messages[0]["ts"]
        print(f"Latest message timestamp: {latest_message_ts}")
        return latest_message_ts

    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
        return None

def send_threaded_message(channel_id, text, thread_ts):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts  # Adding thread_ts to send it as a reply
        )
        return response  # Optional: return response to check status
    except SlackApiError as e:
        print(f"Error sending threaded message: {e.response['error']}")
        return None