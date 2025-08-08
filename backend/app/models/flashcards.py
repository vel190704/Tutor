# /app/models/flashcards.py

from datetime import datetime, timedelta
import uuid
from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB

class Flashcard(db.Model):
    """
    Flashcard model representing a single flashcard in the system.
    Implements SM-2 spaced repetition algorithm.
    """
    __tablename__ = 'flashcards'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(db.String(36), db.ForeignKey('decks.id'), nullable=False)
    front_content = db.Column(db.Text, nullable=False)
    back_content = db.Column(db.Text, nullable=False)
    tags = db.Column(JSONB)  # Array of tags for categorization
    
    # Spaced repetition fields
    ease_factor = db.Column(db.Float, default=2.5)  # EF (SM-2 algorithm)
    interval = db.Column(db.Integer, default=1)     # Interval in days
    repetition = db.Column(db.Integer, default=0)    # n+1 (number of successful recalls)
    next_review = db.Column(db.DateTime)            # Next scheduled review
    
    # Difficulty tracking
    difficulty = db.Column(db.Float, default=3.0)    # 1-5 scale (1=easiest, 5=hardest)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    deck = db.relationship('Deck', back_populates='flashcards')
    user = db.relationship('User', back_populates='flashcards')
    reviews = db.relationship('FlashcardReview', back_populates='flashcard', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Flashcard, self).__init__(**kwargs)
        self.id = str(uuid.uuid4())
        if not self.next_review:
            self.next_review = datetime.utcnow()

    def record_review(self, quality_response):
        """
        Update flashcard spacing based on SM-2 algorithm
        quality_response: 0-5 scale of how well user remembered the card
        """
        quality = min(max(quality_response, 0), 5)
        
        if quality < 3:
            # Incorrect answer - reset repetitions but keep ease factor
            self.repetition = 0
            self.interval = 1
        else:
            # Correct answer
            self.ease_factor = max(1.3, self.ease_factor + (
                0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            ))
            
            if self.repetition == 0:
                self.interval = 1
            elif self.repetition == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
            
            self.repetition += 1
        
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        self.updated_at = datetime.utcnow()
        
        return self

    def calculate_memory_strength(self):
        """Calculate predicted memory strength from 0-1"""
        time_elapsed = (datetime.utcnow() - self.updated_at).days
        memory = 1.0 / (1.0 + (time_elapsed / (self.interval * 0.5)) ** 2)
        return max(0, min(1, memory))

    def to_dict(self):
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'front_content': self.front_content,
            'back_content': self.back_content,
            'tags': self.tags,
            'spacing': {
                'ease_factor': self.ease_factor,
                'interval': self.interval,
                'repetition': self.repetition,
                'next_review': self.next_review.isoformat(),
                'difficulty': self.difficulty
            },
            'memory_strength': self.calculate_memory_strength(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Deck(db.Model):
    """Flashcard deck model"""
    __tablename__ = 'decks'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(64))
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    flashcards = db.relationship('Flashcard', back_populates='deck')
    user = db.relationship('User', back_populates='decks')

    def __init__(self, **kwargs):
        super(Deck, self).__init__(**kwargs)
        self.id = str(uuid.uuid4())

    def to_dict(self, include_flashcards=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'flashcard_count': len(self.flashcards),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_flashcards:
            data['flashcards'] = [f.to_dict() for f in sorted(
                self.flashcards, 
                key=lambda x: x.calculate_memory_strength()
            )]
            
        return data


class FlashcardReview(db.Model):
    """Track individual flashcard review sessions"""
    __tablename__ = 'flashcard_reviews'

    id = db.Column(db.String(36), primary_key=True)
    flashcard_id = db.Column(db.String(36), db.ForeignKey('flashcards.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    review_time = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)  # Time taken to answer (seconds)
    response_quality = db.Column(db.Integer)  # 0-5 scale
    
    # Relationships
    flashcard = db.relationship('Flashcard', back_populates='reviews')
    user = db.relationship('User')

    def __init__(self, **kwargs):
        super(FlashcardReview, self).__init__(**kwargs)
        self.id = str(uuid.uuid4())

    def to_dict(self):
        return {
            'id': self.id,
            'flashcard_id': self.flashcard_id,
            'review_time': self.review_time.isoformat(),
            'response_time': self.response_time,
            'response_quality': self.response_quality
        }
