from fastapi import FastAPI

from .routers import create_router

app = FastAPI()

# design router
app.include_router(create_router(database="designs", type="design"))

# applications router
app.include_router(create_router(database="applications", type="application"))


@app.get("/")
async def root():
    return {"message": "Hello World"}
