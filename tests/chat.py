import sys
import datetime

import pytmi


def main(channel: str) -> None:
    tmi = pytmi.TmiClient()

    if not tmi.login_anonymous():
        return

    tmi.join(channel)

    while True:
        try:
            msg = tmi.get_message()

            if msg == None or not msg.parsed:
                continue

            if "JOIN" in msg.command or "PART" in msg.command:
                continue

            r, g, b = 0xff, 0xff, 0xff

            if msg.tags.get("color", None) != None:
                color = int(msg.tags["color"][1:], 16)

                r = color >> 16
                g = (color & 0x00ff00) >> 8
                b = color & 0x0000ff

            if msg.tags.get("tmi-sent-ts", None) != None:
                sent_ts = datetime.datetime.fromtimestamp(msg.tags["tmi-sent-ts"] / 1000)
                sent_str = sent_ts.strftime("%H:%M")
                print("%s" % sent_str, end = " ")

            privmsg = msg.command.split(" :", 1)[1]

            print("\x1b[38;2;%u;%u;%um" % (r, g, b), end = "")
            print("@%s\x1b[0m: %s\n" % (msg.tags.get("display-name", "justinfan"), privmsg))

            del msg
        except Exception as e:
            if not isinstance(e, IndexError):
                raise

            if not isinstance(e, OSError):
                continue


if __name__ == "__main__":
    try:
        channel = input("Insert the channel to join: ")
        main(channel.lstrip())
    except KeyboardInterrupt:
        sys.exit()
