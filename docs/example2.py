import asyncio
import sys
import datetime

import pytmi


async def main(channel: str) -> None:
    client = pytmi.TmiClient(use_ssl=False)

    await client.login_anonymous()
    await client.join(channel)

    print("Listening chat of {}".format(channel))
    while True:
        await asyncio.sleep(1)
        try:
            # raw = await client.get_privmsg()
            # msg = pytmi.TmiMessage(raw.lstrip())
            msg = await client.get_message()

            if msg is None or not msg.valid or not "PRIVMSG" in msg.command:
                continue

            r, g, b = 0xFF, 0xFF, 0xFF
            if msg.tags.get("color", None) is not None:
                color = int(msg.tags["color"][1:], 16)
                r = color >> 16
                g = (color & 0x00FF00) >> 8
                b = color & 0x0000FF

            if msg.tags.get("tmi-sent-ts", None) is not None:
                sent_ts = datetime.datetime.fromtimestamp(
                    msg.tags["tmi-sent-ts"] / 1000
                )
                sent_str = sent_ts.strftime("%H:%M")
                print("%s" % sent_str, end=" ")

            privmsg = msg.command.split(" :", 1)[1]
            name = msg.tags.get("display-name", "justinfan")

            print(f"\x1b[38;2;{r};{g};{b}m", end="")
            print(f"@{name}\x1b[0m: {privmsg}")

            del raw
            del msg

        # FIXME: Change these except shenanigans
        except OSError:
            raise
        except KeyboardInterrupt:
            await client.logout()
            print("Quitting...")
            return


if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ").lstrip()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(channel))
    except Exception:
        raise
