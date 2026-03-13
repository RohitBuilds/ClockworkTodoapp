from fastapi import APIRouter,status,HTTPException,Depends
from models.todo import Todo
from pydantic import BaseModel,config,ConfigDict
from database import Base, engine,SessionLocal
from sqlalchemy.orm import Session
from typing import Optional
from routes.signin import get_db
from models.users import User
from routes.task import schedule_notification  
from fastapi import BackgroundTasks
from models.notifications import Notification
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone, timedelta


# router=APIRouter(prefix='/app/v1',tags=['Todos'])
router = APIRouter(tags=["Todos"])
scheduler = BackgroundScheduler()
scheduler.start()
    
class TodoCreate(BaseModel):
    title:str
    description:str
    completed:bool=False
    due_time: Optional[datetime] = None

class TodoInDB(BaseModel):
        id:int
        title:str
        description:str
        completed:bool
        due_time: Optional[datetime] = None 
        class Config:
            from_attributes=True
            
class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    read: bool
    timestamp: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Convert naive IST datetime to UTC
def convert_ist_to_utc(due_time_ist: datetime) -> datetime:
    if due_time_ist.tzinfo is None:
        ist_offset = timedelta(hours=5, minutes=30)
        due_time_utc = due_time_ist - ist_offset
        return due_time_utc.replace(tzinfo=timezone.utc)
    return due_time_ist.astimezone(timezone.utc)

# Function to send notification
def send_notification(user_id: int, task_id: int):
    db = SessionLocal()
    try:
        task = db.query(Todo).filter(Todo.id == task_id).first()

        # If task is completed, skip notification
        if task and task.completed:
            print(f"[SKIPPED] Task {task.id} already completed")
            return

        notification = Notification(
            user_id=user_id,
            message=f"Reminder: Your task '{task.title}' is due now!",
            read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        print(f"[NOTIFICATION SAVED] User {user_id} - {notification.message}")

    finally:
        db.close()

# Create todo endpoint
@router.post('/createtodos', status_code=status.HTTP_201_CREATED)
def create_todo(item: TodoCreate, user_id: int, db: Session = Depends(get_db)):
    # Save todo in DB
    todo = Todo(
        title=item.title,
        description=item.description,
        completed=item.completed,
        due_time=item.due_time,
        user_id=user_id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    if todo.due_time:
        due_time_utc = convert_ist_to_utc(todo.due_time)
        scheduler.add_job(
               send_notification,
               "date",
        run_date=due_time_utc,
        args=[todo.user_id, todo.id]
        )

        print(f"[INFO] Notification scheduled for {due_time_utc} UTC")


    return {"message": "TODO created successfully", "todo": {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "due_time": todo.due_time
    }}

@router.get("/notifications")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.read == False
    ).all()
    result = []
    for n in notifications:
        result.append({
            "id": n.id,
            "message": n.message
        })
        n.read = True
        #db.delete(n)   # optional (prevents duplicate notifications)
    db.commit()
    return result


@router.get("/getalltodos/{user_id}")
def get_user_todos(user_id: int, db: Session = Depends(get_db)):
    todos = db.query(Todo).filter(Todo.user_id == user_id).all()
    return todos


#API for getting a Todo by id
@router.get('/gettodosbyid/{item_id}',status_code=status.HTTP_200_OK)
def get_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')    
    return todo

#API for deleting a Todo by id
@router.delete('/deletetodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    db.delete(todo)
    db.commit()
    return {'message':f'TODO with id {item_id} deleted successfully'}
    
#API for updating a Todo by id
@router.put('/updatetodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def update_todo_by_id(item_id:int,data:TodoCreate,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    
    todo.title=data.title
    todo.description=data.description
    todo.completed=data.completed
    db.commit()
    return {'message':f'TODO with id {item_id} updated successfully'}
    
#API for toggling the completed status of a Todo by id
@router.patch('/toggletodosbyid/{item_id}',status_code=status.HTTP_204_NO_CONTENT)
def toggle_todo_by_id(item_id:int,db:Session=Depends(get_db)):
    todo=db.query(Todo).filter(Todo.id==item_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'TODO with id {item_id} not found')
    todo.completed=not todo.completed
    db.commit()
    return {'message':f'TODO with id {item_id} toggled successfully'}
    

# #API for deleting all TODOs
@router.delete('/deletealltodos/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_todos_for_user(user_id: int, db: Session = Depends(get_db)):
    todos = db.query(Todo).filter(Todo.user_id == user_id).all()
    if not todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No TODOs found for user with id {user_id}'
        )
    db.query(Todo).filter(Todo.user_id == user_id).delete(synchronize_session=False)
    db.commit()
    return {'message': f'All TODOs for user {user_id} deleted successfully'}

#Api to get user specific TODOs
@router.get('/getusertodos/{user_id}',status_code=status.HTTP_200_OK )
def get_user_todos(user_id:int,db:Session=Depends(get_db)):
    todos=db.query(Todo).filter(Todo.user_id==user_id).all()
    if len(todos)==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No TODOs found for user with id {user_id}')
    return todos


# Mark notification as read
@router.put("/notifications/read/{notif_id}")
def mark_notification_read(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read = True
    db.commit()
    return {"message": "Notification marked as read"}
