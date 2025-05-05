from sqlalchemy import Column, Date, Float, Integer, String, DateTime, Time, Text, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

# -------------------------- Enum for Mock Test Types --------------------------
class TestTypeEnum(str, enum.Enum):
    TYT = "TYT"
    AYT = "AYT"
    YDT = "YDT"

# -------------------------- User Model --------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    phone_number = Column(String, unique=True, index=True)
    score = Column(Integer, default=0)
    grade = Column(String)  # e.g., 9, 10, 11, 12

    tyt_mock_tests = relationship("TytMockTest", back_populates="user")
    ayt_mock_tests = relationship("AytMockTest", back_populates="user")
    ydt_mock_tests = relationship("YdtMockTest", back_populates="user")
    task_question_records = relationship("TaskQuestionRecord", back_populates="user")
    weeklyplans = relationship("WeeklyPlans", back_populates="user")
    tasks = relationship("Tasks", back_populates="user")
    schedule_slots = relationship('ScheduleSlot', back_populates='user')
    lesson_performance_summaries = relationship("LessonPerformanceSummary", back_populates="user")


# -------------------------- Tasks Model --------------------------
class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    lesson_id = Column(Integer, ForeignKey('lessons.id'))  # Dersin ID'si
    description = Column(String)
    priority = Column(Integer)
    deadline = Column(Date)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    estimated_time = Column(Integer)

    task_question_records = relationship("TaskQuestionRecord", back_populates="task")
    weeklyplans = relationship("WeeklyPlans", back_populates="task")
    schedule_slots = relationship('ScheduleSlot', back_populates="task")
    user = relationship("User", back_populates="tasks")
    lesson = relationship("Lesson", back_populates="tasks")  # Relationship to Lesson


# -------------------------- WeeklyPlans Model --------------------------
class WeeklyPlans(Base):
    __tablename__ = 'weeklyplans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    day = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    user = relationship("User", back_populates="weeklyplans")
    task = relationship("Tasks", back_populates="weeklyplans")


# -------------------------- Lesson Model --------------------------
class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Dersin adı

    tasks = relationship("Tasks", back_populates="lesson")  # Görevler ile ilişki
    task_question_records = relationship("TaskQuestionRecord", back_populates="lesson")
    lesson_performance_summaries = relationship("LessonPerformanceSummary", back_populates="lesson")


# -------------------------- TaskQuestionRecord Model --------------------------
class TaskQuestionRecord(Base):
    __tablename__ = "task_question_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct = Column(Integer, nullable=False)
    wrong = Column(Integer, nullable=False)
    blank = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="task_question_records")
    task = relationship("Tasks", back_populates="task_question_records")
    lesson = relationship("Lesson", back_populates="task_question_records")



class LessonPerformanceSummary(Base):
    __tablename__ = "lesson_performance_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)

    total_questions = Column(Integer, default=0)
    correct = Column(Integer, default=0)
    wrong = Column(Integer, default=0)
    blank = Column(Integer, default=0)
    total_time = Column(Integer, default=0)  # Dakika cinsinden

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson_summary'),)

    # İlişkiler
    user = relationship("User", back_populates="lesson_performance_summaries")
    lesson = relationship("Lesson", back_populates="lesson_performance_summaries")



# -------------------------- ScheduleSlot Model --------------------------
class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day = Column(String)  # e.g. "Monday"
    start_time = Column(Time)
    end_time = Column(Time)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    user = relationship("User", back_populates="schedule_slots")
    task = relationship("Tasks", back_populates="schedule_slots")


# -------------------------- TYT --------------------------
class TytMockTest(Base):
    __tablename__ = "tyt_mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(Date, nullable=False)
    test_name = Column(String)  # Test ismi ekleniyor


    user = relationship("User", back_populates="tyt_mock_tests")
    sections = relationship("TytMockTestSection", back_populates="mock_test", cascade="all, delete-orphan")


class TytMockTestSection(Base):
    __tablename__ = "tyt_mock_test_sections"

    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("tyt_mock_tests.id"), nullable=False)
    section_name = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)
    blank = Column(Integer, nullable=False)
    wrong = Column(Integer, nullable=False)
    net = Column(Float, nullable=False)

    mock_test = relationship("TytMockTest", back_populates="sections")


# -------------------------- AYT --------------------------
class AytMockTest(Base):
    __tablename__ = "ayt_mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(Date, nullable=False)
    test_name = Column(String)  # Test ismi ekleniyor


    sections = relationship("AytMockTestSection", back_populates="mock_test", cascade="all, delete-orphan")
    user = relationship("User", back_populates="ayt_mock_tests")


class AytMockTestSection(Base):
    __tablename__ = "ayt_mock_test_sections"

    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("ayt_mock_tests.id"), nullable=False)
    section_name = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)
    wrong = Column(Integer, nullable=False)
    blank = Column(Integer, nullable=False)
    net = Column(Float, nullable=False)

    mock_test = relationship("AytMockTest", back_populates="sections")


# -------------------------- YDT --------------------------
class YdtMockTest(Base):
    __tablename__ = "ydt_mock_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(Date, nullable=False)
    test_name = Column(String)  # Test ismi ekleniyor


    sections = relationship("YdtMockTestSection", back_populates="mock_test", cascade="all, delete-orphan")
    user = relationship("User", back_populates="ydt_mock_tests")


class YdtMockTestSection(Base):
    __tablename__ = "ydt_mock_test_sections"

    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("ydt_mock_tests.id"), nullable=False)
    section_name = Column(String, nullable=False)
    correct = Column(Integer, nullable=False)
    wrong = Column(Integer, nullable=False)
    blank = Column(Integer, nullable=False)
    net = Column(Float, nullable=False)

    mock_test = relationship("YdtMockTest", back_populates="sections")

