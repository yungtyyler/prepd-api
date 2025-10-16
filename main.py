from fastapi import FastAPI

app = FastAPI(title="Prepd", version="0.1.0")

# register routers
# app.include_router(recipes.router)

# Define your first API endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}