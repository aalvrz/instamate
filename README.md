# Instamate ![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg) [![build](https://github.com/aalvrz/instamate/actions/workflows/build.yml/badge.svg)](https://github.com/aalvrz/instamate/actions/workflows/build.yml)

Instamate is a bot for automating Instagram operations written in Python. Inspired heavily on **[InstaPy](https://github.com/InstaPy/InstaPy)**, Instamate provides a simpler interface and the best and latest Python practices for its development.

## Installing a web driver

You will need to install a web driver such as [Geckodriver](https://github.com/mozilla/geckodriver/releases). Simply download a release binary and place it in your file system at `/usr/local/bin`.

## Configuration

Create a `.env` file in the repository root with your instagram authentication credentials:

```
INSTAGRAM_USERNAME="myuser"
INSTAGRAM_PASSWORD="foobar"
```

## Basic Usage

See [`examples/`](https://github.com/aalvrz/instamate/tree/master/examples) directory for different operations that can be achieved with Instamate.

## Troubleshooting

- https://stackoverflow.com/questions/72405117/selenium-geckodriver-profile-missing-your-firefox-profile-cannot-be-loaded
