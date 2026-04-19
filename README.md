# XLA Stats Bot

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/telegram-bot-blue.svg)](https://t.me/xlastatsbot)

**Telegram bot for monitoring Scala (XLA) mining pool statistics in real-time.**

**Example bot:** [@xlastatsbot](https://t.me/xlastatsbot)

## Features

- 📊 **Real-time pool statistics** - Network difficulty, hashrate, pool stats
- ⏰ **Periodic notifications** - Automatic updates every N minutes
- 🚨 **Threshold alerts** - Custom alerts for hashrate, difficulty, miners count
- 💰 **Wallet statistics** - Check balance, hashrate, workers, payments
- 🔄 **Auto-refresh data** - Always up-to-date information
- 📱 **Inline keyboard interface** - Easy navigation without commands
- 🛡️ **Tor/Proxy support** - Optional proxy support for privacy

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Launch the bot and see welcome message |
| `/stats` | Get current pool statistics |
| `/wallet` | Check wallet balance and mining stats |
| `/menu` | Show main menu |
| `/help` | Show help message with all links |
| `/delete_alert <id>` | Delete an existing alert |

## Links

### Official Scala (XLA) Resources

| Platform | Link |
|----------|------|
| 🌐 **GitHub** | [Scala-Network](https://github.com/scala-network) |
| 💬 **Discord** | [XLA Community](https://discord.gg/W9W6CxSTt8) |
| 📱 **Matrix** | [#scala:unredacted.org](https://matrix.to/#/#scala:unredacted.org) |
| ✈️ **Telegram** | [Scala Chat](https://t.me/scalaofficial) |
| 🔍 **Explorer** | [Scala Explorer](https://explorer.scalaproject.io) |
| ⛏️ **Pool** | [pool.scalaproject.io](https://pool.scalaproject.io) |

### Bot Resources

| Platform | Link |
|----------|------|
| 🐙 **Bot GitHub** | [XLA-stats-bot](https://github.com/post-hum/XLA-stats-bot) |
| 🤖 **Example Bot** | [@xlastatsbot](https://t.me/xlastatsbot) |

## Installation

### Requirements

- Python 3.9+
- SQLite3
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/post-hum/XLA-stats-bot.git
cd XLA-stats-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
DB_PATH=sqlite+aiosqlite:///xla_bot.db
POLL_INTERVAL=300
USE_PROXY=False
# PROXY_URL=socks5://127.0.0.1:9050  # For Tor/SOCKS5 proxy
```

4. **Run the bot:**
```bash
python bot.py
```

### Running with Tor (optional)

```bash
torsocks python3 bot.py
```

## Project Structure

```
XLA-stats-bot/
├── bot.py              # Main entry point
├── config.py           # Configuration
├── fetcher.py          # Pool API fetcher
├── keyboards.py        # Inline keyboards
├── scheduler.py        # Alert scheduler
├── db/
│   ├── models.py       # SQLAlchemy models
│   └── crud.py         # Database operations
└── handlers/
    ├── common.py       # Common commands (start, help, stats)
    ├── alerts.py       # Alert management
    ├── stats.py        # Statistics display
    └── wallet.py       # Wallet statistics
```

## Usage Examples

### Get pool statistics
```
/stats
```

### Check wallet balance
```
/wallet
Send: SvkFweFR7GeAGus6pt7jpg5ZYEvZgqjaUEnYnkqqBRQg57LUuKCMY849e79oVsmDbH9jYH5BVyLJMSweBAQ6YdPB1ekUGaPwc
```

### Set periodic alert
1. Click "⏰ Periodic Alert"
2. Send interval in minutes (5-1440)

### Delete an alert
```
/delete_alert 2
```

## Troubleshooting

### API timeout issues
If you experience slow API responses, increase timeout in `handlers/wallet.py`:
```python
async with session.get(url, timeout=120) as resp:
```

### Proxy connection issues
Make sure Tor is running and `USE_PROXY=True` in `.env`

### Database errors
Delete `xla_bot.db` and restart the bot to recreate database

## Donations

If you find this bot useful, you can support its development:

**XLA (Scala) address:**
```
SvkFweFR7GeAGus6pt7jpg5ZYEvZgqjaUEnYnkqqBRQg57LUuKCMY849e79oVsmDbH9jYH5BVyLJMSweBAQ6YdPB1ekUGaPwc
```
## License

MIT License - see [LICENSE](LICENSE) file for details


**❤️ Thanks for using XLA Stats Bot!**
