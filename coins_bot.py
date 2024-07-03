from telethon import TelegramClient, events
from ultralytics import YOLO
import json
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define coin values and their corresponding labels
coin_values = {'50-cent': 0.50, "Two-riyal": 2,  'One-riyal': 1.0,
              '25-cent': 0.25, "10-cent": 0.10, "5-cent": 0.05}



def detect(img, model):
    logger.info(f"running inference")
    # Run inference on an image
    result = model.predict(img, save=True, imgsz=1280)[0]

    logger.info(f"result saving")
    #save the image result file
    result.save(filename=img)

    #converte the result into json format
    output = result.tojson()

    #load the result using json library
    json_data = json.loads(output)

    logger.info(f"count of detected coins: {len(json_data)}")

    # now we want to sum the values of detected coins
    total = 0


    logger.info("calculating the total amount")
    # iterate over each coin in the image
    for obj in json_data:
        obj_name = obj['name'] # type of the coin
        value = coin_values[obj_name] #get the value of the coin from the dictionary
        total += value # add the value of the coin to the total


    logger.info("detection finishd")
    #return the total amount of coins
    return total



def main():

    try:

        logger.info('Started')

        #load the model
        model = YOLO('best.pt')


        # Load configuration from JSON configuration file
        with open('conf.json', 'r') as f:
            data = json.load(f)

        # Telegram api
        api_id = data['api_id']
        api_hash = data['api_key']

        # create the client object of telegram
        client = TelegramClient('session', api_id, api_hash)

        # wait for new messages
        @client.on(events.NewMessage())
        async def my_event_handler(event):
            sender = await event.get_sender() # sender infromation
            chat_id = event.message.peer_id #get the chat id to reply to it with the result later

            #check if a photo is sent
            if event.photo:

                # will download the image from telegram chat and return the name of the image file
                download_img = await event.download_media()

                # send the image to the detect function, it will return the total amount of the coins
                logger.info(f"processing image:{download_img} from the chat id: {chat_id}")
                total = detect(download_img, model)
                logger.info(f"processing image:{download_img} from chat id: {chat_id} finished ")


                logger.info(f"sending back the detection of image:{download_img} from chat id: {chat_id}")
                # send back the image to the chat again with the detection
                await client.send_file(chat_id, download_img)
                logger.info(f"sending back the result of image:{download_img} from chat id: {chat_id}")
                # send the total amount of the coins
                await client.send_message(chat_id, f" مجموع العملات:{round(total, 4)} ريال ")
            else:
                logger.info(f"message received: {event.text} from chat id: {chat_id}")
                await client.send_message(chat_id, f"ياهلا وسهلا، انا بوت اقدر اساعدك تحسب عملاتك المعدنية، ارسل اي صورة فيها عملات معدنية وحرسل لك مجموعها في ثواني ")

        client.start()
        client.run_until_disconnected()
        logger.info('Finished')

    except Exception as ex:
        logger.error(ex)


if __name__ == "__main__":
    main()
