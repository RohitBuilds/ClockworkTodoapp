
import time
from datetime import datetime, timezone
from models.notifications import Notification

def schedule_notification(user_id: int, task_title: str, due_time: datetime, db_session):
    # Step 1: Treat naive due_time as local time and convert to UTC
    if due_time.tzinfo is None:
        # Assuming your input is IST (UTC+5:30)
        from datetime import timedelta
        ist_offset = timedelta(hours=5, minutes=30)
        due_time = due_time - ist_offset  # convert IST → UTC
        due_time = due_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delay = (due_time - now).total_seconds()
    
    if delay > 0:
        print(f"[INFO] Waiting {delay} seconds for task '{task_title}'")
        time.sleep(delay)
    
    notification = Notification(
        user_id=user_id,
        message=f"Reminder: Your task '{task_title}' is due now!"
    )
    db_session.add(notification)
    db_session.commit()
    
    print(f"[NOTIFICATION] User {user_id} - Task '{task_title}' notification created at {datetime.now(timezone.utc)}")
