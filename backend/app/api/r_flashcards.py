from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from typing import List, Dict, Optional
import uuid
import json
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask Blueprint
flashcards_bp = Blueprint('flashcards', __name__)

class FlashcardManager:
    def __init__(self):
        self.decks = {}  # {deck_id: deck}
        self.cards = {}  # {card_id: card}
        self.storage_path = Path('./flashcard_data')
        self._initialize_storage()

    def _initialize_storage(self):
        """Create storage directory if it doesn't exist"""
        self.storage_path.mkdir(exist_ok=True)

    def create_deck(self, title: str, description: str = "") -> Dict:
        """Create a new flashcard deck"""
        deck_id = str(uuid.uuid4())
        deck = {
            'id': deck_id,
            'title': title,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'card_ids': []
        }
        self.decks[deck_id] = deck
        self._save_deck(deck_id)
        return deck

    def create_card(self, deck_id: str, front: str, back: str) -> Dict:
        """Create a new flashcard"""
        if deck_id not in self.decks:
            raise ValueError("Deck does not exist")

        card_id = str(uuid.uuid4())
        card = {
            'id': card_id,
            'deck_id': deck_id,
            'front': front,
            'back': back,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'stats': {
                'attempts': 0,
                'correct': 0,
                'last_reviewed': None
            }
        }
        self.cards[card_id] = card
        
        # Add card to deck
        self.decks[deck_id]['card_ids'].append(card_id)
        self.decks[deck_id]['updated_at'] = datetime.now().isoformat()
        
        self._save_deck(deck_id)
        self._save_card(card_id)
        
        return card

    def get_deck(self, deck_id: str) -> Optional[Dict]:
        """Get a deck by ID"""
        return self.decks.get(deck_id)

    def get_card(self, card_id: str) -> Optional[Dict]:
        """Get a card by ID"""
        return self.cards.get(card_id)

    def get_cards_in_deck(self, deck_id: str) -> List[Dict]:
        """Get all cards in a deck"""
        if deck_id not in self.decks:
            return []
        
        return [self.cards[card_id] for card_id in self.decks[deck_id]['card_ids']]

    def update_card(self, card_id: str, front: str = None, back: str = None) -> Optional[Dict]:
        """Update an existing flashcard"""
        if card_id not in self.cards:
            return None

        card = self.cards[card_id]
        if front:
            card['front'] = front
        if back:
            card['back'] = back
        
        card['updated_at'] = datetime.now().isoformat()
        self._save_card(card_id)
        
        # Update deck's updated_at timestamp
        deck_id = card['deck_id']
        self.decks[deck_id]['updated_at'] = datetime.now().isoformat()
        self._save_deck(deck_id)
        
        return card

    def record_review(self, card_id: str, is_correct: bool) -> Optional[Dict]:
        """Record a review attempt for a card"""
        if card_id not in self.cards:
            return None

        card = self.cards[card_id]
        card['stats']['attempts'] += 1
        if is_correct:
            card['stats']['correct'] += 1
        card['stats']['last_reviewed'] = datetime.now().isoformat()
        
        self._save_card(card_id)
        return card

    def _save_deck(self, deck_id: str):
        """Save deck data to file"""
        deck_file = self.storage_path / f'deck_{deck_id}.json'
        with open(deck_file, 'w') as f:
            json.dump(self.decks[deck_id], f)

    def _save_card(self, card_id: str):
        """Save card data to file"""
        card_file = self.storage_path / f'card_{card_id}.json'
        with open(card_file, 'w') as f:
            json.dump(self.cards[card_id], f)

    def export_deck(self, deck_id: str, format: str = 'json') -> Optional[str]:
        """Export a deck in various formats"""
        if deck_id not in self.decks:
            return None

        deck = self.decks[deck_id]
        cards = self.get_cards_in_deck(deck_id)

        if format == 'json':
            return json.dumps({
                'deck': deck,
                'cards': cards
            })
        elif format == 'txt':
            content = f"Flashcard Deck: {deck['title']}\n\n"
            for i, card in enumerate(cards, 1):
                content += f"Card {i}:\nFront: {card['front']}\nBack: {card['back']}\n\n"
            return content
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Initialize the flashcard manager
flashcard_manager = FlashcardManager()

# API Routes

@flashcards_bp.route('/api/flashcards/decks', methods=['POST'])
def create_deck():
    """Create a new flashcard deck"""
    try:
        data = request.json
        title = data.get('title')
        description = data.get('description', '')

        if not title:
            return jsonify({"error": "Title is required"}), 400

        deck = flashcard_manager.create_deck(title, description)
        return jsonify(deck), 201

    except Exception as e:
        logger.error(f"Error in create_deck: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/decks/<string:deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get a flashcard deck by ID"""
    try:
        deck = flashcard_manager.get_deck(deck_id)
        if not deck:
            return jsonify({"error": "Deck not found"}), 404
            
        return jsonify(deck), 200

    except Exception as e:
        logger.error(f"Error in get_deck: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/decks/<string:deck_id>/cards', methods=['GET'])
def get_deck_cards(deck_id):
    """Get all cards in a deck"""
    try:
        cards = flashcard_manager.get_cards_in_deck(deck_id)
        return jsonify(cards), 200

    except Exception as e:
        logger.error(f"Error in get_deck_cards: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/cards', methods=['POST'])
def create_card():
    """Create a new flashcard in a deck"""
    try:
        data = request.json
        deck_id = data.get('deck_id')
        front = data.get('front')
        back = data.get('back')

        if not all([deck_id, front, back]):
            return jsonify({"error": "deck_id, front and back are required"}), 400

        card = flashcard_manager.create_card(deck_id, front, back)
        return jsonify(card), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error in create_card: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/cards/<string:card_id>', methods=['PUT'])
def update_card(card_id):
    """Update an existing flashcard"""
    try:
        data = request.json
        front = data.get('front')
        back = data.get('back')

        if not any([front, back]):
            return jsonify({"error": "At least one of front or back must be provided"}), 400

        card = flashcard_manager.update_card(card_id, front, back)
        if not card:
            return jsonify({"error": "Card not found"}), 404
            
        return jsonify(card), 200

    except Exception as e:
        logger.error(f"Error in update_card: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/cards/<string:card_id>/review', methods=['POST'])
def record_card_review(card_id):
    """Record a review session for a card"""
    try:
        data = request.json
        is_correct = data.get('is_correct')

        if not isinstance(is_correct, bool):
            return jsonify({"error": "is_correct (boolean) is required"}), 400

        card = flashcard_manager.record_review(card_id, is_correct)
        if not card:
            return jsonify({"error": "Card not found"}), 404
            
        return jsonify(card), 200

    except Exception as e:
        logger.error(f"Error in record_card_review: {str(e)}")
        return jsonify({"error": str(e)}), 500

@flashcards_bp.route('/api/flashcards/decks/<string:deck_id>/export', methods=['GET'])
def export_deck(deck_id):
    """Export a deck in different formats"""
    try:
        export_format = request.args.get('format', 'json')
        
        if export_format not in ('json', 'txt'):
            return jsonify({"error": "Supported formats: json, txt"}), 400

        exported_data = flashcard_manager.export_deck(deck_id, export_format)
        if not exported_data:
            return jsonify({"error": "Deck not found"}), 404

        if export_format == 'json':
            return jsonify(json.loads(exported_data)), 200
        else:
            return exported_data, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        logger.error(f"Error in export_deck: {str(e)}")
        return jsonify({"error": str(e)}), 500
