

import json
import pytest
import os
import sys
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


def test_register(test_client):
    # Create test user data
    user_data = {
        "email": "testusernew1@example.com",
        "username": "testusernew1",
        "password": "testpassword",
        "fullname": "Test User"
    }

    # Make a request to the register endpoint with the test user data
    response = test_client.post('/api/register', json=user_data)

    # Assert that the response status code is 201 (created)
    assert response.status_code == 201

    # Assert that the response data contains the correct message
    assert response.json['message'] == 'User successfully registered'

    # Assert that the response data contains the correct user data
    assert response.json['data']['email'] == user_data['email']
    assert response.json['data']['username'] == user_data['username']
    assert response.json['data']['fullname'] == user_data['fullname']

    #check again with the same user data
    response = test_client.post('/api/register', json=user_data)
    assert response.status_code == 400
    assert response.json['error'] == 'Email is already taken'

    #check again with the same username
    user_data['email'] = 'newemailtesting@gmail.com'
    response = test_client.post('/api/register', json=user_data)
    assert response.status_code == 400
    assert response.json['error'] == 'Username is already taken'

def test_register_empty_request_body(test_client):
    response = test_client.post('/api/register', json={})
    assert response.status_code == 400
    assert response.json['error'] == 'Request body is empty'


def test_register_invalid_data(test_client):
    data = {
        'email': 'testemail@gmail',
        'username': '',
        'password': 'short',
        'fullname': ''
    }
    
    response = test_client.post('/api/register', json=data)
    assert response.status_code == 400

    assert response.json['error']['email'] == ['Not a valid email address.']
    assert response.json['error']['username'] == [ "Shorter than minimum length 1."]
    assert response.json['error']['password'] == ['Shorter than minimum length 8.']
    assert response.json['error']['fullname'] == ['Shorter than minimum length 1.']