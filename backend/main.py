from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collectors.aws import collect_aws_resources
from collectors.azure import collect_azure_resources
from collectors.gcp import collect_gcp_resources
import os

app = FastAPI(
    title="Cloud Resource Map API",
    description="Multi-cloud resource visibility — beginner friendly",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/resources/aws")
def aws_resources():
    try:
        return collect_aws_resources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resources/azure")
def azure_resources():
    try:
        return collect_azure_resources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resources/gcp")
def gcp_resources():
    try:
        return collect_gcp_resources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
