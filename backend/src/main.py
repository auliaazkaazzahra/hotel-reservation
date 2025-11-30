from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.reservation_controller import router as reservation_router
from .api.auth_controller import router as auth_router
from .config import settings

# Inisialisasi FastAPI app
app = FastAPI(
    title="Hotel Reservation System API",
    description="API untuk Sistem Reservasi Hotel - Implementation DDD Pattern",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(reservation_router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Hotel Reservation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "authentication": "JWT Bearer Token",
        "default_users": [
            {"username": "admin", "password": "admin123"},
            {"username": "user", "password": "user123"}
        ]
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hotel-reservation-api"
    }