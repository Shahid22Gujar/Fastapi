
from fastapi import FastAPI,Depends,HTTPException,status
from sqlmodel import Session
import database,models_and_schemas
from fastapi.security import OAuth2PasswordRequestForm
import crud
import auth
from fastapi.responses import HTMLResponse
import json
from sqlalchemy.orm import sessionmaker

app=FastAPI()

@app.on_event("startup")
def startup_event():
    database.create_db_and_tables()
"""Below commented function delete db on closing server"""
# @app.on_event("shutdown")
# def shutdown_event():
#     database.shutdown()


"""Function to load json file to db"""
def load_json_to_db():
    Session=sessionmaker()
    db=Session(bind=database.engine) # bind engine with session
    print(db)
    with open("imdb.json") as file:
        
        data_list=json.load(file)
        for data in data_list:
            # crud.create_movies_from_json(db=db,movie=data)
            genre=json.dumps(data.get('genre'))
            print(genre)
            db_movie=models_and_schemas.Movies(
                popularity=data.get('99popularity'),
                director=data.get('director'),
                genre=genre,
                imdb_score=data.get('imdb_score'),
                name=data.get('name')
            )
            db.add(db_movie)
            # db.query(models_and_schemas.Movies).delete()
            db.commit()
            
            

"""Calling function to load json"""
# load_json_to_db()


@app.post('/login',tags=["Users"])
def login(db:Session = Depends(database.get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user_by_username(db=db,username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=401,detail="Not found")
    
    if auth.verify_password(form_data.password,db_user.hashed_password):
        token=auth.create_access_token(db_user)
        return {"access_token":token,"token_type":"Bearer"}

    return db_user

@app.post("/register",tags=["Users"])
def register_user(user:models_and_schemas.UserSchema,db:Session=Depends(database.get_db)):
   
    db_user = crud.get_user_by_username(db=db,username=user.username)
    if db_user:
        raise HTTPException(status_code=404,detail=f"Account already exists with this username = {user.username}")
  

    db_user=crud.create_user(db=db,user=user)
   
    return db_user

# @app.get("/user")
# def get_all_users(db:Session=Depends(database.get_db),token: str = Depends(auth.oauth2_scheme)):
#     users=crud.get_user(db=db)
#     return users
@app.get("/user",tags=["Users"])
def get_all_users(db:Session=Depends(database.get_db),active: bool = Depends(auth.check_active)):
    users=crud.get_user(db=db)
    return users

@app.get("/adminsonly",tags=["Users"])
def get_all_users(db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    users=crud.get_user(db=db)
    return users
@app.get("/another_way_adminsonly",dependencies=[Depends(auth.check_admin)],tags=["Users"])
def get_all_users(db:Session=Depends(database.get_db)):
    users=crud.get_user(db=db)
    return users

@app.get("/verify/{token}",response_class=HTMLResponse,tags=["Users"])
def verify_user(token: str,db:Session = Depends(database.get_db)):
    claims=auth.decode_token(token)
    username=claims.get("sub")
    db_user=crud.get_user_by_username(db,username)
    db_user.is_active=True
    db.commit()
    db.refresh(db_user)
    return f"""
    <p>Account activated</p>
    """
"""Movies"""
@app.post("/movies",tags=["Movies"])
def add_movies(movie:models_and_schemas.MovieSchema,db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    db_movie=crud.create_movies(db=db,movie=movie)
    return db_movie

@app.get("/movies",tags=["Movies"])
def get_all_movies(db:Session=Depends(database.get_db),active: bool = Depends(auth.check_active)):
    movies=crud.get_movies(db=db)
    return movies

@app.patch("/movies/{id}",tags=["Movies"])
def update_movie(id:int,movie:models_and_schemas.MovieSchema,db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    db_movie=crud.update_movie(db=db,movie=movie,id=id)
    if db_movie==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return db_movie
    

"""Delete Movie"""    
@app.get("/movies/{id}",tags=["Movies"])
def delete_movie(id:int,db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    db_movie=crud.get_movie_by_id(db=db,id=id)
    if not db_movie:
        raise HTTPException(status_code=404,detail="Try again")
    db_movie.delete()
    return movie
   