####
# apikey = "https://dash.nocaptchaai.com/home" 

# fetch_message = "The message that will be sent for check and transfer"

# check_id = "Discord channel id to check credits"

# transformation_id = "Discord channel id to transfer credits"

# owner = "Discord user id to transfer credits"

# token = "Discord token"

# Fill your own API KEY bellow before using.
# Make sure you already install models
# If you want to make it transfer faster , you can use multi servers channel to check in server and channel to transfer in another server
# If you have any issue please create a github issue or you can ask help on Discord https://discord.gg/kpDDupMFNY
####

import requests
import time
import re
from PIL import Image
from io import BytesIO
import base64
from colorama import init, Fore

apikey = "" 
multiservers = False # True or False
fetch_message = "#credit"
check_id = ""
transformation_id = ""
owner = ""
probot_id = "282859044593598464"
token = ""

def image_to_base64(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    return base64.b64encode(img_buffer.getvalue()).decode('utf-8')

def send_request(image_url):
    try:
        payload = {
            "method": "ocr",
            "image": image_to_base64(image_url)
        }

        headers = {
            "Content-Type": "application/json",
            "apikey": apikey
        }

        response = requests.post("https://pro.nocaptchaai.com/solve", json=payload, headers=headers)
        data = response.json()
        return data.get("solution")
    except Exception as error:
        print(f"Fetch error: {error}")
        return None

headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

data = {
    "content": fetch_message
}

response = requests.post(f"https://discord.com/api/v9/channels/{check_id}/messages", headers=headers, json=data)

if response.status_code == 200:
    print(f"{Fore.LIGHTBLUE_EX }###################################################{Fore.RESET}")
    print(f"{Fore.LIGHTBLUE_EX }#{Fore.RESET} ({Fore.LIGHTBLUE_EX }~{Fore.RESET}) Token : {Fore.LIGHTBLUE_EX }{token.split('.')[0]}{Fore.RESET}")

    message_id = response.json()["id"]

    message_sent = False
    attachment_url = None

    while True:
        response = requests.get(f"https://discord.com/api/v9/channels/{check_id}/messages", headers=headers)

        if response.status_code == 200:
            messages = response.json()
            for message in messages:
                if (
                    "author" in message
                    and message["author"]["id"] == probot_id
                    and message.get("referenced_message") and message["referenced_message"].get("id") == str(message_id)
                ):
                    bot_response = message["content"]

                    if not message_sent:
                        numbers = re.findall(r"\$(\d+)", bot_response)
                        if numbers:
                            if numbers[0] == "0":
                                print(f"{Fore.LIGHTRED_EX }#{Fore.RESET} ({Fore.LIGHTRED_EX }!{Fore.RESET}) Token : {Fore.LIGHTRED_EX }[0]{Fore.RESET} credit")
                                message_sent = True
                                break

                            transform_message = f"{fetch_message} {owner} {' '.join(numbers)}"
                            data = {
                                "content": transform_message
                            }
                            print(f"{Fore.LIGHTBLUE_EX }#{Fore.RESET} ({Fore.LIGHTBLUE_EX }~{Fore.RESET}) Token : {Fore.LIGHTBLUE_EX }[{' '.join(numbers)}]{Fore.RESET} credits")
                            time.sleep(1) if multiservers else time.sleep(20) 
                            requests.post(f"https://discord.com/api/v9/channels/{transformation_id}/messages", headers=headers, json=data)
                            message_sent = True
                            while True:
                                response = requests.get(f"https://discord.com/api/v9/channels/{transformation_id}/messages", headers=headers)
                                if response.status_code == 200:
                                    messages = response.json()
                                    for message in messages:
                                        if "attachments" in message and len(message["attachments"]) > 0:
                                            attachment_url = message["attachments"][0]["url"]
                                            print(f"{Fore.LIGHTBLUE_EX }#{Fore.RESET} ({Fore.LIGHTBLUE_EX }~{Fore.RESET})  OCR  : {Fore.LIGHTBLUE_EX }{attachment_url}{Fore.RESET}")
                                            break
                                    if attachment_url:
                                        break

                            captcha_solution = send_request(attachment_url)
                            if captcha_solution:
                                probot_ocr_solution_message = f"{captcha_solution}"
                                data = {
                                    "content": probot_ocr_solution_message
                                }
                                requests.post(f"https://discord.com/api/v9/channels/{transformation_id}/messages", headers=headers, json=data)

                        print(f"{Fore.LIGHTBLUE_EX }#{Fore.RESET} ({Fore.LIGHTBLUE_EX }~{Fore.RESET}) Solve : {Fore.LIGHTBLUE_EX }{captcha_solution}{Fore.RESET}")

                    break

        time.sleep(1)

        if message_sent:
            break

else:
    print(f"{Fore.LIGHTRED_EX }###################################################{Fore.RESET}")
    print(f"[{Fore.LIGHTRED_EX }!{Fore.RESET}] Failed to send message")
    print(f"[{Fore.LIGHTRED_EX }!{Fore.RESET}] Token: {Fore.LIGHTRED_EX }{token}{Fore.RESET}")
    print(f"{Fore.LIGHTRED_EX }###################################################{Fore.RESET}")
print(f"{Fore.LIGHTBLUE_EX }###################################################{Fore.RESET}")
print(f"\n[{Fore.LIGHTGREEN_EX }~{Fore.RESET}] {Fore.LIGHTGREEN_EX }Processe successful{Fore.RESET}")
print(f"[{Fore.LIGHTRED_EX }!{Fore.RESET}] {Fore.LIGHTRED_EX }Terminal kiled{Fore.RESET}")
