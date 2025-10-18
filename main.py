from fastapi import FastAPI
from routers import auth, recipes

app = FastAPI(title="Prepd", version="0.1.0")

# register routers
app.include_router(auth.router)
app.include_router(recipes.router)

# Define your first API endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}