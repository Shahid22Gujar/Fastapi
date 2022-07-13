from os import access
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

register_user_data={
  "email": "test@example.com",
  "username": "admin",
  "is_active": True,
  "role": "admin",
  "password": "shahid"
}
login_user_data={
  "username": "gujar",
  "password": "shahid"
}
login_user_admin_data={
  "username": "admin",
  "password": "admin"
}

movie_data={
  "popularity": 12,
  "director": "shahid",
  "genre": [
    "string","string1"
  ],
  "imdb_score": 23,
  "name": "Hm Tumhare hosake sanam"
}


def test_register_user():
    response=client.post("/register",json=login_user_admin_data)
    assert response.status_code == 201
    assert response.json() == register_user_data
def get_access_token() -> str:
  response=client.post("/test-login",json=login_user_admin_data)
  access_token=response.json().get('access_token')
  return access_token

def test_login_user():
    response=client.post("/test-login",json=login_user_data)
    access_token=response.json().get('access_token')
    print(access_token,"Access Token >>>>")  
    assert response.status_code == 200

def test_create_movie():


  access_token=get_access_token()
  response=client.post("/movies",json=movie_data,headers={"Authorization":f"Bearer {access_token}"})
  assert response.status_code == 201
  assert response.json() == movie_data

