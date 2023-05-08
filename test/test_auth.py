import json
import pytest
import os
import sys
from flask_jwt_extended import decode_token, create_refresh_token
from datetime import  timedelta
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

def test_login_with_valid_credentials(test_client):
        # Test login with valid credentials
        user_data = {"username": "ravindu112",
                      "password": "test1234"}
        response = test_client.post('/api/authenticate', json= user_data)
        
        assert response.status_code == 200
        assert 'message' in response.json
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'access_token_expire_date' in response.json
        assert 'refresh_token_expire_date' in response.json
        assert response.json['message'] == 'Login successful'


def test_login_with_invalid_credentials(test_client):
        # Test login with invalid credentials
        user_data = {"username": "ravindu112",
                      "password": "test12345"}
        response = test_client.post('/api/authenticate', json= user_data)
        
        assert response.status_code == 401
        assert 'error' in response.json
        assert response.json['error'] == 'Invalid username or password'

def test_login_with_empty_request_body(test_client):
        # Test login with empty request body
        response = test_client.post('/api/authenticate', json= {})
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert response.json['error'] == 'Request body is empty'


def test_refresh_token(test_client):
    # First, get an access and refresh token for a user
    user_data = {"username": "ravindu112", "password": "test1234"}
    login_response = test_client.post('/api/authenticate', json=user_data)
    assert login_response.status_code == 200

    refresh_token = login_response.json['refresh_token']
    # Test refresh token with valid refresh token
    header = {"Authorization": "Bearer " +  refresh_token}
    refresh_response = test_client.post('/api/refreshtoken', headers=header)

    assert refresh_response.status_code == 200
    assert 'access_token' in refresh_response.json
    assert 'refresh_token' in refresh_response.json
    assert 'access_token_expire_date' in refresh_response.json
    assert 'refresh_token_expire_date' in refresh_response.json

    # Test refresh token with invalid refresh token
    header = {"Authorization": "Bearer " +  refresh_token + 'invalid'}
    invalid_refresh_response = test_client.post('/api/refreshtoken',headers = header)
    assert invalid_refresh_response.status_code == 422
    assert 'msg' in invalid_refresh_response.json
    assert invalid_refresh_response.json['msg'] == 'Signature verification failed'

    #Test refresh token with empty authozation header
    empty_refresh_response = test_client.post('/api/refreshtoken')
    assert empty_refresh_response.status_code == 401
    assert 'msg' in empty_refresh_response.json
    assert empty_refresh_response.json['msg'] == 'Missing Authorization Header'

    #Test refresh token with expired authozation header
    
    # Simulate an expired refresh token by changing its expiration date to the past
    decoded_token = decode_token(refresh_token)
    expired_token = create_refresh_token(
                identity=decoded_token['sub'], expires_delta=timedelta(seconds=1))
    
    sleep(2)
    header = {"Authorization": "Bearer " +  expired_token}
    expired_refresh_response = test_client.post('/api/refreshtoken',headers = header)
    assert expired_refresh_response.status_code == 401
    assert 'msg' in expired_refresh_response.json
    assert expired_refresh_response.json['msg'] == 'Token has expired'
