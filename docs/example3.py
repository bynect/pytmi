import asyncio
import sys
import datetime

import pytmi


async def main(channel: str) -> None:
    client = pytmi.TmiClient()

    await client.login_anonymous()
    await client.join(channel)

    print("Dumping chat of {}".format(channel))
    try:
        while True:
            raw = await client.get_raw_message()
            print(raw, "\n")
            del raw
    except OSError:
        raise
    finally:
        await client.logout()


if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ").lstrip()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(channel))
    except KeyboardInterrupt:
        print("Quitting...")
    except Exception:
        raise
