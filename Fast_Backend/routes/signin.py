from fastapi import APIRouter,status,HTTPException,Depends
from models import users
from models.todo import Todo
from models.users import User
from pydantic import BaseModel
from database import Base, engine,SessionLocal
from sqlalchemy.orm import Session
from auth import hash_password, verify_password

router=APIRouter(prefix='/app/v1',tags=['users'])

class UserCreate(BaseModel):
    username:str
    email:str
    password:str

class UserLogin(BaseModel):
    email:str
    password:str
     

class UserInDB(BaseModel):
        user_id:int
        username:str
        email:str
        password:str
        class Config:
            from_attributes=True

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

#API for creating a new user
@router.post('/signup', status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists'
        )
    # Hash password
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        'message': 'User created successfully',
        'user_id': new_user.user_id
    }


@router.post('/signin',status_code=status.HTTP_200_OK)
def signin_user(user:UserLogin,db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )
    return {
        'message': 'User signed in successfully',
        'user_id': db_user.user_id
    }
@router.get('/getallusers',status_code=status.HTTP_200_OK)
def get_users(db:Session=Depends(get_db)):
    users=db.query(User).all()
    return users

@router.delete('/deleteusersbyid/{user_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(user_id:int,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.user_id==user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'User with id {user_id} not found')
    db.delete(user)
    db.commit()
    return {'message':f'User with id {user_id} deleted successfully'}

@router.delete('/deleteallusers',status_code=status.HTTP_204_NO_CONTENT)
def delete_all_users(db:Session=Depends(get_db)):
        db.query(User).delete(synchronize_session=False)
        db.commit()
        return {'message':'All users deleted successfully'}