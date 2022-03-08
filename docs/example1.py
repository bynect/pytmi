import asyncio
import pytmi


async def main() -> None:
    nick = input("Insert your Twitch nickname: ").lstrip()
    token = input("Insert your Twitch OAuth token: ").lstrip()
    channel = input("Insert the channel to join: ").lstrip()

    client = pytmi.Client()
    await client.login_oauth(token, nick)

    await client.join(channel)
    await client.send_privmsg("Hello, Twitch!")

    await client.part(channel)
    await client.logout()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except:
        print("Something went wrong.")
