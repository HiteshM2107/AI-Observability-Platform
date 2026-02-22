# AI Observability Platform

A distributed, real-time log monitoring system with AI-driven anomaly detection and incident summarization.

This project simulates a production-grade observability pipeline using microservices, Redis streaming, PostgreSQL persistence, sliding-window anomaly detection, and a live React dashboard.

---

## Overview

Modern distributed systems generate massive volumes of logs. This platform demonstrates how to:

- Collect logs from multiple services  
- Stream them through a message broker  
- Detect anomalies using sliding-window error rate logic  
- Trigger AI-based incident summaries  
- Persist incidents and metrics  
- Visualize everything in a real-time dashboard  

This system mimics the architecture of observability tools like Datadog or Splunk, with AI integration for automated incident analysis.

---

## Architecture

```
auth-service         payment-service
        \               /
         \             /
          → ingestion-service → Redis → processor-service → PostgreSQL
                                                  |
                                                  ↓
                                             ai-service
                                                  |
                                                  ↓
                                            React Dashboard
```

### Services

- **auth-service**  
  Simulates authentication logs.

- **payment-service**  
  Simulates transaction logs with configurable error rates.

- **ingestion-service (FastAPI)**  
  Receives structured logs and pushes them into Redis.

- **processor-service**  
  - Implements sliding-window anomaly detection  
  - Computes real-time error rate  
  - Stores metrics  
  - Triggers AI summaries  
  - Persists incidents  

- **ai-service (FastAPI)**  
  Generates incident summaries (mock AI service, easily extendable to OpenAI API).

- **Redis**  
  Streaming layer between ingestion and processing.

- **PostgreSQL**  
  Stores incidents and time-series metrics.

- **React Dashboard**  
  Displays metrics and incidents in real time.

---

## Anomaly Detection Logic

The system uses a **sliding-window error rate approach**:

- Maintains a rolling window of the last 20 logs
- Computes error rate within that window
- Triggers incident if:

```
error_rate > 40%
```

### Severity Classification

| Error Rate | Severity |
|------------|----------|
| > 70%      | HIGH     |
| > 50%      | MEDIUM   |
| > 40%      | LOW      |

A cooldown mechanism prevents repeated alert flooding until the system stabilizes.

---

## Metrics Tracked

- Total logs processed  
- Total errors  
- Cumulative error rate (%)  
- Sliding window error rate  
- Timestamped metrics for trend visualization  

---

## Dashboard Features

- Dark-themed enterprise UI  
- Real-time auto-refresh (5 seconds)  
- Error rate trend visualization (Recharts)  
- Severity-tagged incidents  
- Server-side service filtering  
- Modular React architecture  

 This is how the Frontend looks-
<img width="1680" height="907" alt="Screenshot 2026-02-21 at 8 55 43 PM" src="https://github.com/user-attachments/assets/27451a0a-3b7d-49ea-a763-bcbbb71fb6ee" />
<img width="1680" height="907" alt="Screenshot 2026-02-21 at 8 55 43 PM" src="https://github.com/user-attachments/assets/7ce25464-9648-4477-a61b-774b9a5a6c6a" />
The highlighted sections feature a service-level filtering feature and real-time status & refresh clock:  Users can dynamically select a specific microservice from the dropdown menu to view incidents related only to that service. This filtering is performed server-side via query parameters: `GET /incidents?service=payment-service`. This ensures: reduced data transfer, scalable querying and clean separation of frontend and backend responsibilities. The dashboard includes a live status indicator and timestamp displaying when data was last fetched. This mimics real observability platforms where data recency is critical.

---

## Tech Stack

### Backend
- Python
- FastAPI
- Redis
- PostgreSQL
- Docker / Docker Compose

### Frontend
- React
- Axios
- Recharts

---

## Running Locally

### Clone Repository

```bash
git clone <your-repo-url>
cd ai-log-monitor
```

### Start Backend Services

```bash
docker compose up --build
```

This starts:

- auth-service  
- payment-service  
- ingestion-service  
- processor-service  
- ai-service  
- Redis  
- PostgreSQL  

### Start Frontend

In a new terminal:

```bash
cd frontend
npm install
npm start
```

Open:

```
http://localhost:3000
```

---

## API Endpoints

```
GET  /incidents
GET  /incidents?service=payment-service
GET  /metrics
GET  /services
POST /log
```

---

## Design Decisions

### Why Redis?
Provides asynchronous decoupling between ingestion and processing layers, allowing scalable log streaming.

### Why Sliding Window Detection?
Short-term behavioral spikes are more indicative of incidents than cumulative averages.

### Why Server-Side Filtering?
Reduces unnecessary data transfer and scales better with increasing incident volume.

### Why Modular Frontend?
Improves maintainability, separation of concerns, and scalability.

---

## Future Improvements

- Time-based anomaly detection (e.g., last 30 seconds)
- Per-service error rate tracking
- WebSocket-based real-time updates
- Integration with real LLM (OpenAI API)
- Kubernetes deployment
- Authentication & RBAC
- Pagination for large incident volumes

---

## What This Project Demonstrates

- Distributed systems design  
- Event-driven architecture  
- Microservice communication  
- Real-time analytics  
- AI integration patterns  
- Full-stack engineering  
