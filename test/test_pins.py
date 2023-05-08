import json
import pytest
import os
from datetime import timedelta
from time import sleep
import sys
from flask_jwt_extended import  decode_token, create_access_token
from jwt import encode
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


def test_create_pin_with_valid_data(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Create a pin using the access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'pin' in response.json
    assert 'title' in response.json['pin']
    assert 'body' in response.json['pin']
    assert 'image' in response.json['pin']
    assert 'user_id' in response.json['pin']
    assert 'date_posted' in response.json['pin']
    assert 'updated_date' in response.json['pin']

def test_create_pin_with_invalid_access_token(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Try to create a pin with an invalid access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}invalid"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Invalid token Passed'

def test_create_pin_with_expired_access_token(test_client):
    # First, log in to get an access token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Simulate an expired access token by changing its expiration date to the past
    decoded_token = decode_token(access_token)
    expired_token = create_access_token(
                identity=decoded_token['sub'], expires_delta=timedelta(seconds=1))
    
    sleep(2.0)

    # Try to create a pin with the expired access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {expired_token}"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Access token expired, new token generated'

def test_create_pin_with_empty_request(test_client):
    #First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Try to create a pin with an empty request
    pin_data = {}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json
    
    assert response.json['error'] == 'Request body is empty'

def test_create_pin_with_missing_title(test_client):
    #First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    pin_data = {"body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error']['title'][0] == 'Missing data for required field.'

def test_create_pin_with_missing_body(test_client):
    #First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    pin_data = {"title": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.post('/api/pins', json=pin_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json
    assert response.json['error']['body'][0] == 'Missing data for required field.'


def test_update_pin_with_valid_data(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # update a pin using the access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.put('/api/pins/pins/6', json=pin_data, headers=headers)
    assert response.status_code == 200
    assert 'Pin updated successfully' in response.json['message']
    assert 'pin' in response.json
    assert 'title' in response.json['pin']
    assert 'body' in response.json['pin']
    assert 'image' in response.json['pin']
    assert 'user_id' in response.json['pin']
    assert 'date_posted' in response.json['pin']
    assert 'updated_date' in response.json['pin']

def test_update_pin_with_invalid_access_token(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Try to update a pin with an invalid access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}invalid"}
    response = test_client.put('/api/pins/pins/6', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Invalid token Passed'

def test_update_pin_with_expired_access_token(test_client):
    # First, log in to get an access token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Simulate an expired access token by changing its expiration date to the past
    decoded_token = decode_token(access_token)
    expired_token = create_access_token(
                identity=decoded_token['sub'], expires_delta=timedelta(seconds=1))
    
    sleep(2.0)

    # Try to update a pin with the expired access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {expired_token}"}
    response = test_client.put('/api/pins/pins/6', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Access token expired, new token generated'

def test_update_pin_with_empty_request(test_client):
    #First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Try to update a pin with an empty request
    pin_data = {}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.put('/api/pins/pins/6', json=pin_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json
    
    assert response.json['error'] == 'Request body is empty'


def test_update_pin_with_another_users_access_token(test_client):
    # First, log in to get an access token and refresh token with diffrent user
    user_data = {"username": "testusernew1",
        "password": "testpassword",}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Try to update a pin with another users access token
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.put('/api/pins/pins/6', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'You are not authorized to update this pin'

def test_update_pin_with_invalid_pin_id(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Try to update a pin with an invalid pin id
    pin_data = {"title": "Test pin", "body": "This is a test pin", "image": "https://example.com/image.jpg"}

    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.put('/api/pins/pins/100', json=pin_data, headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Pin does not Exist' 

def test_delete_pin_with_valid_data(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.delete('/api/pins/pins/17', headers=headers)
    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == 'Pin deleted successfully'

def test_delete_pin_with_another_users_access_token(test_client):
    # First, log in to get an access token and refresh token with diffrent user
    user_data = {"username": "testusernew1",
        "password": "testpassword",}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Try to delete a pin with another users access token
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.delete('/api/pins/pins/10', headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'You are not authorized to delete this pin'

def test_delete_pin_with_invalid_pin_id(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}"}
    response = test_client.delete('/api/pins/pins/180', headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Pin does not Exist'

def test_delete_pin_with_expired_access_token(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    #Simulate an expired access token by changing its expiration date to the past
    decoded_token = decode_token(access_token)
    expired_token = create_access_token(
                identity=decoded_token['sub'], expires_delta=timedelta(seconds=1))
    
    sleep(2.0)
    # Try to delete a pin with an expired access token
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {expired_token}"}
    response = test_client.delete('/api/pins/pins/15', headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Access token expired, new token generated'

def test_delete_pin_with_invalid_token(test_client):
    # First, log in to get an access token and refresh token
    user_data = {"username": "ravindu112", "password": "test1234"}
    response = test_client.post('/api/authenticate', json=user_data)
    assert response.status_code == 200
    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']
    # Try to delete a pin with an invalid access token
    headers = {"Authorization": f"Bearer {refresh_token}", "AccessToken": f"Bearer {access_token}invalid"}
    response = test_client.delete('/api/pins/pins/16', headers=headers)
    assert response.status_code == 401
    assert 'error' in response.json
    assert response.json['error'] == 'Invalid token Passed'


def test_get_all_pins(test_client):
    filter_data = {}
    response = test_client.get('/api/pins',json=filter_data)
    assert response.status_code == 200
    assert isinstance(response.json['pins'], list)
    assert 'pins' in response.json

def test_get_all_pins_for_user(test_client):
    filter_data ={ "user_id":3}
    response = test_client.get('/api/pins',json=filter_data)
    assert response.status_code == 200
    assert isinstance(response.json['pins'], list)
    assert 'pins' in response.json
    allvalid = True
    if len(response.json['pins'])>0:
        for pin in response.json['pins']:
            if  pin['user_id'] != filter_data['user_id']:
                allvalid = False
    assert allvalid == True


def test_get_all_pins_by_order(test_client):
    filter_data = {"order":"True"}
    response = test_client.get('/api/pins',json=filter_data)
    assert response.status_code == 200
    assert isinstance(response.json['pins'], list)
    assert 'pins' in response.json
    if len(response.json['pins'])>0:
        # sort the pins list based on the date_posted key in descending order
        sorted_pins = sorted(response.json['pins'], key=lambda pin: pin['date_posted'], reverse=True)
        # compare the sorted pins list with the list of pins returned in the response
        assert sorted_pins == response.json['pins']

def test_get_all_pins_orderd_and_by_user(test_client):
    filter_data = {"order":"True",
                    "user_id":3}
    response = test_client.get('/api/pins',json=filter_data)
    assert response.status_code == 200
    assert 'pins' in response.json
    assert isinstance(response.json['pins'], list)
    allvalid_user = True
    if len(response.json['pins'])>0:
        for pin in response.json['pins']:
            if  pin['user_id'] != filter_data['user_id']:
                allvalid_user = False
        # sort the pins list based on the date_posted key in descending order
        sorted_pins = sorted(response.json['pins'], key=lambda pin: pin['date_posted'], reverse=True)
        # compare the sorted pins list with the list of pins returned in the response
        assert sorted_pins == response.json['pins']

    assert allvalid_user == True


def test_get_single_pin(test_client):
    response = test_client.get('api/pins?pin_id=3')
    assert response.status_code == 200
    assert isinstance(response.json['pins'][0], dict)
    assert response.json['pins'][0]['pin_id'] == 3