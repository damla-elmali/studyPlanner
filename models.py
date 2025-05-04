from sqlalchemy import Column, Integer, String, DateTime, Time, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

# --------------------------


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

    progress = relationship("TopicProgress", back_populates="user", cascade="all, delete")


# --------------------------


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    deadline = Column(String)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))


# --------------------------


class Analyzer(Base):
    __tablename__ = "analyzer"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_title = Column(String, nullable=False)
    test_date = Column(DateTime, default=datetime.datetime.utcnow)
    test_type = Column(String, nullable=False)  # TYT, AYT, YDT, Branş
    lesson_category = Column(String, nullable=True)
    notes = Column(Text)

    mistakes = relationship("Mistake", back_populates="analyzer", cascade="all, delete")


# --------------------------


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # e.g., Matematik
    category = Column(String)  # e.g., TYT, AYT

    topics = relationship("Topic", back_populates="lesson", cascade="all, delete")


# --------------------------


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String)  # e.g., Temel Kavramlar
    lesson_id = Column(Integer, ForeignKey("lessons.id"))

    lesson = relationship("Lesson", back_populates="topics")
    mistakes = relationship("Mistake", back_populates="topic")
    progress = relationship("TopicProgress", back_populates="topic", cascade="all, delete")


# --------------------------


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(Integer, primary_key=True, index=True)
    analyzer_id = Column(Integer, ForeignKey("analyzer.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    detail_note = Column(Text)
    is_reviewed = Column(Boolean, default=False)

    analyzer = relationship("Analyzer", back_populates="mistakes")
    topic = relationship("Topic", back_populates="mistakes")


# --------------------------


class TopicProgress(Base):
    __tablename__ = "topic_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    last_reviewed = Column(DateTime, default=datetime.datetime.utcnow)
    mistake_count = Column(Integer, default=0)
    mastery_level = Column(Integer, default=0)  # 0–100 scale for understanding

    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")


# --------------------------


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferred_start_hour = Column(Integer)  # like 9 (9 AM)
    preferred_end_hour = Column(Integer)    # like 18 (6 PM)
    preferred_days = Column(String)         # e.g. "Mon,Tue,Wed"
    auto_plan_enabled = Column(Boolean, default=True)
    # Optional: relationship to User


# --------------------------


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day = Column(String)                   # e.g. "Monday"
    start_time = Column(Time)
    end_time = Column(Time)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    # Optional relationships:
    task = relationship("Tasks")
    topic = relationship("Topic")