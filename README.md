# **Hotel Reservation System**

Sistem Reservasi Hotel berbasis **FastAPI**, dibangun menggunakan pendekatan **Domain-Driven Design (DDD)**.
Arsitektur sistem dibuat modular dengan pemisahan **Domain**, **Application**, **Infrastructure**, **API**, **Authentication**, **Testing (TDD)**, **CI/CD**, dan **Docker Containerization**.

---

# **Quick Start**

## **Using Docker**

### Jalankan aplikasi

```bash
docker compose up app
```

### Jalankan seluruh test

```bash
docker compose up test
```

### Mode development (hot reload)

```bash
docker compose up dev
```

---

# **Local Development**

### Install dependencies

```bash
uv sync
```

### Start development server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### Run tests with coverage

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Code quality checks

```bash
uv run ruff check app/ tests/
uv run black app/ tests/
uv run isort app/ tests/
```

---

# **Project Overview**

## **Architecture**

```
HOTEL-RESERVATION/
├── .github/
│   └── workflows/
│       └── ci.yml                     # CI Pipeline
│
├── backend/
│   ├── src/
│   │   ├── domain/                    # Domain Layer
│   │   │   ├── entities/              # Aggregate Roots / Entities
│   │   │   │   ├── reservation.py
│   │   │   │   └── reservation_detail.py
│   │   │   └── value_objects/
│   │   │       └── value_objects.py
│   │   │
│   │   ├── application/               # Use Cases
│   │   │   └── reservation_service.py
│   │   │
│   │   ├── infrastructure/            # Repository, Auth, etc.
│   │   │   ├── reservation_repository.py
│   │   │   └── auth/
│   │   │       ├── jwt_handler.py
│   │   │       └── user_repository.py
│   │   │
│   │   ├── api/                       # Routing & Controllers
│   │   │   ├── reservation_controller.py
│   │   │   ├── auth_controller.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── tests/                         # TDD Test Suite
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   ├── test_api_extended.py
│   │   ├── test_auth.py
│   │   ├── test_main.py
│   │   ├── test_repository.py
│   │   ├── test_service.py
│   │   ├── test_aggregate.py
│   │   └── test_value_objects.py
│   │
│   ├── Dockerfile                     # Backend Dockerfile
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── requirements.txt
│
└── frontend/
```

---

# **API Documentation**

Base URL:

```
http://localhost:8000
```

## **Authentication Endpoints**

| Method | Endpoint             | Description                    |
| ------ | -------------------- | ------------------------------ |
| POST   | `/api/auth/register` | Register user                  |
| POST   | `/api/auth/login`    | Login user (returns JWT)       |
| GET    | `/api/auth/me`       | Get authenticated user profile |

---

# **Reservation Endpoints**

| Method | Endpoint                                             | Description             |
| ------ | ---------------------------------------------------- | ----------------------- |
| POST   | `/api/reservations/`                                 | Create new reservation  |
| GET    | `/api/reservations/`                                 | Get all reservations    |
| GET    | `/api/reservations/{reservation_id}`                 | Get reservation by ID   |
| DELETE | `/api/reservations/{reservation_id}`                 | Delete reservation      |
| POST   | `/api/reservations/{reservation_id}/rooms`           | Add room to reservation |
| POST   | `/api/reservations/{reservation_id}/confirm-payment` | Confirm payment         |
| POST   | `/api/reservations/{reservation_id}/confirm`         | Confirm reservation     |
| POST   | `/api/reservations/{reservation_id}/cancel`          | Cancel reservation      |

---

# **Reservation Workflow**

### **Status Flow**

1. **BOOKED**
2. **PAID**
3. **CONFIRMED**
4. **CANCELLED**

### **Rules**

* Tidak bisa menambah kamar jika status **CANCELLED**
* Tidak bisa melakukan pembayaran setelah **CANCELLED**
* Status tidak bisa kembali ke status sebelumnya

---

# **Example Payloads**

### Create Reservation

