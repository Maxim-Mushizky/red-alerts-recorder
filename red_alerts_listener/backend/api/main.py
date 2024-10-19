from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from red_alerts_listener.backend.api.auth import (
    Token,
    Depends,
    fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token
)
from red_alerts_listener.backend.api.routes import poll_alerts

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(poll_alerts.router, prefix="/api/v1/alerts")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or form_data.password != "secret":  # Replace with proper password checking
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "is_admin": user["is_admin"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def main():
    return {"message": "Hello World"}


# Events
# @app.on_event("startup")
# async def startup_event():
#     await connect_to_mongo()
#
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     await close_mongo_connection()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
