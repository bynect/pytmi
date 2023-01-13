import asyncio
import pytmi

async def main() -> None:
    nick = input("Insert your Twitch nickname: ").strip()
    token = input("Insert your Twitch OAuth token: ").strip()
    channel = input("Insert the channel to join: ").strip()

    async with pytmi.Client() as client:
        await client.login_oauth(token, nick, channel)
        await client.join(channel)
        await client.send_message("Hello, Twitch!")
        await client.part(channel)

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except:
        print("Something went wrong.")
