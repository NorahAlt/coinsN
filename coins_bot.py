from telethon import TelegramClient, events
from ultralytics import YOLO
import json
import logging
logger = logging.getLogger(__name__)
# Define coin values and their corresponding labels
coin_values = {'50-cent': 0.50, "Two-riyal": 2,  'One-riyal': 1.0,
              '25-cent': 0.25, "10-cent": 0.10, "5-cent": 0.05}

def detect(img, model):

    # Run inference on an image
    results = model.predict(img, save=True, imgsz=1280)
    for result in results:
        output = result.tojson()
        json_data = json.loads(output)

        logger.info('count of detected coins:', len(json_data))
        # now we want to sum the values of detected coins
        total = 0
        for obj in json_data:
            obj_name = obj['name']
            value = coin_values[obj_name]
            logger.info(f'{obj_name} is found. Now add {value}')
            total += value
        result.save(filename=img)
        #return the total amount of coins
        return total



def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')

    #load the model
    model = YOLO('best.pt')

    # Telegram api
    api_id = 24203327
    api_hash = '4edcd0bbd0951806c619345fb7a0b4c3'
    client = TelegramClient('session', api_id, api_hash)

    # wait for new messages
    @client.on(events.NewMessage())
    async def my_event_handler(event):
        sender = await event.get_sender()

        try:
            if sender.id in [1817795973, 1567582549]:
                logger.info("-------------------------New Message-----------------------------")
            else:
                return
        except Exception:
            logger.error("Unhandled error")
            return

        #check if a photo is sent
        if event.photo:
            download_img = await event.download_media() #will download the image from telegram chat and return the name of the image file
            total = detect(download_img, model)
            logger.info("New photo received")
        await client.send_file("https://t.me/+oRpdEkoS7eBmZGJk", download_img)
        await client.send_message("https://t.me/+oRpdEkoS7eBmZGJk", f" مجموع العملات:{round(total, 4)} ريال ")

    client.start()
    client.run_until_disconnected()
    logger.info('Finished')


if __name__ == "__main__":
    main()
