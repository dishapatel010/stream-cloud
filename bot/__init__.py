from telethon import events,functions,errors
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from config import Config
import asyncio
import threading
import requests
import re

def cronjob():
    threading.Timer(60*5, cronjob).start()
    requests.get(Config.DOMAIN)
    
if "heroku" in Config.DOMAIN:
    cronjob()

client = TelegramClient(
            StringSession(),
            Config.API_ID,
            Config.API_HASH,
            # proxy=("socks5","127.0.0.1",9050)
            ).start(bot_token=Config.TOKEN)

username_bot = client.get_me().username

def get_file_name(message):
    if message.file.name:
        return message.file.name.replace(" ","-")
    ext = message.file.ext or ""
    return f"file{ext}"

@client.on(events.NewMessage)
async def download(event):
 
    if (pv := event.is_private) or event.is_group :
        if pv:
            try:
                await event.client(functions.channels.GetParticipantRequest(
                    channel = Config.CHANNEL_USERNAME,
                    participant = event.sender_id
                    ))
            except errors.UserNotParticipantError:
                await event.reply(f"First join to our official channel to access the bot or get the newest news about the bot\n\n@{Config.CHANNEL_USERNAME}\n\nAfter that /start the bot again.")
                return
        
        if event.file :
            if not pv :
                if not event.file.size > 10_000_000:
                    return 
            sender = await event.get_sender()
            msg = await event.client.send_file(
                Config.CHANNEL,
                file=event.message.media
                caption=f"x")
            id_hex = hex(msg.id)[2:]
            id = f"{id_hex}/{get_file_name(msg)}"
            bot_url = f"Telegram.dog/{username_bot}?start={id_hex}"
            await event.reply(f"Your Link Generated! 💕\n\n📥 **Download Link:** {Config.DOMAIN}/{id}\n\n**📂 Share** : {bot_url}")
            return

        elif id_msg := re.search("/start (.*)", event.raw_text ):
            if id_hex := id_msg.group(1) :
                try:
                    id = int(id_hex,16)
                except ValueError:
                    return
                msg = await event.client.get_messages(Config.CHANNEL,ids=id)
                if not msg or not msg.file :
                    return await event.reply("File Not Found")
                if regex := re.search(r"(\d*)/(\d*)",msg.message):
                    if user_id := int(regex.group(1)) :
                        msg_id = int(regex.group(2))
                        file = await event.client.get_messages(user_id,ids=msg_id)
                        if not file or not file.file :
                            return await event.reply("File Not Found")
                        forward = await file.forward_to(event.chat_id)
                        id_name = f"{id_hex}/{get_file_name(msg)}"
                        bot_url = f"Telegram.dog/{username_bot}?start={id_hex}"
                        forward_reply = await forward.reply(f"```Save The File.\n\nDeleting in 30 seconds.```\n\n📥 **Download :** {Config.DOMAIN}/{id_name}\n\n**📂 Share** : {bot_url}",link_preview=False)
                        await asyncio.sleep(20)
                        await forward_reply.edit(f"```Save The File.\n\nDeleting in 10 seconds.\n\n```📥 **Download :** {Config.DOMAIN}/{id_name}\n\n**📂 Share** : {bot_url}")
                        await asyncio.sleep(10)
                        await forward.delete()
                        await forward_reply.edit(f"**Your Generated Link! 💕**\n\n📥 **Download :** {Config.DOMAIN}/{id_name}\n\n**📂 Share** : {bot_url}",link_preview=True)
                return
        
        if pv:
            await event.reply("🌻 Hey!!\n\nAn Instant Telegram File to Link Generator Bot.\n\nSend me any File & see the magic ✨")
        

    elif event.is_channel:
        if event.chat_id == Config.CHANNEL:
            if event.reply_to:
                msg = await event.get_reply_message()
                if regex := re.search(r"(\d*)/(\d*)",msg.message):
                    if user_id := int(regex.group(1)) :
                        msg_id = int(regex.group(2))
                        if await event.client.send_message(entity=user_id, message=event.message, reply_to=msg_id):
                            await event.client.edit_message(event.chat_id,event.id,f"{event.message.message}\n sended")
                        
                        
                    
client.run_until_disconnected()
