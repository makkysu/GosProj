from fastapi import FastAPI
from app.routes.laws import laws

app = FastAPI()

app.include_router(laws)
