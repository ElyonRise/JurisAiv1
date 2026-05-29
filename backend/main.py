```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jurisai-rho.vercel.app",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROOT
@app.get("/")
async def root():
    return {
        "status": "online"
    }

# LOGIN
@app.post("/login")
async def login(data: dict):
    return {
        "message": "login ok",
        "data": data
    }

# REGISTER
@app.post("/register")
async def register(data: dict):
    return {
        "message": "register ok",
        "data": data
    }

# RESET
@app.post("/forgot-password")
async def forgot_password(data: dict):
    return {
        "message": "reset ok",
        "data": data
    }
```
