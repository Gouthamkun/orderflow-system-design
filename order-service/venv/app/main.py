from fastapi import FastAPI
from app.pubsub import start_listener
from app.database import engine
from app.models import Base
from app.routes import router

app = FastAPI(title="OrderFlow")


@app.on_event("startup")
def create_tables():

    Base.metadata.create_all(bind=engine)

    start_listener()

app.include_router(router)


@app.get("/")
def home():
    return {"message": "OrderFlow is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
