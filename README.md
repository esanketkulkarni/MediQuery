# MediQuery

MediQuery is a medical information retrieval system that provides accurate, domain-specific answers to medical queries using trusted medical sources.

## Features

- Topic-based medical query classification
- Domain-specific search filtering (e.g., drugs.com, mayoclinic.org, etc.)
- Real-time answers from trusted medical sources
- Modern React-based UI
- FastAPI backend with Sonar API integration

## Tech Stack

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python 3.11
- Sonar API integration

## Prerequisites

- Docker and Docker Compose
- Sonar API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MediQuery.git
cd MediQuery
```

2. Create a `.env` file in the root directory:
```bash
SONAR_API_KEY=your_sonar_api_key_here
```

3. Build and run the application by running below inside project directory:
```bash
docker-compose up
```

4. To bring down application run below in another terminal:
```bash
docker-compose down
```

## Usage

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000


## Project Structure

```
MediQuery/
├── mediquery_ui/          # Frontend Next.js application
├── Mediquery_sonar_api/   # Backend FastAPI application
├── docker-compose.yml     # Docker composition file
└── README.md             # This file
```

## Development

Both frontend and backend services support hot-reloading in development mode. Any changes made to the source code will be reflected immediately.

### Frontend Development
The frontend code is in the `mediquery_ui` directory. It uses Next.js with TypeScript and Tailwind CSS.

### Backend Development
The backend code is in the `Mediquery_sonar_api` directory. It uses FastAPI with Python 3.11.

## API Endpoints

- `POST /ask`: Submit a medical query
  - Request body: `{"question": "your medical question"}`
  - Returns: Topic classification, domain filters, answer, and citations

## Contributors

- Sanket Kulkarni

