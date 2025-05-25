# 📘 Distributed Library System

**A fault-tolerant, scalable reservation platform for managing library resources, built with modern web technologies and a distributed Cassandra backend.**

[![Backend Python Application](https://github.com/MichalRedm/bigdata-distributed-app/actions/workflows/python-app.yml/badge.svg)](https://github.com/MichalRedm/bigdata-distributed-app/actions/workflows/python-app.yml)
![Architecture Diagram](https://img.shields.io/badge/Backend-Python%20%7C%20Tornado-blue?logo=python)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-blueviolet?logo=react)
![Database](https://img.shields.io/badge/Database-Cassandra-orange?logo=apachecassandra)
![Deployment](https://img.shields.io/badge/Distributed-Yes-green)

---

## 📚 Project Overview

This system enables users to:

* 📖 View available books across distributed nodes.
* 📝 Reserve books and manage reservations.
* 🔁 Cancel individual or bulk reservations.
* 🔍 See who reserved which book.
* ⚙️ Stress test the system under concurrent loads (for performance evaluation).

Built as a **two-node distributed application** to fulfill course requirements for **Big Data and Distributed Processing**.

---

## 🧠 Tech Stack

| Layer     | Tech                                      |
| --------- | ----------------------------------------- |
| Frontend  | React, TypeScript, SCSS                   |
| Backend   | Python, Tornado                           |
| Database  | Apache Cassandra                          |
| Cluster   | Multi-node Docker (or manual)             |
| Dev Tools | Vite, React Query, Axios, GitHub, VS Code |

---

## 🚀 Quick Start

### ✅ Prerequisites

* Node.js ≥ 18
* Python ≥ 3.10
* Docker (for Cassandra cluster)
* Git

---

### 📦 Setup

1. **Clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/bigdata-distributed-app.git
cd bigdata-distributed-app
```

2. **Install frontend dependencies:**

```bash
cd frontend
npm install
```

3. **Set up backend virtual environment:**

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

4. **Start Cassandra (e.g., via Docker):**

```bash
docker-compose up -d
```

> Ensure multiple nodes are configured in `docker-compose.yml`.

---

### 🧪 Run in Development Mode

From the root directory:

```bash
npm run dev
```

This will concurrently start:

* 🖥️ Frontend at `http://localhost:5173`
* ⚙️ Backend at `http://localhost:8000`

---

## 🧩 Architecture

```text
[Frontend: React + TS]
       ↓ REST API
[Backend: Tornado]
       ↓ CQL
[Cassandra Node 1] ⇄ [Cassandra Node 2] ⇄ [Cassandra Node 3]
```

* Stateless Tornado backend handles business logic and routes.
* Cassandra cluster provides eventual consistency and scalability.
* Stress testing tools simulate heavy concurrent usage.

---

## 📈 Features

* 🔐 Make, update, cancel, and view reservations
* 👥 Track who reserved what
* 🚨 Supports stress tests:

  * Rapid repeated requests
  * Concurrent client races
  * Bulk cancellation and occupancy
* ⚡ Async + non-blocking backend
* 🎨 Stylish responsive frontend UI

---

## 📁 Monorepo Structure

```
bigdata-distributed-app/
├── frontend/      # React app (Vite + TypeScript)
├── backend/       # Tornado app (Python + Cassandra)
├── docs/          # Report, schema, diagrams
├── docker-compose.yml
├── package.json   # Root dev scripts
└── README.md
```

---

## 🧑‍💻 Authors

| Name              | GitHub                                       |
| ----------------- | -------------------------------------------- |
| **Deniz Aksoy**   | [@dka124](https://github.com/dka124)         |
| **Michał Redmer** | [@MichalRedm](https://github.com/MichalRedm) |

---

## 📄 Report & Documentation

> Located in `/docs/`:

* 🧾 System architecture
* 🗃️ Database schema
* 🛠️ Performance analysis
* 🧵 Challenges and conclusions

---

## 💡 Future Work

* Add user authentication (e.g. JWT)
* Admin panel for library management
* GraphQL or gRPC API layer
* Full CI/CD pipeline

---

## 📜 License

This project is part of the **Big Data and Distributed Processing** course at Poznań University of Technology and is not licensed for commercial use.
