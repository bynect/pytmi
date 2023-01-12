# pytmi

[![package_version](https://img.shields.io/pypi/v/pytmi)](https://pypi.org/project/pytmi/)
[![license](https://img.shields.io/pypi/l/pytmi)](https://choosealicense.com/licenses/mit/#)
[![python_version](https://img.shields.io/pypi/pyversions/pytmi)](https://www.python.org/)
[![wheel](https://img.shields.io/pypi/wheel/pytmi)](https://pypi.org/project/pytmi/)

TMI (Twitch Messaging Interface) library for Python.

You can get your OAuth token with the site `https://twitchapps.com/tmi/`.

## Example

Here's a little application that logs in the user using OAuth, joins the Twitch channel requested by the user, sends the message `Hello, Twitch!` to the chat and then leaves the channel.

```python
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
        await client.logout()

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except:
        print("Something went wrong.")
```

You can find others usage example inside the [`test`](/test) directory.

## Known bugs

* Spurious errors when using SSL.

* Possible problems with pending tasks (if you don't cleanup them properly).

## Todos

* Handle connection and login error in a better way.

* Handle messages that are not correctly encoded in UTF8.

## Changelog

### v1.0.0

* Major version bump.

* Add a background task that collects messages in a buffer and sends pong as needed.

* Rewrite Client code.

* Change methods name (`part` -> `leave`, `privmsg` -> `send_message`).

* Add async context manager (`async with`) support for Client.

### v0.3.0

* Major library simplification and rewriting.

* Removed buggy background task.

* Add library logging.

### v0.2.3

* Add background task to collect messages (removed in `v0.3.0`).

* Refactor code.

### v0.2.2

* Add message buffer abstraction.

* Major code refactoring.

### v0.2.1

* Minor code refactoring.

### v0.2.0

* Rewrite library to be asynchronous.

* Add SSL support (enabled by default).

* Reorganize project structure.

### v0.1.1

* Minor code refactoring.

* Improve message handling and parsing.

### v0.1.0

* Initial version.
