"""Google credential model."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class GoogleCredential(BaseModel):
    """Google OAuth credential model."""
    
    __tablename__ = "google_credentials"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_uri = Column(String(500), nullable=True)
    client_id = Column(String(500), nullable=True)
    client_secret = Column(String(500), nullable=True)
    scopes = Column(Text, nullable=True)  # JSON array of scopes
    expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="google_credential")
    
    def __repr__(self):
        return f"<GoogleCredential(id={self.id}, user_id={self.user_id})>"
