# CincyJunkBot - Cincinnati/NKY Junk Removal Lead Generator

Automated bot that finds junk removal customers in Cincinnati and Northern Kentucky areas.

## Quick Deploy to Render.com (Free)

1. **Create GitHub Repository** - Upload these files:
   - `app.py`
   - `config.py`
   - `requirements.txt`
   - `Procfile`
   - `bot/` folder (all files)

2. **Deploy**:
   - Go to [Render.com](https://render.com)
   - Connect GitHub → New Web Service
   - Select your repo
   - Settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`

3. **Optional Environment Variables**:
   - `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram
   - `TELEGRAM_CHAT_ID` - Your Telegram chat ID

## Features:
- Scrapes Cincinnati/NKY Craigslist every 60 seconds
- Filters for $175+ jobs
- Prioritizes by zip code (Mason, Hyde Park, West Chester, etc.)
- Lead scoring 0-100
- Telegram/SMS alerts for hot leads

## Demo Dashboard:
https://grlyp1i65xu1.space.minimax.io
