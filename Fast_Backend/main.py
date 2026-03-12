from fastapi import FastAPI,Depends,HTTPException
from routes.todoRoute import router as todo_router
from routes.signin import router as signin_router
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from models.notifications import Notification
import time
from datetime import datetime

app = FastAPI(title='TODO App')

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "https://clockwork-todoapp.vercel.app"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(todo_router)
# app.include_router(signin_router)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https://.*vercel.app",
    allow_credentials=False,  # disable for wildcard or multiple domains
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(todo_router, prefix="/app/v1")
app.include_router(signin_router, prefix="/app/v1")

@app.on_event("startup")
def startup_event():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)

@app.get('/',tags=['Main'])
def read_root():
    return {'message': 'Welcome to the TODO App'}
