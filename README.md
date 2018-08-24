# Flask Security Bundle

**IMPORTANT**: This project has been merged into the [Flask Unchained](https://github.com/briancappello/flask-unchained) project. Therefore, **this package is deprecated**, but is left archived here for historical purposes.

## What is it?

This project started as a Python package extending and customizing a few things from the [Flask Security](https://pythonhosted.org/Flask-Security/) project so that it would work with Flask Unchained. However, as I continued to work with their code base, it become more and more apparent that it suffered from a lot of technical debt, and in my opinion, it was just generally very difficult to read and follow.

So, over time as I continued to improve Flask Security's integration with Flask Unchained, I more or less rewrote the whole thing. The core encryption/hashing code remains unchanged, and juts like upstream, it supports session and token authentication (support for HTTP basic auth got dropped). Much of the API actually remains the same (or very similar), so if you're familiar with the Flask Security code base, there should be quite a few things you'll recognize.

As of the latest commits, this project is now a fully independent fork of Flask Security, and no longer depends on it (but it does require Flask Unchained; it will not work with stock Flask).

Requirements:

* Python 3.6+
* Flask Unchained at commit hash `71b88923e1447ea6696cda5ed450b3edba2ac8f9`
* Flask Login
* Flask Principal
* Flask BabelEx
* Flask WTF
* itsdangerous
* passlib

## License

MIT
