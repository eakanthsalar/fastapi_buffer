from operator import mod
from fastapi import status,HTTPException,Depends,APIRouter
from schemas import Token
from oauth2 import create_access_token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm#only gives username , password
#this method allows us to give input as form data in postman
#we need to give :OAuth2PasswordRequestForm=Depends() as schema for input data packet
import models
from sqlalchemy.orm import Session
from database import get_db
from schemas import User_Login_Schema
from utills import verify_password
from sqlalchemy import func
#pip install "python-jose[cryptography]" for jwt web tokens

router=APIRouter()

@router.post('/users/signin',response_model=Token)
def signin(login_details:OAuth2PasswordRequestForm=Depends(),db:Session = Depends(get_db)):
    real_user=db.query(models.User).filter(models.User.username == login_details.username).first()
    if real_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with username {login_details.username} does not exists")
    verification=verify_password(login_details.password,real_user.password)
    if not verification:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="incorrect password,try again")
    access_token = create_access_token(data={"user_name":login_details.username})#to sign access token with intial credentials as username
    user_posts=db.query(models.User,func.count(models.Post.owner_id).label("total_posts")).join(models.Post,models.User.id == models.Post.owner_id,isouter=True).filter(models.User.id==real_user.id).group_by(models.User.id).first()
    print(user_posts.total_posts)
    return {"access_token":access_token,"token_type":"bearer","total_posts_owned":user_posts.total_posts}

     # select users.*,count(new_posts.owner_id) as no_of_posts from users left join new_posts on users.id = new_posts.owner_id where users.id=1 group by users.id order by users.id;
    



