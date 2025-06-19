from discord import SyncWebhook
import json

class bugReport():
    def __init__(self, error_type, command, error):
        super().__init__()
        self.type = error_type
        self.command = command
        self.error = error
        
    def sendReport(type, command, error):
        with open("data/webhooks.json", "r") as whs:
            whData = json.load(whs)
        whURL = whData[type]
        webhook = SyncWebhook.from_url(whURL)
        webhook.send(content=f"**Type:** {type} \n**Command:** {command} \n \n**Error:** ```{error}```")