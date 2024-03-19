from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
import json

app = FastAPI()
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_SECRET_KEY"),
    MAIL_FROM = os.getenv("MAIL_USERNAME"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fast_mail = FastMail(conf)

html = """
<ul>
    <li>{name}</li>
    <li>{email}</li>
    <li>{subject}</li>
</ul>
"""

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def hello():
    return {"hello":"world"}

@app.get("/articles")
async def read_articles():
    with open("static/articles.json", "r") as file:
        articles = json.load(file) 
    return articles

@app.post("/send_email/")
async def send_email(name: str = Form(...), email: str = Form(...), subject: str = Form(...)):

    message = MessageSchema(
        subject="Email from portfolio",
        recipients=[os.getenv("MAIL_USERNAME")],
        body=html.format(name=name,email=email,subject=subject),
        subtype=MessageType.html)

    try:
        await fast_mail.send_message(message)
        return {"message": "Email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
