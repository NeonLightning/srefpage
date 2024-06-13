import discord, os, requests, re, asyncio, argparse
from PIL import Image

class MidjountySrefScraper(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = THREAD_ID_HERE
        self.rate_limit_delay = 1
        self.save_path = kwargs.get('save_path', './images')

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id != self.target_channel_id:
            return
        if '--sref' in message.content and '""' in message.content and message.attachments:
            await asyncio.sleep(self.rate_limit_delay)
            sref_number = self.get_sref_number(message.content)
            if sref_number:
                filename = os.path.join(self.save_path, f"sref_{sref_number}.png")
                for attachment in message.attachments:
                    r = requests.get(attachment.url, allow_redirects=True)
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    image = Image.open(filename)
                    resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                    resized_filename = os.path.join(self.save_path, f"sref_{sref_number}_resized.png")
                    resized_image.save(resized_filename)
                    os.remove(filename)
                    os.rename(resized_filename, filename)
                    print(f"Image saved as {filename}")
            self.rate_limit_delay *= 2

    def get_sref_number(self, message_content):
        sref_index = message_content.find('--sref')
        if sref_index != -1:
            sref_number = re.search(r'\d+', message_content[sref_index + 6:])
            if sref_number:
                return sref_number.group()
        return None

    async def on_disconnect(self):
        print("Disconnected from Discord. Attempting to reconnect...")

    async def run_bot(self, token):
        while True:
            try:
                await self.start(token)
            except ConnectionResetError:
                print("Connection reset error occurred. Reconnecting...")
                await asyncio.sleep(5)
            except discord.errors.HTTPException as e:
                print(f"HTTP exception occurred: {e}. Reconnecting...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord bot to save images from messages.')
    parser.add_argument('--save_path', type=str, default='./images', help='Path to save images.')
    args = parser.parse_args()
    save_path = args.save_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    client = MidjountySrefScraper(save_path=save_path)
    token = 'USER_ID_HERE'
    asyncio.run(client.run_bot(token))