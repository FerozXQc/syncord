# Syncord

> Use Discord as a makeshift file storage and synchronization server.

Syncord is a lightweight Python-based tool that leverages a Discord bot to store and retrieve files through channels—essentially turning Discord into a pseudo-database or data pipe. It uses Redis for local caching and supports async file operations for efficient transfers.

---

## 🚀 Features

- 📤 Upload files to a Discord channel as persistent backup.
- 📥 Retrieve files from Discord using message history.
- ⚡ Fast and async-based operations using `discord.py` and `aiofiles`.
- 🧠 Redis caching layer for session memory and deduplication.
- 🐳 Optional Docker support for easy deployment.

---

## 📁 Project Structure

```
syncord/
├── bot.py               # Discord bot logic (upload/download)
├── app.py               # Web or CLI entry point (optional)
├── redis_client.py      # Redis connection helper
├── config.env           # Environment variables (tokens, keys)
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker orchestration
└── Dockerfile           # Image definition
```

---

## ⚙️ Installation

### 🔧 Prerequisites

- Python 3.9+
- Redis server running locally or remotely
- A Discord bot token and server setup

### 🐍 Manual Setup

```bash
git clone https://github.com/FerozXQc/syncord
cd syncord
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_target_channel_id
REDIS_URL=redis://localhost:6379
```

Then run the bot:

```bash
python bot.py
```

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

---

## 💡 Usage

Access your Syncord file gateway via:

    http://localhost:8000/docs – Swagger UI to upload/download files.

    The backend automatically relays files through Discord using the bot.

No commands needed inside Discord. All interactions happen via the FastAPI endpoints.

---

## 🧪 Todo / WIP

- [ ] Chunked uploads for large files
- [ ] Indexing and lookup messages
- [ ] Optional compression before sending
- [ ] CLI or Web UI frontend

---

## 📄 License

MIT License. Use at your own risk—Discord isn't designed for long-term storage.

---

## 🧠 Inspiration

Built for fun and fast experiments—Syncord is a side-project exploring how far Discord bots can go in handling unconventional tasks like file storage.
