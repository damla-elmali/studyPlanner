from sqlalchemy.orm import Session
from models import TaskQuestionRecord, LessonPerformanceSummary, Tasks
from sqlalchemy import func

def update_lesson_summary_from_record(db: Session, user_id: int, lesson_id: int):
    # Tüm kayıtları çek bu kullanıcı ve ders için
    records = (
        db.query(TaskQuestionRecord)
        .filter_by(user_id=user_id, lesson_id=lesson_id)
        .all()
    )

    # Toplamları hesapla
    total_questions = sum(r.total_questions for r in records)
    correct = sum(r.correct for r in records)
    wrong = sum(r.wrong for r in records)
    blank = sum(r.blank for r in records)

    # Tüm taskların sürelerini topla
    task_ids = list(set(r.task_id for r in records))
    total_time = db.query(func.sum(Tasks.estimated_time)).filter(Tasks.id.in_(task_ids)).scalar() or 0

    # Güncelleme veya yeni oluşturma
    summary = (
        db.query(LessonPerformanceSummary)
        .filter_by(user_id=user_id, lesson_id=lesson_id)
        .first()
    )

    if summary:
        summary.total_questions = total_questions
        summary.correct = correct
        summary.wrong = wrong
        summary.blank = blank
        summary.total_time = total_time
    else:
        summary = LessonPerformanceSummary(
            user_id=user_id,
            lesson_id=lesson_id,
            total_questions=total_questions,
            correct=correct,
            wrong=wrong,
            blank=blank,
            total_time=total_time
        )
        db.add(summary)

    db.commit()
