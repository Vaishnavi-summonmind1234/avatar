from fastapi import FastAPI
from route.created_avatar_route import router

test = FastAPI()

@test.get("/")
def health_check():
    return {"status": "API is running 🚀"}
test.include_router(router)



