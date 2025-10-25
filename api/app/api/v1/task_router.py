from fastapi import APIRouter
from app.tasks.check_keys_task import add

router = APIRouter()

@router.post("/check-keys/")
def add_numbers(a: int, b: int):
    task = add.delay(a, b)
    return {"task_id": task.id}
