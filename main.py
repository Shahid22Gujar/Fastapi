
from ssl import MemoryBIO
from fastapi import FastAPI,Depends,HTTPException
from sqlmodel import Session
import database,models_and_schemas
from fastapi.security import OAuth2PasswordRequestForm
import crud
import auth
from fastapi.responses import HTMLResponse

app=FastAPI()

@app.on_event("startup")
def startup_event():
    database.create_db_and_tables()

# @app.on_event("shutdown")
# def shutdown_event():
#     database.shutdown()

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
    print(user,">>>>>>>>s")
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
    print(movie,">>>>>>>>s")
    # db_user=crud.create_user(db=db,user=user)
    db_movie=crud.create_movies(db=db,movie=movie)
   
    return db_movie

@app.get("/movies",tags=["Movies"])
def get_all_movies(db:Session=Depends(database.get_db),active: bool = Depends(auth.check_active)):
    movies=crud.get_movies(db=db)
    return movies

@app.patch("/movies/{id}",tags=["Movies"])
def update_movie(id:int,movie:models_and_schemas.MovieSchema,db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    db_movie=crud.update_movie(db=db,movie=movie,id=id)
    return db_movie
    

"""Delete Movie"""    
@app.get("/movies/{id}",tags=["Movies"])
def delete_movie(id:int,db:Session=Depends(database.get_db),active: bool = Depends(auth.check_admin)):
    movie=crud.delete_movie(db=db,id=id)
    
    return movie
   