from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from typing import Literal, List, Dict, Optional
from enum import Enum
from datetime import date

from database import SessionLocal
from models import MockTest, MockTestSection, TestTypeEnum
from routers.auth import get_current_user

router = APIRouter()


# ---------------- ENUMS ----------------

class TestType(str, Enum):
    TYT = "TYT"
    AYT = "AYT"
    YDT = "YDT"


# ---------------- STRUCTURES ----------------

TYT_STRUCTURE = {
    "Türkçe": 40,
    "Sosyal Bilimler": 20,
    "Matematik": 40,
    "Fen Bilimleri": 20
}

AYT_STRUCTURE = {
    "Türk Dili ve Edebiyatı - Sosyal Bilimler-1": 40,
    "Sosyal Bilimler-2": 40,
    "Matematik": 40,
    "Fen Bilimleri": 40
}

YDT_STRUCTURE = {
    "English": 80,
    "German": 80,
    "French": 80,
    "Russian": 80,
    "Arabic": 80
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
    blank: int
    wrong: int

    @validator('correct', 'blank', 'wrong')
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Values must be non-negative")
        return v

    def total_questions(self) -> int:
        return self.correct + self.blank + self.wrong

    def net_score(self) -> float:
        return round(self.correct - (self.wrong * 0.25), 2)


class TestResult(BaseModel):
    test_type: TestType
    test_date: date
    sections: List[SectionResult]

    @validator("sections")
    def validate_sections(cls, sections, values):
        test_type = values.get("test_type")
        if not test_type:
            raise ValueError("test_type must be provided before sections are validated")

        structure = {
            TestType.TYT: TYT_STRUCTURE,
            TestType.AYT: AYT_STRUCTURE,
            TestType.YDT: YDT_STRUCTURE
        }[test_type]

        for section in sections:
            expected = structure.get(section.section_name)
            if expected is None:
                raise ValueError(f"{section.section_name}: Invalid section name for {test_type}")

            actual = section.total_questions()
            if actual != expected:
                raise ValueError(f"{section.section_name}: Expected {expected} questions, got {actual}")

        if test_type == TestType.YDT and len(sections) != 1:
            raise ValueError("YDT sınavı için yalnızca bir dil bölümü girilmelidir.")

        return sections

    def summary(self) -> Dict[str, float]:
        return {section.section_name: section.net_score() for section in self.sections}

    def total_net(self) -> float:
        return round(sum(section.net_score() for section in self.sections), 2)


# ---------------- ROUTE ----------------

@router.post("/analyze-and-save-mock-test")
def analyze_and_save_mock_test(
        test_result: TestResult,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Save MockTest
    mock_test = MockTest(
        user_id=user["id"],
        test_type=test_result.test_type,
        test_date=test_result.test_date
    )
    db.add(mock_test)
    db.flush()  # To get mock_test.id

    # Save each section
    for section in test_result.sections:
        net = section.net_score()
        section_record = MockTestSection(
            mock_test_id=mock_test.id,
            section_name=section.section_name,
            correct=section.correct,
            blank=section.blank,
            wrong=section.wrong,
            net=net
        )
        db.add(section_record)

    db.commit()

    return {
        "message": "Mock test successfully saved.",
        "summary": test_result.summary(),
        "total_net": test_result.total_net()
    }
