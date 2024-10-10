import asyncio

import requests
from telegram import Bot

async def fetch_avito_data(access_token, user_id, telegram_token, telegram_chat_id, chat_limit, message_limit):
    """
    Fetch data from Avito API, including chat IDs, chat info, and recent messages.
    Then sends the messages to a Telegram channel.

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

            text_messages = []
            for message in messages_data.get('messages', []):
                if message.get('type') == 'text':
                    text_content = message['content'].get('text')
                    direction = message.get('direction')
                    if text_content:
                        text_messages.append({
                            'text': text_content,
                            'direction': direction
                        })
                        print(f"{text_content} [{direction}]")
                        print()

            # Отправляем сообщения в Telegram
            await send_to_telegram(chat_id, text_messages, telegram_token, telegram_chat_id)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching messages for chat ID {chat_id}: {e}")
            continue


async def send_to_telegram(chat_id, messages, telegram_token, telegram_chat_id):
    """
    Sends the chat ID and last messages to a Telegram channel.

    :param chat_id: ID of the chat from Avito
    :param messages: List of messages with direction (in/out)
    :param telegram_token: Token for Telegram Bot API
    :param telegram_chat_id: ID of the Telegram channel or group to send messages to
    """
    bot = Bot(token=telegram_token)

    # Форматируем текст для отправки
    message_text = f"Last {len(messages)} messages for chat ID {chat_id}:\n\n"
    for message in messages:
        message_text += f"{message['text']} [{message['direction']}]\n"

    try:
        await bot.send_message(chat_id=telegram_chat_id, text=message_text)
        print(f"Messages for chat ID {chat_id} sent to Telegram successfully.")
    except Exception as e:
        print(f"Failed to send messages for chat ID {chat_id} to Telegram: {e}")



if __name__ == "__main__":
    access_token = "_u7D53CsRc-YXRaVhYGORwYavjUh7qnlpuGh0oIR"
    user_id = 373140542
    telegram_token = "8144752538:AAGwALUxXfN77RFEoSH9KMkZZDB_ClbE_NI"
    telegram_chat_id = '-1002465274869'
    chat_limit = 5
    message_limit = 15

    asyncio.run(fetch_avito_data(access_token, user_id, telegram_token, telegram_chat_id, chat_limit, message_limit))

