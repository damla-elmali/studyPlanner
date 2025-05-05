from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict
from enum import Enum
from datetime import date

from database import SessionLocal
from models import (
    TytMockTest, TytMockTestSection,
    AytMockTest, AytMockTestSection,
    YdtMockTest, YdtMockTestSection, TaskQuestionRecord
)
from routers.auth import get_current_user


router = APIRouter()

# ---------------- ENUMS ----------------

class TestType(str, Enum):
    TYT = "TYT"
    AYT = "AYT"
    YDT = "YDT"

# ---------------- STRUCTURES ----------------

TEST_STRUCTURES = {
    TestType.TYT: {
        "Türkçe": 40,
        "Sosyal Bilimler": 20,
        "Matematik": 40,
        "Fen Bilimleri": 20
    },
    TestType.AYT: {
        "Türk Dili ve Edebiyatı - Sosyal Bilimler-1": 40,
        "Sosyal Bilimler-2": 40,
        "Matematik": 40,
        "Fen Bilimleri": 40
    },
    TestType.YDT: {
        "İngilizce": 80,
        "Almanca": 80,
        "Fransızca": 80,
        "Rusça": 80,
        "Arapça": 80
    }
}

# ---------------- DB DEPENDENCY ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- SCHEMAS ----------------

class SectionResult(BaseModel):
    section_name: str
    correct: int
    wrong: int
    blank: int

    def get_total_questions(self) -> int:
        return self.correct + self.wrong + self.blank

    def net_score(self) -> float:
        return round(self.correct - (self.wrong * 0.25), 2)

class TaskQuestionRecordCreate(BaseModel):
    user_id: int
    task_id: int
    total_questions: int
    correct: int
    wrong: int
    blank: int

    @validator('correct', 'wrong', 'blank')
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Values must be non-negative")
        return v

    def get_total_questions(self) -> int:
        return self.correct + self.wrong + self.blank

    def net_score(self) -> float:
        return round(self.correct - (self.wrong * 0.25), 2)

class TestResult(BaseModel):
    test_type: TestType
    test_name: str  # test adı
    test_date: date
    sections: List[SectionResult]

    @validator("sections")
    def validate_sections(cls, sections, values):
        test_type = values.get("test_type")
        if not test_type:
            raise ValueError("test_type must be provided")

        structure = TEST_STRUCTURES[test_type]

        for section in sections:
            expected = structure.get(section.section_name)
            if expected is None:
                raise ValueError(f"{section.section_name}: Invalid section name for {test_type}")

            if section.get_total_questions() != expected:
                raise ValueError(
                    f"{section.section_name}: Expected {expected} questions, got {section.total_questions()}"
                )

        if test_type == TestType.YDT and len(sections) != 1:
            raise ValueError("YDT sınavı için yalnızca bir dil bölümü girilmelidir.")

        return sections

    def summary(self) -> Dict[str, float]:
        return {section.section_name: section.net_score() for section in self.sections}

    def total_net(self) -> float:
        return round(sum(section.net_score() for section in self.sections), 2)

# ---------------- HELPER ----------------
def check_user(user: dict):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def save_mock_test(db: Session, user_id: int, test_result: TestResult):
    test_models = {
        TestType.TYT: (TytMockTest, TytMockTestSection),
        TestType.AYT: (AytMockTest, AytMockTestSection),
        TestType.YDT: (YdtMockTest, YdtMockTestSection),
    }

    mock_test_model, section_model = test_models[test_result.test_type]

    mock_test = mock_test_model(
        user_id=user_id,
        test_date=test_result.test_date,
        test_name =test_result.test_name  # Test adı da ekleniyor

    )
    db.add(mock_test)
    db.flush()

    for section in test_result.sections:
        section_record = section_model(
            mock_test_id=mock_test.id,
            section_name=section.section_name,
            correct=section.correct,
            wrong=section.wrong,
            blank=section.blank,
            net=section.net_score()
        )
        db.add(section_record)

    db.commit()

# ---------------- ROUTES ----------------

@router.post("/analyze-and-save", response_model=dict)
async def analyze_and_save_mock_test(
        test_result: TestResult,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    save_mock_test(db, user["id"], test_result)

    return {
        "message": f"{test_result.test_type} mock test saved successfully.",
        "summary": test_result.summary(),
        "total_net": test_result.total_net()
    }

def convert_to_test_result(test_obj, test_type: TestType, section_model) -> TestResult:
    return TestResult(
        test_type=test_type,
        test_name=test_obj.test_name,
        test_date=test_obj.test_date,
        sections=[
            SectionResult(
                section_name=s.section_name,
                correct=s.correct,
                wrong=s.wrong,
                blank=s.blank
            )
            for s in test_obj.sections
        ]
    )

@router.get("/mock-tests", response_model=List[TestResult])
async def get_mock_tests(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    tyt_tests = db.query(TytMockTest).filter_by(user_id=user["id"]).all()
    ayt_tests = db.query(AytMockTest).filter_by(user_id=user["id"]).all()
    ydt_tests = db.query(YdtMockTest).filter_by(user_id=user["id"]).all()

    all_test_results = []

    for test in tyt_tests:
        all_test_results.append(convert_to_test_result(test, TestType.TYT, TytMockTestSection))

    for test in ayt_tests:
        all_test_results.append(convert_to_test_result(test, TestType.AYT, AytMockTestSection))

    for test in ydt_tests:
        all_test_results.append(convert_to_test_result(test, TestType.YDT, YdtMockTestSection))

    return all_test_results



@router.delete("/mock-tests/{test_type}/{test_id}", response_model=dict)
async def delete_mock_test(
    test_type: str,
    test_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    check_user(user)

    # Test türüne göre ilgili tabloyu seç
    if test_type == "TYT":
        model = TytMockTest
    elif test_type == "AYT":
        model = AytMockTest
    elif test_type == "YDT":
        model = YdtMockTest
    else:
        raise HTTPException(status_code=400, detail="Invalid test type. Choose from 'tyt', 'ayt', or 'ydt'.")

    # Belirtilen test_id ve kullanıcıya ait testi sorgula
    mock_test = db.query(model).filter_by(id=test_id, user_id=user["id"]).first()

    if not mock_test:
        raise HTTPException(status_code=404, detail="Mock test not found.")

    db.delete(mock_test)
    db.commit()

    return {"message": f"{test_type.upper()} mock test {test_id} deleted successfully."}

@router.put("/mock-tests/{test_id}", response_model=dict)
async def update_mock_test(test_id: int, test_result: TestResult, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    check_user(user)

    mock_test = db.query(TytMockTest, AytMockTest, YdtMockTest).filter_by(id=test_id, user_id=user["id"]).first()

    if not mock_test:
        raise HTTPException(status_code=404, detail="Mock test not found")

    mock_test.test_date = test_result.test_date
    db.commit()

    for section in test_result.sections:
        section_record = db.query(TytMockTestSection, AytMockTestSection, YdtMockTestSection).filter_by(mock_test_id=mock_test.id, section_name=section.section_name).first()

        if section_record:
            section_record.correct = section.correct
            section_record.wrong = section.wrong
            section_record.blank = section.blank
            section_record.net = section.net_score()

    db.commit()
    return {"message": f"Mock test {test_id} updated successfully."}
