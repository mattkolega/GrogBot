# GrogBot
 
A simple bot for my discord server. Contains a collection of fun commands and utilities.

## Installation and Setup

- Ensure Python 3.8 or above is installed
- Clone the repository
- Create a bot in the discord developer portal and add to a discord server
- Run the following command to install python dependencies:

```bash
# Windows
py -3 -m pip install -r requirements.txt

# Linux/macOS
python3 -m pip install -r requirements.txt
```

- Download and install FFmpeg to enable voice functionality
    - Add to PATH if using Windows
- If using a linux environment, the following dependencies are also required:
    - libffi
    - libnacl
    - python3-dev
- Obtain bot token from developer portal
- Create .env file in the directory of the cloned repository and place bot token inside under the name `BOT_TOKEN`

## Usage

- Run the following command in the directory of the cloned repository to bring the bot online:

```bash
# Windows
py -3 main.py

# Linux/macOS
python3 main.py
```

- Commands use the `$` prefix
- Type `$help` into a discord server channel to see available commands

## Additional Help

- [discord.py Documentation](https://discordpy.readthedocs.io/en/stable/index.html)
