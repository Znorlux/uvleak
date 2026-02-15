#!/usr/bin/env python3
"""
Genera un token JWT firmado con un secret dado.
Uso: python jwt_forge.py [verify <token>]
"""

import jwt
import sys


JWT_SECRET = 'internlink2024'


def create_token(user_id='1', email='admin@internlink.com', role='admin'):
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        return f"Error: {e}"


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        if len(sys.argv) < 3:
            print("Uso: python jwt_forge.py verify <token>")
            return
        print(verify_token(sys.argv[2]))
    else:
        user_id = input("User ID [1]: ").strip() or '1'
        email = input("Email [admin@internlink.com]: ").strip() or 'admin@internlink.com'
        role = input("Role [admin]: ").strip() or 'admin'

        token = create_token(user_id, email, role)

        print(f"\nPayload: user_id={user_id}, email={email}, role={role}")
        print(f"Token:\n{token}\n")

        print("Verificación:")
        print(verify_token(token))


if __name__ == '__main__':
    main()
