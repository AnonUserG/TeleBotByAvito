import requests


def fetch_avito_data(access_token, user_id, chat_limit=5, message_limit=15):
    """
    Fetch data from Avito API, including chat IDs, chat info, and recent messages.

    Parameters:
    - access_token (str): Authorization token for Avito API.
    - user_id (int): User ID for which chats and messages are fetched.
    - chat_limit (int): Number of chats to retrieve (default is 5).
    - message_limit (int): Number of messages to retrieve per chat (default is 15).

    """
    url_get_chats = f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "limit": chat_limit
    }

    try:
        response = requests.get(url_get_chats, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching chats: {e}")
        return

    data = response.json()
    chats = data.get('chats', [])

    if not chats:
        print("No chats found.")
        return

    print("Chat IDs:")
    chat_ids = [chat.get('id') for chat in chats if chat.get('id')]

    for chat_id in chat_ids:
        print(chat_id)
    print()

    for chat_id in chat_ids:
        chat_info_url = f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats/{chat_id}"
        try:
            chat_response = requests.get(chat_info_url, headers=headers)
            chat_response.raise_for_status()
            chat_data = chat_response.json()
            print(f"Chat information for chat ID {chat_id}:")
            print(chat_data)
            print()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chat details for chat ID {chat_id}: {e}")
            continue

        messages_url = f"https://api.avito.ru/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/"
        messages_params = {
            "limit": message_limit
        }

        try:
            messages_response = requests.get(messages_url, headers=headers, params=messages_params)
            messages_response.raise_for_status()
            messages_data = messages_response.json()
            print(f"Last {message_limit} messages for chat ID {chat_id}:")

            for message in messages_data.get('messages', []):
                if message.get('type') == 'text':
                    text_content = message['content'].get('text')
                    direction = message.get('direction')
                    if text_content:
                        print(f"{text_content} [{direction}]")
                        print()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching messages for chat ID {chat_id}: {e}")
            continue


if __name__ == "__main__":
    access_token = "_u7D53CsRc-YXRaVhYGORwYavjUh7qnlpuGh0oIR"
    user_id = 373140542
    fetch_avito_data(access_token, user_id)
