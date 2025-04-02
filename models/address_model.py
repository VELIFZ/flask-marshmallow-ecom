from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional
from .base import Base
from .user_model import User
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

# Enum class to centralized list of allowed values - a group of related constant values
# inherit from str so Marshmallow sees string values not custom objects
# avoids duplication - 'home', 'Home'...
class AddressType(str, Enum):
    HOME = 'Home'
    WORK = "Work"
    OTHER = "Other"

class Address(Base):
    """
    Address model for user shipping addresses.
    
    Relationships:
        - user: User who owns this address
    """
    __tablename__ ='addresses'
    
    # Basic address information fields
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
        # helps to identify primary shipping address
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
        # categorize addresses (Work, Home, Other)  
    #address_type: Mapped[Optional[str]] = mapped_column(String(50))
    # This prevents invalid data from being saved in database
    address_type: Mapped[Optional[AddressType]] = mapped_column(SQLAlchemyEnum(AddressType), nullable=True)
    
    # Relationships -> Many-to-One
    # ForeignKey linking Address to User - each address must belong to a user
    # Made nullable=True temporarily for testing
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    # Relationship back to User
    # This creates bidirectional relationship with user model's addresses field
    # One user can have Many addresses, but each address belongs to One user
    user: Mapped[Optional["User"]] = relationship(back_populates="addresses", lazy="noload")
    
#? Method to set this address as default and unset others
# # Method to set this address as default and unset others
# def set_as_default(self, session: Session):
#     """
#     Set this address as the default and unset all other addresses for the user.
#     """
#     session.query(Address).filter(
#         Address.user_id == self.user_id,
#         Address.id != self.id
#     ).update({"is_default": False})

#     self.is_default = True
#     session.commit()