```json
{
  "customer_id": "CUST-001",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-03",
  "room_details": [
    {
      "room_id": "ROOM-001",
      "room_type": "Deluxe",
      "number_of_guests": 2,
      "price_per_night": 500000
    }
  ]
}
```

### Add Room

```json
{
  "room_id": "ROOM-002",
  "room_type": "Standard",
  "number_of_guests": 1,
  "price_per_night": 300000
}
```

### Confirm Payment

```json
{
  "payment_id": "PAY-001"
}
```

---

# **Example Responses**

## Create Reservation Response

```json
{
  "reservation_id": "c2cec82a-8576-4ba5-a6b1-58ec381e7326",
  "customer_id": "CUST-001",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-03",
  "number_of_nights": 2,
  "booking_status": "BOOKED",
  "reservation_details": [
    {
      "detail_id": "a0a2ddc7-f2b5-4370-886f-151457ddcb8e",
      "room_id": "ROOM-001",
      "room_type": "Deluxe",
      "number_of_guests": 2,
      "price_per_night": 500000
    }
  ],
  "total_amount": 1000000,
  "currency": "IDR",
  "payment_id": null,
  "created_at": "2025-12-01T10:00:00",
  "updated_at": "2025-12-01T10:00:00"
}
```

---

## Add Room Response

```json
{
  "reservation_id": "c2cec82a-8576-4ba5-a6b1-58ec381e7326",
  "customer_id": "CUST-001",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-03",
  "number_of_nights": 2,
  "booking_status": "BOOKED",
  "reservation_details": [
    {
      "detail_id": "UUID-1",
      "room_id": "ROOM-001",
      "room_type": "Deluxe",
      "number_of_guests": 2,
      "price_per_night": 500000
    },
    {
      "detail_id": "UUID-2",
      "room_id": "ROOM-002",
      "room_type": "Standard",
      "number_of_guests": 1,
      "price_per_night": 300000
    }
  ],
  "total_amount": 1300000,
  "currency": "IDR",
  "payment_id": null,
  "created_at": "2025-12-01T10:00:00",
  "updated_at": "2025-12-01T10:05:00"
}
```

---

## Confirm Payment Response

```json
{
  "reservation_id": "c2cec82a-8576-4ba5-a6b1-58ec381e7326",
  "customer_id": "CUST-001",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-03",
  "number_of_nights": 2,
  "booking_status": "PAID",
  "reservation_details": [
    {
      "detail_id": "UUID-1",
      "room_id": "ROOM-001",
      "room_type": "Deluxe",
      "number_of_guests": 2,
      "price_per_night": 500000
    }
  ],
  "total_amount": 1000000,
  "currency": "IDR",
  "payment_id": "PAY-001",
  "created_at": "2025-12-01T10:00:00",
  "updated_at": "2025-12-01T11:00:00"
}
```

---

# **Testing (TDD)**

## Struktur Test

```
tests/
├── test_api.py
├── test_api_extended.py
├── test_auth.py
├── test_service.py
├── test_repository.py
├── test_value_objects.py
├── test_aggregate.py
├── test_main.py
└── conftest.py
```

### Menjalankan semua test

```bash
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### Coverage

* **171 test cases**
* **ALL PASSED**
* **Coverage: 96.39%**

---

# **Continuous Integration (CI)**

### CI mencakup:

* Linting (ruff, black, isort)
* Test runner
* Coverage check & coverage.xml
* Build Docker image
* Summary report

### Trigger

* Push ke branch `main`
* Pull Request

---

# **Docker Usage**

### Build image

```bash
docker build -t hotel-reservation .
```

### Run container

```bash
docker run -p 8000:8000 hotel-reservation
```

### Docker Compose

```bash
docker compose up
```

Access:

```
http://localhost:8000
```

---

# **Development Tools**

* Python 3.11+
* FastAPI + Uvicorn
* uv package manager
* pytest + pytest-cov
* ruff, black, isort
* mypy
* Docker & Docker Compose

---

# **Author**

**Nama:** Aulia Azka Azzahra
**NIM:** 18223131
**Mata Kuliah:** II3160 – Teknologi Sistem Terintegrasi

---
