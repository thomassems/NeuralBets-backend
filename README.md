# NeuralBets Backend

> A scalable, microservices-based backend platform for sports betting analytics and odds management, built with modern Python technologies and containerized deployment.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)](https://www.mongodb.com/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-WSGI%20Server-298729.svg)](https://gunicorn.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Development](#development)

## 🎯 Overview

NeuralBets Backend is a production-ready microservices architecture designed to handle sports betting data, odds aggregation, and user management. The system integrates with external sports betting APIs to fetch real-time odds, stores and processes betting data, and provides RESTful APIs for frontend consumption.

### Key Highlights

- **Microservices Architecture**: Modular design with independent, scalable services
- **Containerized Deployment**: Docker and Docker Compose for easy deployment and scaling
- **Data Modeling**: Type-safe schemas with validation and transformation utilities
- **Repository Pattern**: Clean separation of data access logic
- **Production-Ready**: Gunicorn WSGI server, health checks, error handling

## 🏗️ Architecture

The backend follows a **microservices architecture** with the following services:

```
┌─────────────────────────────────────────────────────────┐
│                    NeuralBets Backend                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ User Service │  │ Bet Service  │  │ Auth Service │ │
│  │   (Port 8081)│  │  (Port 8082) │  │  (Port TBD)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                    ┌───────▼────────┐                   │
│                    │  Shared Utils  │                   │
│                    │  (Constants,   │                   │
│                    │   Validators)  │                   │
│                    └───────┬────────┘                   │
│                            │                            │
│         ┌──────────────────┼──────────────────┐         │
│         │                  │                  │         │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐  │
│  │  MongoDB    │  │ External API  │  │   Docker     │  │
│  │  Database   │  │  Integration  │  │  Containers  │  │
│  └─────────────┘  └───────────────┘  └──────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Service Responsibilities

- **User Service**: User management and authentication
- **Bet Service**: Odds aggregation, betting data management, external API integration
- **Auth Service**: Authentication and authorization (planned)
- **Account Service**: User account management (planned)
- **Wallet Service**: Transaction and balance management (planned)
- **Prediction Service**: ML-based predictions (planned)

## 🛠️ Technologies

### Core Stack

- **Python 3.11** - Modern Python with latest features
- **Flask 3.0.3** - Lightweight web framework for REST APIs
- **Gunicorn 22.0.0** - Production WSGI HTTP Server
- **MongoDB** - NoSQL database for flexible data storage
- **PyMongo** - MongoDB driver for Python

### DevOps & Infrastructure

- **Docker** - Containerization for consistent deployments
- **Docker Compose** - Multi-container orchestration
- **Python-dotenv** - Environment variable management

### Architecture Patterns

- **Microservices** - Service-oriented architecture
- **Repository Pattern** - Data access abstraction
- **Schema/Model Pattern** - Type-safe data structures
- **Blueprint Pattern** - Modular route organization

### External Integrations

- **The Odds API** - Real-time sports betting odds aggregation

## ✨ Features

### Bet Service

- ✅ Real-time odds fetching from multiple bookmakers
- ✅ Sports data aggregation and caching
- ✅ Event data management
- ✅ Data transformation and normalization
- ✅ Schema-based validation
- ✅ MongoDB persistence with optimized queries
- ✅ Health check endpoints

### Data Management

- ✅ **Dual Storage Strategy**: Full and simplified data formats
- ✅ **Type-Safe Schemas**: Dataclass-based models with validation
- ✅ **Automatic Transformation**: API data → Simplified format
- ✅ **JSON Serialization**: Handles ObjectId, datetime, nested structures
- ✅ **Data Validation**: Pre-storage validation for data integrity

### Development Features

- ✅ Hot-reload support for development
- ✅ Comprehensive error handling
- ✅ Logging and debugging utilities
- ✅ Environment-based configuration
- ✅ Shared utilities package for code reuse

## 📁 Project Structure

```
NeuralBets-backend/
├── bet-service/              # Betting odds and data service
│   ├── routes/              # API route definitions
│   │   └── api_routes.py
│   ├── schemas.py           # Data models and transformations
│   ├── respository.py       # Data access layer
│   ├── external_api_client.py  # External API integration
│   ├── config.py            # Service configuration
│   ├── app.py               # Flask application entry point
│   ├── Dockerfile           # Service containerization
│   └── requirements.txt     # Python dependencies
│
├── user-service/            # User management service
│   ├── routes/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── shared_utils/            # Shared code package
│   ├── constants.py         # Shared constants and validators
│   └── setup.py             # Package configuration
│
├── docker-compose.yml       # Multi-service orchestration
├── .env                     # Environment variables (not in repo)
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- MongoDB instance (or use Docker)
- API key for The Odds API

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NeuralBets-backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Build and start services**
   ```bash
   docker compose up --build
   ```

4. **Verify services are running**
   ```bash
   # Check service health
   curl http://localhost:8081/health  # User Service
   curl http://localhost:8082/health   # Bet Service
   ```

### Development Setup

For local development without Docker:

```bash
# Install shared utilities
cd shared_utils
pip install -e .

# Install service dependencies
cd ../bet-service
pip install -r requirements.txt

# Run service
python app.py
```

## 📡 API Endpoints

### Bet Service (Port 8082)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service health check |
| `/health` | GET | Health status |
| `/bets/status` | GET | API status |
| `/bets/getdefaultodds` | GET | Get cached/default odds |
| `/bets/getodds` | GET | Get odds for specific sport |
| `/bets/getevents` | GET | Get events for sport |
| `/bets/getdefaultevents` | GET | Get default events |

### User Service (Port 8081)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service health check |
| `/health` | GET | Health status |
| `/users/status` | GET | API status |

## 💻 Development

### Code Organization

- **Schemas** (`schemas.py`): Define data structures, transformations, and validation
- **Repository** (`respository.py`): Handle all database operations
- **Routes** (`routes/api_routes.py`): Thin HTTP layer, delegates to repository
- **External Client** (`external_api_client.py`): Third-party API integration

### Adding a New Service

1. Create service directory with `app.py`, `Dockerfile`, `requirements.txt`
2. Add service to `docker-compose.yml`
3. Use shared utilities from `shared_utils/` package
4. Follow existing patterns for consistency

### Best Practices

- ✅ Use schemas for all data structures
- ✅ Validate data before storage
- ✅ Transform data on storage (not retrieval)
- ✅ Handle errors gracefully
- ✅ Use type hints where possible
- ✅ Document functions and classes

## 🔧 Configuration

Services are configured via environment variables:

- `ODDS_API_KEY`: API key for The Odds API
- `MONGODB_URI`: MongoDB connection string
- `FLASK_ENV`: Environment (development/production
