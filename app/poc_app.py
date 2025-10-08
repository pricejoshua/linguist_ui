import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

fastapi_app = FastAPI()

NGROK_URL = os.getenv("NGROK_URL", "http://localhost:5017")

# Configure CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.ngrok.io",
        "https://*.ngrok-free.app",
        "http://localhost:5017",
        NGROK_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/status")
def status():
    return {"message": "FastAPI app running"}

# Import and include the linguist router
from linguist.routes import router as linguist_router
fastapi_app.include_router(linguist_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.getenv('LOCAL_PORT', 5017)), log_level="info")
