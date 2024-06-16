import discord, os, re, asyncio, argparse, random, aiohttp, logging
from PIL import Image

class MidjountySrefScraper(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_channel_id = CHANNEL_ID_HERE
        self.save_path = kwargs.get('save_path', './images')
        self.downloaded_images = set()
        self.scan_downloaded_images()
    try:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.basicConfig(filename='/home/neonbot/midjourney/scraper.log', level=logging.INFO)
        logger = logging.getLogger()
        handler = logger.handlers[0]
        handler.setFormatter(formatter)
        print(f"Log file path: {os.path.abspath('scraper.log')}")
        logging.debug(f"Log file path: {os.path.abspath('scraper.log')}")
    except Exception as e:
        print(f"Error setting up logging: {e}")
        logging.error(f"Error setting up logging: {e}")

    def scan_downloaded_images(self):
        files = 0
        for filename in os.listdir(self.save_path):
            files += 1
            if filename.startswith("sref_") and filename.endswith(".png"):
                sref_number = filename.split("_")[1].split(".")[0]
                self.downloaded_images.add(sref_number)
        logging.info(f"downloaded {files}")
        print(f"downloaded {files}")

    async def on_ready(self):
        logging.info(f'We have logged in as {self.user}')
        print(f'We have logged in as {self.user}')
        channel = self.get_channel(self.target_channel_id)
        async for message in channel.history(limit=None):
            await self.process_message(message)

    async def on_message(self, message):
        await self.process_message(message)

    async def process_message(self, message):
        self.rate_limit_delay = random.randint(1, 3)
        await asyncio.sleep(self.rate_limit_delay)
        if message.author == self.user:
            return
        if '"" --v 6.0 --ar 16:9 --sw 1000 --sref' in message.content and message.attachments:
            sref_number = self.get_sref_number(message.content)
            if sref_number and not self.is_image_downloaded(sref_number):
                filename = os.path.join(self.save_path, f"sref_{sref_number}.png")
                logging.info(f'saving download of {filename}')
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
                                logging.info(f"Image saved as {filename}")
                                print(f"Image saved as {filename}")
                                self.downloaded_images.add(sref_number)
            elif self.is_image_downloaded(sref_number):
                filename = os.path.join(self.save_path, f"sref_{sref_number}.png")
                logging.debug(f'skipping download of {filename}')
                print(f'skipping download of {filename}')
        elif message.attachments is not None and '"" --v 6.0 --ar 16:9 --sw 1000 --sref' not in message.content:
            logging.debug('Attachment')

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
        logging.debug("Disconnected from Discord. Attempting to reconnect...")
        print("Disconnected from Discord. Attempting to reconnect...")

    async def run_bot(self, token):
        while True:
            try:
                await self.start(token)
            except (ConnectionResetError, discord.errors.HTTPException, aiohttp.ClientError) as e:
                logging.error(f"An exception occurred: {e}. Reconnecting...")
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
    token = 'USER_ID_HERE'
    asyncio.run(client.run_bot(token))