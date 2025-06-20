# Rald
---
Rald is a multifunctional Discord bot build with Py-cord. Rald has multi server support, welcome messages, moderation, fun commands, a sepical embed editing system (made by z3lev), music commands (that supports playing music by name and also by link), an url shortener and much more thet is waiting for you to check out

## How to setup
1. Get your Discord bot token at [Discord Developer Portal](https://discord.com/developers/applications)
    - Log in with your Discord account
    - Create a new application by clicking the ``New Application`` button in the top right corner
    - Once your bot was made go to that bot and go to the ``Bot`` page
    - Here scroll down and enable: ```Presence Intent, Server Members Intent, Message Content Intent```
    - Than scroll up and reset your bot's token by using the ``Reset Token`` button and save the new token for later
2. Buy a VPS/ Python server for the bot, a VPS/Lavalink server and a VPS/Python server for the url shortener API
3. Upload the bot files to the VPS/Paython server and also the API files to the VPS/Python server
4. Configure the bot by creating a .env file with these datas and configure the bugreport webhooks in ``/data/webhooks.json``:
    ```
    TOKEN= your bot token

    # LAVALINK
    LAVALINK_URI = your Lavalink server url
    LAVALINK_PASSWORD = your lavalink server password
    ```
    
    4, A: If you are on a VPS install the requirements with these commands:
    ```apt install python3
    apt install python3-pip
    pip install wavelink
    pip install py-cord
    pip install -m requirements.txt```
5. Start the bot and enjoy

---

Fell free to open issues, contribute or fork the project