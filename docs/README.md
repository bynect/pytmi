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
    nick = input("Insert your Twitch nickname: ").lstrip()
    token = input("Insert your Twitch OAuth token: ").lstrip()
    channel = input("Insert the channel to join: ").lstrip()

    client = pytmi.Client()
    await client.login_oauth(token, nick)

    await client.join(channel)
    await client.privmsg("Hello, Twitch!")

    await client.part(channel)
    await client.logout()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except:
        print("Something went wrong.")
```

You can another find a [usage example](example2.py) inside the `docs` directory.

## Bugs

* Warnings with background tasks.

* Error when using SSL.

## Todos

* Add a way to receive messages and pong every 5 minutes.

* Handle connection and login error in a better way.

* Handle messages that are not correctly encoded in UTF8.

* Initial connection to Twitch server is a little bit slow.

## Changelog

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
