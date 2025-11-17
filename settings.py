import os

import yaml
from dotenv import load_dotenv

load_dotenv()


LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_GUILD = int(os.getenv("ALLOWED_GUILD", ""))
CREATE_TICKET_CHANNEL = int(os.getenv("CREATE_TICKET_CHANNEL"))

if os.path.exists("config.yaml"):
    with open("config.yaml", "r", encoding="utf-8") as f:
        MESSAGES = yaml.safe_load(f)

else:
    with open("config_static.yaml", "r", encoding="utf-8") as f:
        MESSAGES = yaml.safe_load(f)
