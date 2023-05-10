from app.models import User
from flask import Flask, jsonify, request, Blueprint, current_app
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime, timezone
from .schema import LoginSchema
from ...dbcon import create_pool
import traceback

auth_bp = Blueprint(
    'authenticate', __name__, url_prefix='/api/authenticate')
refresh_token_bp = Blueprint(
    'refreshtoken', __name__, url_prefix='/api/refreshtoken')


@auth_bp.route('', methods=['POST'])
async def login():
    try:
        # Parse request body
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Check if request body is empty
        if not data:
            return jsonify({'error': 'Request body is empty'}), 400

        # validate request body
        errors = LoginSchema().validate(data)
        if errors:
            return jsonify({'error': errors}), 400

        # Check if user exists and password is correct
        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT id,password FROM user WHERE username = %s", (username))
            result = await cur.fetchone()
            if not result:
                return jsonify({'error': 'Invalid username or password'}), 401

            if not check_password_hash(result[1], password):
                return jsonify({'error': 'Invalid username or password'}), 401

            # Generate access and refresh tokens
            user_id = result[0]
            access_token = create_access_token(
                identity=user_id, expires_delta=timedelta(hours=1))
            refresh_token = create_refresh_token(
                identity=user_id, expires_delta=timedelta(days=30))

            # store refresh token in database
            await cur.execute("UPDATE user SET refresh_token = %s WHERE id = %s", (refresh_token, user_id))
            await conn.commit()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        # Return response with tokens and expiration dates
        response = jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expire_date': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'refresh_token_expire_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        })
        response.status_code = 200
        return response

    except Exception as e:
        # Handle any exceptions that occur during the login process
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@refresh_token_bp.route('', methods=['POST'])
@jwt_required(refresh=True)
async def refresh():
    try:
        current_user = get_jwt_identity()
        refresh_token = request.headers.get('Authorization').split()[1]
        decoded_token = decode_token(refresh_token)
        refresh_token_expire_date = datetime.fromtimestamp(
            decoded_token['exp'], timezone.utc)
        now = datetime.now(timezone.utc)

        if refresh_token_expire_date < now:
            raise ExpiredSignatureError('Refresh token has expired')

        # Compare refresh token from database with the one passed in request header
        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT refresh_token FROM user WHERE id = %s", (current_user))
            result = await cur.fetchone()
            if not result:
                return jsonify({'error': 'User Not available in the databse'}), 401

            if result[0] != refresh_token:
                raise InvalidTokenError('Invalid refresh token')

            # Generate new access and refresh tokens
            access_token = create_access_token(
                identity=current_user, expires_delta=timedelta(hours=1))
            refresh_token = create_refresh_token(
                identity=current_user, expires_delta=timedelta(days=30))

            # store refresh token in database
            await cur.execute("UPDATE user SET refresh_token = %s WHERE id = %s", (refresh_token, current_user))
            await conn.commit()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        return jsonify({'access_token': access_token,
                        'access_token_expire_date': (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                        'refresh_token': refresh_token,
                        'refresh_token_expire_date': refresh_token_expire_date.strftime('%Y-%m-%d %H:%M:%S')})

    except Exception as e:
        # Handle any exceptions that occur during the login process
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
