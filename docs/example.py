import asyncio
import sys
import datetime

import pytmi


async def main(channel: str) -> None:
    client = pytmi.TmiClient(ssl=False)

    await client.login_anonymous()
    await client.join(channel)

    while True:
        try:
            raw = await client.get_privmsg()
            msg = pytmi.TmiMessage(raw.lstrip())

            if msg == None or not msg.parsed or not "PRIVMSG" in msg.command:
                continue

            r, g, b = 0xFF, 0xFF, 0xFF

            if msg.tags.get("color", None) != None:
                color = int(msg.tags["color"][1:], 16)
                r = color >> 16
                g = (color & 0x00FF00) >> 8
                b = color & 0x0000FF

            if msg.tags.get("tmi-sent-ts", None) != None:
                sent_ts = datetime.datetime.fromtimestamp(
                    msg.tags["tmi-sent-ts"] / 1000
                )
                sent_str = sent_ts.strftime("%H:%M")
                print("%s" % sent_str, end=" ")

            privmsg = msg.command.split(" :", 1)[1]

            print("\x1b[38;2;%u;%u;%um" % (r, g, b), end="")
            print(
                "@%s\x1b[0m: %s\n"
                % (msg.tags.get("display-name", "justinfan"), privmsg)
            )

            del raw
            del msg
        except OSError:
            raise
        except Exception:
            continue


if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ").lstrip()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(channel))
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        raise
