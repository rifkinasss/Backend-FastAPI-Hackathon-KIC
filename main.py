from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import analysis, config, devices, dht22, emission, locations, sensors


app = FastAPI(title="IOT Fuzzy Kideco API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(config.router)
app.include_router(devices.router)
app.include_router(dht22.router)
app.include_router(emission.router)
app.include_router(locations.router)
app.include_router(sensors.router)


@app.get("/")
def read_root():
    return {"status": "API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

