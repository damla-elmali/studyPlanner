from datetime import date
from typing import Annotated, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from models import Tasks, User, Lesson, TaskQuestionRecord
from database import SessionLocal
from routers.analyzer import TaskQuestionRecordCreate
from routers.auth import get_current_user, templates
from utils.analytics_updater import update_lesson_summary_from_record
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse


router = APIRouter()

templates = Jinja2Templates(directory="templates")

class TaskCreate(BaseModel):
    title: str = Field(..., example="Task Title")
    lesson_id: int = Field(..., example=1)  # Burada artık lesson_id olacak
    description: str = Field(..., example="Task Description")
    priority: int = Field(..., example=1)
    deadline: date = Field(..., example="2025-05-06")
    completed: bool = Field(False, example=False)
    estimated_time: int = Field(..., example=120)  # minute-based time as an integer

    @validator('estimated_time')
    def validate_estimated_time(cls, v):
        if v <= 0:
            raise ValueError("Estimated time must be a positive integer representing minutes.")
        return v


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- HELPER ----------------
def check_user(user: dict):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# ddf
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response


# TASK SAYFASINI GÖRÜNTÜLE
@router.get("/tasks-page")
async def render_tasks_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        tasks = db.query(Tasks).filter(Tasks.owner_id == user.get('id')).all()
        return templates.TemplateResponse("edit-task.html", {"request": request, "tasks": tasks, "user": user})
    except:
        return redirect_to_login()


# YENİ TASK EKLEME SAYFASINI GÖRÜNTÜLE
@router.get("/add-task-page")
async def render_add_task_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse("edit-task.html", {"request": request, "user": user})
    except:
        return redirect_to_login()


# TASK DÜZENLEME SAYFASINI GÖRÜNTÜLE
@router.get("/edit-task-page/{task_id}")
async def render_edit_task_page(request: Request, task_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        task = db.query(Tasks).filter(Tasks.id == task_id).first()
        return templates.TemplateResponse("edit-task.html", {"request": request, "task": task, "user": user})
    except:
        return redirect_to_login()






# Create Task
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, task_request: TaskCreate):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Lesson ID'sine göre ders bilgisini alıyoruz
    lesson = db.query(Lesson).filter(Lesson.id == task_request.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    # Yeni görev oluşturuyoruz
    task = Tasks(**task_request.dict(), owner_id=user.get('id'), lesson_name=lesson.name)

    # Görevi veritabanına ekliyoruz
    db.add(task)
    db.commit()

    return {"message": "Task created successfully", "task_id": task.id}


# Get All Tasks
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Tasks).filter(Tasks.owner_id == user.get('id')).all()


# Delete Task
@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user)
):
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.owner_id == user.get("id")).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


# Update Task
@router.put("/task/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
        task_id: int,
        task_update: TaskCreate,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user)
):
    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.owner_id == user.get("id")).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ders ID'si ile ilgili ders bilgisini alıyoruz
    lesson = db.query(Lesson).filter(Lesson.id == task_update.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    task.title = task_update.title
    task.description = task_update.description
    task.priority = task_update.priority
    task.deadline = task_update.deadline
    task.completed = task_update.completed
    task.lesson_id = lesson.id  # Dersin ID'si burada kullanılıyor

    db.commit()
    return {"message": "Task updated successfully"}



@router.put("/task/{task_id}/complete-with-analysis", status_code=status.HTTP_200_OK)
async def complete_task_with_analysis(
    task_id: int,
    payload: TaskQuestionRecordCreate = Body(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    task = db.query(Tasks).filter(Tasks.id == task_id, Tasks.owner_id == user.get("id")).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.completed:
        raise HTTPException(status_code=400, detail="Task already completed")

    # Görevi tamamlandı olarak işaretle
    task.completed = True
    db.commit()

    # Aynı görev için tekrar kayıt yapılmasın
    existing_record = db.query(TaskQuestionRecord).filter(
        TaskQuestionRecord.task_id == task_id,
        TaskQuestionRecord.user_id == user.get("id")
    ).first()
    if existing_record:
        raise HTTPException(status_code=400, detail="Analysis already exists for this task")

    # Analiz kaydı oluştur
    task_record = TaskQuestionRecord(
        user_id=user["id"],
        task_id=task_id,
        lesson_id=payload.lesson_id,
        total_questions=payload.total_questions,
        correct=payload.correct,
        wrong=payload.wrong,
        blank=payload.blank
    )

    db.add(task_record)
    db.commit()

    return {"message": "Task marked as completed and analysis recorded successfully"}




@router.post("/analyze-and-save-task-questions", response_model=dict)
async def record_task_questions(payload: TaskQuestionRecordCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    task_record = TaskQuestionRecord(
        user_id=payload.user_id,
        task_id=payload.task_id,
        lesson_id=payload.lesson_id,
        total_questions=payload.total_questions,
        correct=payload.correct,
        wrong=payload.wrong,
        blank=payload.blank
    )
    db.add(task_record)
    db.commit()

    # 2. LessonPerformanceSummary güncelle
    update_lesson_summary_from_record(
        db=db,
        user_id=payload.user_id,
        lesson_id=payload.lesson_id
    )

    return {"message": "Task question record added successfully."}

@router.get("/task-question-records/{task_id}", response_model=List[TaskQuestionRecordCreate])
async def get_task_question_records(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    task_records = db.query(TaskQuestionRecord).filter_by(task_id=task_id).all()
    if not task_records:
        raise HTTPException(status_code=404, detail="No records found for the task.")
    return task_records

@router.delete("/task-question-records/{task_id}", response_model=dict)
async def delete_task_question_record(task_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    task_records = db.query(TaskQuestionRecord).filter_by(task_id=task_id).all()

    if not task_records:
        raise HTTPException(status_code=404, detail="No records found for the task.")

    for record in task_records:
        db.delete(record)

    db.commit()
    return {"message": f"All records for task {task_id} deleted successfully."}

@router.put("/task-question-records/{task_id}", response_model=dict)
async def update_task_question_record(task_id: int, payload: TaskQuestionRecordCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    task_record = db.query(TaskQuestionRecord).filter_by(task_id=task_id, user_id=payload.user_id).first()

    if not task_record:
        raise HTTPException(status_code=404, detail="Task question record not found.")

    task_record.correct = payload.correct
    task_record.wrong = payload.wrong
    task_record.blank = payload.blank
    task_record.total_questions = payload.total_questions
    db.commit()

    return {"message": f"Task question record for task {task_id} updated successfully."}

@router.get("/lesson_analysis", response_model=List[Dict[str, int]])
async def lesson_analysis(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    results = db.query(
        TaskQuestionRecord.lesson_id,
        func.sum(TaskQuestionRecord.correct).label('correct'),
        func.sum(TaskQuestionRecord.wrong).label('wrong'),
        func.sum(TaskQuestionRecord.blank).label('blank'),
        func.count(TaskQuestionRecord.id).label('total_questions')
    ).filter_by(user_id=user["id"]).group_by(TaskQuestionRecord.lesson_id).all()

    lesson_analysis_results = [
        {
            'lesson_id': result.lesson_id,
            'correct': result.correct,
            'wrong': result.wrong,
            'blank': result.blank,
            'total_questions': result.total_questions
        }
        for result in results
    ]

    return lesson_analysis_results



