from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import analysis, config, devices, emission, locations, readings, sensors


app = FastAPI(
    title="SIMOSI API",
    description="Smart IoT Monitoring System — Environmental monitoring for mining operations",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── v1 Routes ────────────────────────────────────────────────
app.include_router(devices.router)      # /api/v1/devices
app.include_router(readings.router)     # /api/v1/readings
app.include_router(analysis.router)     # /api/v1/analysis
app.include_router(emission.router)     # /api/v1/emission
app.include_router(config.router)       # /api/v1/config
app.include_router(locations.router)    # /api/v1/locations
app.include_router(sensors.router)      # /api/v1/sensors


@app.get("/")
def read_root():
    return {"status": "API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

