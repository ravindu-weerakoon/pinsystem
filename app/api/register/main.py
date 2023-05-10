# import asyncio
# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash
# from app.dbcon import db
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# # from flasgger import swag_from
# from app.models import User
# from app.api.register.schema import RegistrationSchema

# register_bp = Blueprint('register', __name__, url_prefix='/api/register')


# def get_user(username):
#     user = User.query.filter_by(username=username).first()
#     return user


# @register_bp.route('', methods=['POST'])
# async def register():
#     try:
#         # Parse request body
#         data = request.get_json()
#         email = data.get('email')
#         username = data.get('username')
#         password = data.get('password')
#         fullname = data.get('fullname')

#         # Check if request body is empty
#         if not data:
#             return jsonify({'error': 'Request body is empty'}), 400

#         # Check if email, username, and password are provided and valid
#         errors = RegistrationSchema().validate(data)
#         if errors:
#             return jsonify({'error': errors}), 400

#         # Check if email and username are already taken
#         async with AsyncSession(db.engine, expire_on_commit=False) as session:
#             if (await session.execute(select(User).where(User.email == email))).scalar():
#                 return jsonify({'error': 'Email is already taken'}), 400
#             if (await session.execute(select(User).where(User.username == username))).scalar():
#                 return jsonify({'error': 'Username is already taken'}), 400

#             # Create new user and save to database
#             hashed_password = generate_password_hash(password, method='sha256')
#             new_user = User(email=email, username=username,
#                             password=hashed_password, fullname=fullname)
#             session.add(new_user)
#             await session.commit()

#         # Return success response
#         response_data = {
#             'id': new_user.id,
#             'username': new_user.username,
#             'email': new_user.email,
#             'fullname': new_user.fullname
#         }
#         return jsonify({'message': 'User successfully registered', 'data': response_data}), 201

#     except Exception as e:
#         # Return error response
#         return jsonify({'error': str(e)}), 500

from datetime import datetime
import aiomysql
import asyncio
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from app.models import User
from app.api.register.schema import RegistrationSchema
from flask import Flask, jsonify
from ...dbcon import create_pool
from sqlalchemy import select
import traceback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


register_bp = Blueprint('register', __name__, url_prefix='/api/register')


# loop = asyncio.get_event_loop()

# db = asyncio.run(connect_to_db(current_app))

# print(type(db))


# loop = asyncio.get_event_loop()


@register_bp.route('', methods=['POST'])
async def register():

    try:
        # db_user = os.environ.get('MYSQL_USER')
        # db_password = os.environ.get('MYSQL_PASSWORD')
        # db_host = os.environ.get('MYSQL_HOST', 'localhost')
        # db_port = os.environ.get('MYSQL_PORT', '3306')
        # db_name = os.environ.get('MYSQL_DATABASE')

        

        # Parse request body
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        fullname = data.get('fullname')

        # Check if request body is empty
        if not data:
            return jsonify({'error': 'Request body is empty'}), 400

        # Check if email, username, and password are provided and valid
        errors = RegistrationSchema().validate(data)
        if errors:
            return jsonify({'error': errors}), 400

        # Check if email and username are already taken
        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT username, email FROM user WHERE email = %s;", (email))
            email_present = await cur.fetchone()
            if email_present:
                return jsonify({'error': 'Email is already taken'}), 400
            await cur.execute("SELECT username, email FROM user WHERE username = %s;", (username))
            user = await cur.fetchone()
            if user:
                return jsonify({'error': 'Username is already taken'}), 400

            hashed_password = generate_password_hash(password, method='sha256')

            await cur.execute("INSERT INTO user (email, username, password, fullname,date_joined) VALUES (%s, %s, %s, %s,%s);", (email, username, hashed_password, fullname, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            await conn.commit()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        # Return success response
        response_data = {
            'username': username,
            'email': email,
            'fullname': fullname
        }
        return jsonify({'message': 'User successfully registered', 'data': response_data}), 201

    except Exception as e:
        # Return error response
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# loop.run_until_complete(register())
