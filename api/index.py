from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics
import numpy as np
import json
import os

app = FastAPI()

# Allow POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load the telemetry JSON file
data_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "q-vercel-latency.json"
)

with open(data_file, "r") as f:
    telemetry = json.load(f)


class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: float


@app.post("/")
def calculate_metrics(request: RequestData):

    result = {}

    for region in request.regions:

        records = [
            record
            for record in telemetry
            if record["region"] == region
        ]

        latencies = [
            record["latency_ms"]
            for record in records
        ]

        uptimes = [
            record["uptime_pct"]
            for record in records
        ]

        breaches = sum(
            1
            for latency in latencies
            if latency > request.threshold_ms
        )

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": breaches
        }

    return result