# 🏈 Advanced Sports Betting Platform

A modern, AI-powered sports betting application built with FastAPI, React, and deployed on AWS. This platform integrates multiple sports APIs (ESPN, The Rundown, All-Sports) to provide real-time data and uses machine learning to recommend high-probability bets.

## 🚀 Features

### Core Functionality
- **Multi-API Integration**: ESPN, The Rundown, All-Sports DB
- **AI-Powered Predictions**: Machine learning models for bet recommendations
- **DraftKings Integration**: Direct bet placement via API
- **Real-time Data**: Live odds and sports event updates
- **Portfolio Management**: Track betting performance and analytics

### Technical Features
- **Microservices Architecture**: Containerized backend and frontend
- **Cloud-Native**: Fully deployed on AWS with auto-scaling
- **High Performance**: Redis caching and PostgreSQL database
- **Secure**: JWT authentication and API rate limiting
- **Monitoring**: Prometheus metrics and structured logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │────│   (FastAPI)     │────│   APIs          │
│   Port: 3000    │    │   Port: 8000    │    │   ESPN/DK/etc   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         │              │   PostgreSQL    │             │
         └──────────────│   Database      │─────────────┘
                        │   Port: 5432    │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   Redis Cache   │
                        │   Port: 6379    │
                        └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with async support
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Component library
- **React Query**: Data fetching and caching
- **Zustand**: State management
- **Recharts**: Data visualization

### Infrastructure
- **AWS ECS Fargate**: Container orchestration
- **AWS RDS**: Managed PostgreSQL
- **AWS ElastiCache**: Managed Redis
- **AWS ALB**: Load balancing
- **AWS ECR**: Container registry
- **CloudFormation**: Infrastructure as Code

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- AWS CLI (for deployment)

### Local Development

1. **Clone and setup environment**
```bash
git clone https://github.com/siggy2543/mysportsbet.git
cd sports_app
cp variables.env .env
# Edit .env with your API keys
```

2. **Start with Docker Compose**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
