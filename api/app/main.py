from fastapi import FastAPI
from .routers import configuration


app = FastAPI()

# Include routers
app.include_router(configuration.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
