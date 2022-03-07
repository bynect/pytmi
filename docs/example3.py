import asyncio
import sys
import datetime

import pytmi


async def main(channel: str) -> None:
    client = pytmi.TmiClient(use_task=False)

    await client.login_anonymous()
    await client.join(channel)

    print("Dumping chat of {}".format(channel))
    while True:
        raw = await client.get_raw_message()
        print(raw, "\n")
        del raw

if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ").lstrip()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(channel))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Quitting...")
