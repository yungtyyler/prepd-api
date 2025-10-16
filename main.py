from fastapi import FastAPI
from routes import auth

app = FastAPI(title="Prepd", version="0.1.0")

# register routers
app.include_router(auth.router)

# Define your first API endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}