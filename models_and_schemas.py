from sqlmodel import SQLModel,Field
from pydantic import EmailStr
from enum import Enum
from typing import Optional

class Roles(str,Enum):
    user="user"
    admin="admin"

class BaseUser(SQLModel):
    email: EmailStr
    username: str
    is_active: bool
    role: Roles
    
class User(BaseUser,table=True):
    id: Optional[int] =  Field(default=None,primary_key=True)
    hashed_password: str

class BaseMovies(SQLModel):
   
    popularity: int
    director: str
    genre: str
    imdb_score : int
    name : str

class Movies(BaseMovies,table=True):
     id: Optional[int] =  Field(default=None,primary_key=True)

"""User Schema its like serializers of drf"""
class UserSchema(BaseUser):
    password: str

"""User Schema its like serializers of drf"""
class MovieSchema(BaseMovies):
    genre: list