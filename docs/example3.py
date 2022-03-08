import asyncio
import pytmi
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


async def main(channel: str) -> None:
    client = pytmi.Client()

    await client.login_anonymous()
    await client.join(channel)

    print("Dumping chat of {}".format(channel))
    while True:
        raw = await client.get_message_raw()
        print(raw, "\n")
        del raw


if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ").strip()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(channel))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Quitting...")
