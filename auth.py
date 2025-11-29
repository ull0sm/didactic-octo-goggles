"""
Authentication utilities for Google OAuth
"""
import os
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def verify_google_token(token):
    """
    Verify Google OAuth token
    Returns user info if valid, None otherwise
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', idinfo['email'].split('@')[0])
        }
    except ValueError as e:
        print(f"Token verification failed: {e}")
        return None


def get_or_create_coach(db, user_info):
    """
    Get existing coach or create new one
    """
    from database import Coach
    
    coach = db.query(Coach).filter(Coach.email == user_info['email']).first()
    
    if not coach:
        coach = Coach(
            email=user_info['email'],
            name=user_info['name'],
            google_id=user_info['google_id']
        )
        db.add(coach)
        db.commit()
        db.refresh(coach)
    
    return coach
