#!/usr/bin/env python3
"""
Script to generate a secure SECRET_KEY for Django
"""

import secrets
import string

def generate_secret_key():
    """Generates a secure SECRET_KEY for Django"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(chars) for _ in range(50))

if __name__ == '__main__':
    secret_key = generate_secret_key()
    print("Your new secure SECRET_KEY:")
    print(f"SECRET_KEY={secret_key}")
    print("\nCopy this key and:")
    print("1. Paste it in the .env file for local development")
    print("2. Configure it in Render.com environment variables")