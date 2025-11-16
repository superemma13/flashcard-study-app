"""
Vercel serverless function wrapper for FastAPI
"""
from fastapi import FastAPI
from app.main import app as fastapi_app

# Export the FastAPI app for Vercel
app = fastapi_app
