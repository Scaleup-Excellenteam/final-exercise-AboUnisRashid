from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create the base class for declarative models
Base = declarative_base()
"""
Base class provides a set of common functionality for declarative models.
It is used as a base class for our User and Upload classes to inherit from.
This allows SQLAlchemy to track and manage the defined models.
"""


class User(Base):
    """
    Class User represents a user in the system with a unique email address.
    It has a one-to-many relationship with the Upload class, representing the files uploaded by the user.
    """

    # Define the table name for the User model
    __tablename__ = "users"

    # Primary key column for the User model
    id = Column(Integer, primary_key=True)

    # Email column with unique constraint and non-nullability
    email = Column(String, unique=True, nullable=False)

    # Relationship with the Upload model, specifying the back reference and cascade behavior
    uploads = relationship("Upload", back_populates="user", cascade="all, delete")


class Upload(Base):
    """
    Class Upload represents an uploaded file in the system.
    It has a foreign key reference to the User model and a one-to-many relationship with the User class.
    """

    # Define the table name for the Upload model
    __tablename__ = "uploads"

    # Primary key column for the Upload model
    id = Column(Integer, primary_key=True)

    # UID column for the uploaded file with non-nullability
    uid = Column(String, nullable=False)

    # Filename column for the uploaded file with non-nullability
    filename = Column(String, nullable=False)

    # Upload time column with non-nullability
    upload_time = Column(DateTime, nullable=False)

    # Finish time column that can be nullable
    finish_time = Column(DateTime)

    # Status column for the upload
    status = Column(String)

    # Foreign key column referencing the id column of the User model
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with the User model, specifying the back reference
    user = relationship("User", back_populates="uploads")
