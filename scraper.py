import discord
import os
import re
import asyncio
import argparse
from PIL import Image
import random
import aiohttp

class MidjountySrefScraper(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = THREAD_ID_HERE
        self.save_path = kwargs.get('save_path', './images')
        self.downloaded_images = set()
        self.scan_downloaded_images()

    def scan_downloaded_images(self):
        for filename in os.listdir(self.save_path):
            if filename.startswith("sref_") and filename.endswith(".png"):
                sref_number = filename.split("_")[1].split(".")[0]
                self.downloaded_images.add(sref_number)

    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        channel = self.get_channel(self.target_channel_id)
        async for message in channel.history(limit=10):
            await self.process_message(message)

    async def process_message(self, message):
        self.rate_limit_delay = random.randint(1, 3)
        await asyncio.sleep(self.rate_limit_delay)
        if message.author == self.user:
            return
        if '--sref' in message.content and '""' in message.content and message.attachments:
            sref_number = self.get_sref_number(message.content)
            if sref_number and not self.is_image_downloaded(sref_number):
                filename = os.path.join(self.save_path, f"sref_{sref_number}.png")
                print(f'saving download of {filename}')
                async with aiohttp.ClientSession() as session:
                    for attachment in message.attachments:
                        async with session.get(attachment.url) as resp:
                            if resp.status == 200:
                                with open(filename, 'wb') as f:
                                    while True:
                                        chunk = await resp.content.read(1024)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                image = Image.open(filename)
                                resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                                resized_image.save(filename)
                                print(f"Image saved as {filename}")
                                self.downloaded_images.add(sref_number)
            elif self.is_image_downloaded(sref_number):
                filename = os.path.join(self.save_path, f"sref_{sref_number}.png")
                print(f'skipping download of {filename}')

    def get_sref_number(self, message_content):
        sref_index = message_content.find('--sref')
        if sref_index != -1:
            sref_number = re.search(r'\d+', message_content[sref_index + 6:])
            if sref_number:
                return sref_number.group()
        return None

    def is_image_downloaded(self, sref_number):
        return sref_number in self.downloaded_images

    async def on_disconnect(self):
        print("Disconnected from Discord. Attempting to reconnect...")

    async def run_bot(self, token):
        while True:
            try:
                await self.start(token)
            except (ConnectionResetError, discord.errors.HTTPException, aiohttp.ClientError) as e:
                print(f"An exception occurred: {e}. Reconnecting...")
                await self.close()
                await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord bot to save images from messages.')
    parser.add_argument('--save_path', type=str, default='./images', help='Path to save images.')
    args = parser.parse_args()
    save_path = args.save_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    client = MidjountySrefScraper(save_path=save_path)
    token = 'CLIENT_ID_HERE'
    asyncio.run(client.run_bot(token))