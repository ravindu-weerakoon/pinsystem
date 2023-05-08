import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, decode_token, create_access_token
from .schema import PinSchema, UpdatePinsSchema
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from ...dbcon import create_pool

pins_bp = Blueprint('pins', __name__, url_prefix='/api/pins')

pins_bp1 = Blueprint('pins1', __name__, url_prefix='/api/pins1')


@pins_bp1.route('', methods=['POST'])
@jwt_required(refresh=True)
async def create_pin1():

    # Get the access token and refresh token from the Header
    refresh_token = request.headers.get('Authorization').split()[1]
    access_token = request.headers.get('AccessToken').split()[1]
    if '\"' in access_token:
        access_token = access_token.replace('\"', '')
    decode_token_access = decode_token(access_token)
    decode_token_refresh = decode_token(refresh_token)
    # Create the response with the access token and refresh token
    response = jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'decode_token_access': decode_token_access,
        'decode_token_refresh': decode_token_refresh
    })
    return response


async def decode_access_tokens(access_token, refresh_token):
    decode_access_token_id = ''
    if '\"' in access_token:
        access_token = access_token.replace('\"', '')
    try:
        decode_access_token_id = decode_token(access_token)['sub']

    except ExpiredSignatureError:
        # If access token is expired, try to refresh it
        try:
            refresh_token = request.headers.get('Authorization').split()[1]
            decode_refresh_token_user = decode_token(refresh_token)['sub']
            new_token = create_access_token(
                identity=decode_refresh_token_user)
            decode_access_token_id = decode_token(new_token)['sub']
            response = jsonify(
                {'error': 'Access token expired, new token generated', 'access_token': new_token}), 401
            return response

        except Exception as e:
            return jsonify({'error is': str(e)}), 500

    except InvalidTokenError:
        return jsonify({'error': 'Invalid token Passed'}), 401

    return decode_access_token_id


