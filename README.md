# 🎡 Wheel of Fortune - Django Application

A real-time spinning wheel application with admin controls, built with Django, Channels, and WebSockets.

## Features

- 🎡 Interactive spinning wheel
- 👤 User authentication (Login/Signup/Logout)
- 🎯 Admin panel with forced winner control
- 📊 Real-time updates via WebSockets
- 🎨 Tailwind CSS for styling
- 🔄 Redis for channel layers

## Tech Stack

- **Backend**: Django 6.0.6
- **WebSockets**: Django Channels
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Cache/Channel Layer**: Redis
- **Frontend**: Tailwind CSS
- **Deployment**: Render.com

## Local Development

### Prerequisites

- Python 3.11+
- Redis (for WebSocket support)
- PostgreSQL (optional, for production-like environment)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wheel-project.git
cd wheel-project