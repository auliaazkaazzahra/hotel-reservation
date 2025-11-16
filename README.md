# Hotel Reservation System

Sistem Reservasi Hotel ini dibangun menggunakan pendekatan **Domain-Driven Design (DDD)** dan framework **FastAPI**. Struktur ini dibuat modular sesuai konsep DDD: domain, application, infrastructure, dan API layer.

---

## **Struktur Proyek**

```
HOTEL-RESERVATION/
├── backend/
│   └── src/
│       ├── domain/              # Domain Layer (Core Business Logic)
│       │   ├── entities/        # Aggregate Root & Entities
│       │   │   ├── reservation.py
│       │   │   └── reservation_detail.py
│       │   └── value_objects/   # Value Objects
│       │       └── value_objects.py
│       ├── application/         # Application Layer (Use Cases)
│       │   └── reservation_service.py
│       ├── infrastructure/      # Infrastructure Layer
│       │   └── reservation_repository.py
│       ├── api/                 # API Layer (Controllers)
│       │   └── reservation_controller.py
│       └── main.py              # FastAPI Entry Point
├── frontend/
└── README.md
```

---

## **Cara Menjalankan Aplikasi**

### **1. Setup Virtual Environment**

```bash
cd backend
python -m venv venv

# Windows
env\Scripts\activate
# Linux / Mac
source venv/bin/activate
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Jalankan Server**

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server berjalan di: **[http://localhost:8000](http://localhost:8000)**

---

## **API Documentation**

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## **Available Endpoints**

| Method | Endpoint                                             | Deskripsi               |
| ------ | ---------------------------------------------------- | ----------------------- |
| POST   | `/api/reservations/`                                 | Create New Reservation  |
| GET    | `/api/reservations/`                                 | Get All Reservations    |
| GET    | `/api/reservations/{reservation_id}`                 | Get Reservation by ID   |
| DELETE | `/api/reservations/{reservation_id}`                 | Delete Reservation      |
| POST   | `/api/reservations/{reservation_id}/rooms`           | Add Room to Reservation |
| POST   | `/api/reservations/{reservation_id}/confirm-payment` | Confirm Payment         |
| POST   | `/api/reservations/{reservation_id}/confirm`         | Confirm Reservation     |
| POST   | `/api/reservations/{reservation_id}/cancel`          | Cancel Reservation      |

---

## **Testing dengan cURL**

### **1. Create Reservation**

```bash
curl -X POST "http://localhost:8000/api/reservations/" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### **2. Get Reservation**

```bash
curl -X GET "http://localhost:8000/api/reservations/{reservation_id}"
```

### **3. Confirm Payment**

```bash
curl -X POST "http://localhost:8000/api/reservations/{reservation_id}/confirm-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "PAY-001"
  }'
```

### **4. Cancel Reservation**

```bash
curl -X POST "http://localhost:8000/api/reservations/{reservation_id}/cancel"
```

---

## **Author**

**Nama:** *Aulia Azka Azzahra*
**NIM:** *18223131*
**Mata Kuliah:** **II3160 - Teknologi Sistem Terintegrasi**