@pins_bp.route('', methods=['POST'])
@jwt_required(refresh=True)
async def create_pin():
    try:
        # parse request body
        data = request.get_json()
        title = data.get('title')
        body = data.get('body')
        image = data.get('image')
        date_posted = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # check if the access token is expired if it is then refresh it using the refresh token endpoint and then try again
        # if the refresh token is expired then return an error message
        # if the refresh token is valid then return a new access token and refresh token
        # if the access token is valid then continue with the request

        # Get the access token and refresh token from the Header
        refresh_token = request.headers.get('Authorization').split()[1]
        access_token = request.headers.get('AccessToken').split()[1]

        if '\"' in access_token:
            access_token = access_token.replace('\"', '')
        try:
            decode_access_token_id = decode_token(access_token)['sub']

        except ExpiredSignatureError:
            # If access token is expired, try to refresh it
            try:
                refresh_token = request.headers.get('Authorization').split()[1]
                decode_refresh_token_user = decode_token(refresh_token)['sub']
                new_token = create_access_token(
                    identity=decode_refresh_token_user)
                decode_access_token_id = decode_token(new_token)['sub']
                response = jsonify(
                    {'error': 'Access token expired, new token generated', 'access_token': new_token}), 401
                return response

            except Exception as e:
                return jsonify({'error is': str(e)}), 500

        except InvalidTokenError:
            return jsonify({'error': 'Invalid token Passed'}), 401

        # check if request body is empty
        if not data:
            return jsonify({'error': 'Request body is empty'}), 400

        # validate request body
        errors = PinSchema().validate(data)
        if errors:
            return jsonify({'error': errors}), 400

        pool = await create_pool()

        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT * FROM user WHERE id = %s", (str(decode_access_token_id,)))
            user_id = await cur.fetchone()
            if not user_id:
                return jsonify({'error': 'User does not Exist'}), 401

            await cur.execute("INSERT INTO pins (title, body, image, user_id, date_posted, updated_date) VALUES (%s, %s, %s, %s, %s, %s)", (title, body, image, decode_access_token_id, date_posted, updated_date))
            await conn.commit()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        # return response
        response = jsonify({
            'message': 'Pin created successfully',
            'pin': {
                # 'pin_id': new_pin.pin_id,
                'title': title,
                'body': body,
                'image': image,
                'user_id': decode_access_token_id,
                'date_posted': date_posted,
                'updated_date': updated_date
            }
        })
        response.status_code = 201
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pins_bp.route('pins/<int:pin_id>', methods=['PUT'])
@jwt_required(refresh=True)
async def update_pin(pin_id):
    try:
        updated_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Get the access token and refresh token from the Header
        refresh_token = request.headers.get('Authorization').split()[1]
        access_token = request.headers.get('AccessToken').split()[1]

        if '\"' in access_token:
            access_token = access_token.replace('\"', '')
        try:
            decode_access_token_id = decode_token(access_token)['sub']

        except ExpiredSignatureError:
            # If access token is expired, try to refresh it
            try:
                refresh_token = request.headers.get('Authorization').split()[1]
                decode_refresh_token_user = decode_token(refresh_token)['sub']
                new_token = create_access_token(
                    identity=decode_refresh_token_user)
                decode_access_token_id = decode_token(new_token)['sub']
                response = jsonify(
                    {'error': 'Access token expired, new token generated', 'access_token': new_token}), 401
                return response

            except Exception as e:
                return jsonify({'error is': str(e)}), 500

        except InvalidTokenError:
            return jsonify({'error': 'Invalid token Passed'}), 401

        # check if request body is empty
        if not request.json:
            return jsonify({'error': 'Request body is empty'}), 400
        # validate request body
        errors = UpdatePinsSchema().validate(request.json)
        if errors:
            return jsonify({'error': errors}), 400

        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT user_id FROM pins WHERE pin_id = %s", (pin_id,))
            pin_id_return = await cur.fetchone()
            if not pin_id_return:
                return jsonify({'error': 'Pin does not Exist'}), 401

            # Get the user_id of the pin
            user_id_cur = pin_id_return[0]

            await cur.execute("SELECT * FROM user WHERE id = %s", (str(decode_access_token_id)))
            user_id = await cur.fetchone()

            if not user_id:
                return jsonify({'error': 'User does not Exist'}), 401

            if user_id_cur != decode_access_token_id:
                return jsonify({'error': 'You are not authorized to update this pin'}), 401

            # update only the fields that are in the request body
            update_query = "UPDATE pins SET "

            if 'title' in request.json and request.json['title']:
                update_query += f"title = '{request.json['title']}', "

            if 'body' in request.json and request.json['body']:
                update_query += f"body = '{request.json['body']}', "

            if 'image' in request.json and request.json['image']:
                update_query += f"image = '{request.json['image']}', "

            if update_query == "UPDATE pins SET ":
                return jsonify({'error': 'No fields to update'}), 400

            # remove the last comma and space from the query
            update_query = update_query[:-2]

            # append the condition to update only the pin with the given ID
            update_query += f",updated_date = '{updated_date}' WHERE pin_id = '{str(pin_id)}';"

            await cur.execute(update_query)
            await conn.commit()

            # get the updated pin
            await cur.execute("SELECT * FROM pins WHERE pin_id = %s", (pin_id,))
            pin_just_updated = await cur.fetchone()

            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        # return response
        response = jsonify({
            'message': 'Pin updated successfully',
            'pin': {
                'pin_id': pin_just_updated[0],
                'title': pin_just_updated[1],
                'body': pin_just_updated[2],
                'image': pin_just_updated[3],
                'user_id': pin_just_updated[6],
                'date_posted': pin_just_updated[4],
                'updated_date': pin_just_updated[5]
            }
        })
        response.status_code = 200
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pins_bp.route('<int:pin_id>', methods=['DELETE'])
@jwt_required(refresh=True)
async def delete_pin(pin_id):
    try:
        # Get the access token and refresh token from the Header
        refresh_token = request.headers.get('Authorization').split()[1]
        access_token = request.headers.get('AccessToken').split()[1]

        if '\"' in access_token:
            access_token = access_token.replace('\"', '')
        try:
            decode_access_token_id = decode_token(access_token)['sub']

        except ExpiredSignatureError:
            # If access token is expired, try to refresh it
            try:
                refresh_token = request.headers.get('Authorization').split()[1]
                decode_refresh_token_user = decode_token(refresh_token)['sub']
                new_token = create_access_token(
                    identity=decode_refresh_token_user)
                decode_access_token_id = decode_token(new_token)['sub']
                response = jsonify(
                    {'error': 'Access token expired, new token generated', 'access_token': new_token}), 401
                return response

            except Exception as e:
                return jsonify({'error is': str(e)}), 500

        except InvalidTokenError:
            return jsonify({'error': 'Invalid token Passed'}), 401

        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT user_id FROM pins WHERE pin_id = %s", (pin_id,))
            pin_id_return = await cur.fetchone()
            if not pin_id_return:
                return jsonify({'error': 'Pin does not Exist'}), 401

            # Get the user_id of the pin
            user_id_cur = pin_id_return[0]
            if user_id_cur != decode_access_token_id:
                return jsonify({'error': 'You are not authorized to delete this pin'}), 401

            # Delete the pin
            await cur.execute("DELETE FROM pins WHERE pin_id = %s", (pin_id,))
            await conn.commit()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        # return response
        response = jsonify({'message': 'Pin deleted successfully'})
        response.status_code = 200
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pins_bp.route('<pin_id>', methods=['GET'])
async def get_pins():
    try:
        if 'pin_id' in request.args and request.args['pin_id']:
            # Retrieve a single pin by pin_id
            sql_query = f"SELECT * FROM pins WHERE pin_id = '{str(request.args['pin_id'])}'"
        else:
            # Retrieve all pins
            sql_query = "SELECT * FROM pins ORDER BY date_posted ASC"

            if 'user_id' in request.json and request.json['user_id']:
                sql_query = f"SELECT * FROM pins WHERE user_id = '{str(request.json['user_id'])}'"

            if 'order' in request.json and request.json['order']:
                sql_query = f" SELECT * FROM pins ORDER BY date_posted DESC"

            if 'user_id' in request.json and request.json['user_id'] and 'order' in request.json and request.json['order']:
                sql_query = f"SELECT * FROM pins WHERE user_id = '{str(request.json['user_id'])}' ORDER BY date_posted DESC"

        pool = await create_pool()
        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute(sql_query)
            pins = await cur.fetchall()
            await cur.close()
            conn.close()

        pool.close()
        await pool.wait_closed()

        result = []
        for record in pins:
            # Create a dictionary for each record
            record_dict = {
                "pin_id": record[0],
                "title": record[1],
                "body": record[2],
                "image_url": record[3],
                "date_posted": record[4].strftime('%Y-%m-%d %H:%M:%S'),
                "date_updated": record[5].strftime('%Y-%m-%d %H:%M:%S'),
                "user_id": record[6]
            }
            result.append(record_dict)
        # # paginate results
        # page = request.args.get('page', 1, type=int)
        # per_page = request.args.get('per_page', 10, type=int)
        # pins_paginated = pins_query.paginate(page=page, per_page=per_page)

        # prepare response
        # pins = []
        # for pin in pins.items:
        #     pins.append({
        #         'pin_id': pin.pin_id,
        #         'title': pin.title,
        #         'body': pin.body,
        #         'image': pin.image,
        #         'user_id': pin.user_id,
        #         'date_posted': pin.date_posted,
        #         'updated_date': pin.updated_date
        #     })
        response = {
            'pins': result, }

        # return response
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
