<a id="readme-top"></a>
<h1 align="center">
    RedTickets
</h1>

![tickets_embed]

<p align="center">
    Discord ticketing helper for game communities
    <br />
    <a href="https://redmarket.click">Visit Site</a>
    &middot;
    <a href="https://github.com/RedR1ghtHand/RedTickets/issues/new?labels=bug&template=bug-report.md">Report Bug</a>
    &middot;
    <a href="https://github.com/RedR1ghtHand/RedTickets/issues/new?labels=enhancement&template=feature-request.md">Request Feature</a>
</p>

&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;

## About
RedTickets is a Discord bot written in Python that lets guild memebers create guided support tickets via an interactive message, routes each ticket into the correct category channel, and keeps your staff sane with business-hour reminders and simple controls.

## Features
- fully asynchronous, powered by `discord.py 2.4`
- persistent select menu so users can spawn a ticket from one embed at any time
- modal flow collects nickname, time of incident, and a detailed description before opening a channel
- automatic channel naming/topic templating with per-reason icons from `config_static.yaml`
- business-hours warnings generated from timezone-aware config (weekend closures supported)
- staff control panel with “close” / “move” buttons tied to permission checks
- admin `/ticket_send_main` command to purge + repost the master embed in the configured channel
- centralized logging setup with configurable log level

<img width="420" height="320" alt="ticket modal" src="https://github.com/user-attachments/assets/ccdb3e4c-0fd4-4e97-b228-6ddf4027c9bd" />

## Setup and Startup

### Discord bot
- Create an app at the [Discord Developer Portal](https://discord.com/developers/applications)
- Add a Bot user, copy its token
- Under OAuth2 → URL Generator select:
  1. `bot` and `applications.commands` scopes
  2. Bot Permissions:
      - *View Channels*
      - *Send Messages*
      - *Manage Channels*
      - *Manage Messages*
      - *Embed Links*
      - *Attach Files*
      - *Use Slash Commands*
  3. Invite the bot to your server using the generated URL

### .env Setup
Copy project from git  
```bash
git clone https://github.com/RedR1ghtHand/RedTickets.git
cd RedTickets
```

Create a `.env` in the project root:
```env
# ==========================
# Discord Bot Configuration
# ==========================
BOT_TOKEN=your_discord_bot_token_here

# ==========================
# Guild & Channel IDs
# ==========================
# Main guild that will receive slash commands/tickets
ALLOWED_GUILD=123456789012345678
# Channel where the ticket embed + select menu lives
CREATE_TICKET_CHANNEL=135791357913579135

# ==========================
# Logging Configuration
# ==========================
# DEBUG / INFO / WARNING / ERROR
LOG_LEVEL=INFO
```

> [!TIP]  
> IDs can be copied in Discord by enabling Developer Mode, right-clicking the guild or channel, and selecting “Copy ID”.

### Customize ticket reasons & messages
- All copy, emoji, color, and channel target settings live in `config_static.yaml`
- Duplicate that file into `config.yaml` if you want to override the defaults without touching git
- Channel list entries map select options to Discord category IDs; each entry supports `{reason, id, icon}`
- `messages.embeds.business_hours` controls timezone + daily windows and the reminder template

### Local development
1. Install Python ≥ 3.10
2. Install dependencies (uv or pip, whichever you prefer):
   ```bash
   pip install -r <(uv pip compile pyproject.toml)
   # or simply:
   pip install -e .
   ```
3. Run the bot:
   ```bash
   python -m main
   ```

### Production tips
- Keep the bot online with a process manager (systemd, pm2, Docker — your choice)
- Grant the bot Manage Channels in every category that will host tickets
- Use `/ticket_send_main` after redeploys to refresh the select menu message
- Configure `LOG_LEVEL=INFO` (or `WARNING`) in production to avoid noise

<p align="right">(<a href="#readme-top">back to top</a>)</p>

