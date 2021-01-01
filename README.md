# pytmi

[![package_version](https://img.shields.io/pypi/v/pytmi)](https://pypi.org/project/pytmi/)
[![license](https://img.shields.io/pypi/l/pytmi)](https://choosealicense.com/licenses/mit/#)
[![python_version](https://img.shields.io/pypi/pyversions/pytmi)](https://www.python.org/)
[![wheel](https://img.shields.io/pypi/wheel/pytmi)](https://pypi.org/project/pytmi/)

TMI (Twitch Messaging Interface) library for Python.

## Example

Here's a little application that logs in the user using OAuth, joins the Twitch channel requested by the user, sends the message `Hello, Twitch` to the chat and then leaves the channel.

```python
import pytmi


def send_message() -> None:
    username = input("Insert your Twitch username: ").lstrip()
    token = input("Insert your Twitch OAuth token: ").lstrip()
    channel = input("Insert the channel to join: ").lstrip()

    client = pytmi.TmiClient()
    client.login_oauth(token, username)

    client.join(channel)
    client.privmsg("Hello, Twitch")

    client.logout()


if __name__ == "__main__":
    try:
        send_message()
    except:
        print("Something went wrong.")
```

You can find an [extended example](tests/chat.py) in the `tests` directory.
