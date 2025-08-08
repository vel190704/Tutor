from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import List, Dict

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask Blueprint
mcq_bp = Blueprint('mcq', __name__)

class MCQManager:
    def __init__(self):
        self.mcqs = []  # List to store MCQs
        self.mcq_id_counter = 1  # Simple counter for MCQ IDs

    def create_mcq(self, question: str, options: List[str], correct_option: int) -> Dict:
        """Create a new MCQ"""
        mcq = {
            'id': self.mcq_id_counter,
            'question': question,
            'options': options,
            'correct_option': correct_option,
            'created_at': datetime.now().isoformat()
        }
        self.mcqs.append(mcq)
        self.mcq_id_counter += 1
        return mcq

    def get_mcq(self, mcq_id: int) -> Dict:
        """Retrieve an MCQ by ID"""
        for mcq in self.mcqs:
            if mcq['id'] == mcq_id:
                return mcq
        return None

    def get_all_mcqs(self) -> List[Dict]:
        """Retrieve all MCQs"""
        return self.mcqs

    def check_answer(self, mcq_id: int, selected_option: int) -> bool:
        """Check if the selected answer is correct"""
        mcq = self.get_mcq(mcq_id)
        if mcq and 0 <= selected_option < len(mcq['options']):
            return mcq['correct_option'] == selected_option
        return False

# Initialize the MCQ manager
mcq_manager = MCQManager()

# API Routes

@mcq_bp.route('/api/mcq/create', methods=['POST'])
def create_mcq():
    """Endpoint to create a new MCQ"""
    try:
        data = request.json
        question = data.get('question')
        options = data.get('options')
        correct_option = data.get('correct_option')

        if not question or not options or correct_option is None:
            return jsonify({"error": "Question, options, and correct_option are required"}), 400

        if not (0 <= correct_option < len(options)):
            return jsonify({"error": "correct_option must be a valid index"}), 400

        mcq = mcq_manager.create_mcq(question, options, correct_option)
        return jsonify(mcq), 201

    except Exception as e:
        logger.error(f"Error in create_mcq: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcq_bp.route('/api/mcq/<int:mcq_id>', methods=['GET'])
def get_mcq(mcq_id: int):
    """Endpoint to retrieve an MCQ by ID"""
    try:
        mcq = mcq_manager.get_mcq(mcq_id)
        if mcq is None:
            return jsonify({"error": "MCQ not found"}), 404
        return jsonify(mcq), 200

    except Exception as e:
        logger.error(f"Error in get_mcq: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcq_bp.route('/api/mcq', methods=['GET'])
def get_all_mcqs():
    """Endpoint to retrieve all MCQs"""
    try:
        mcqs = mcq_manager.get_all_mcqs()
        return jsonify(mcqs), 200

    except Exception as e:
        logger.error(f"Error in get_all_mcqs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@mcq_bp.route('/api/mcq/<int:mcq_id>/answer', methods=['POST'])
def answer_mcq(mcq_id: int):
    """Endpoint to check the answer for an MCQ"""
    try:
        data = request.json
        selected_option = data.get('selected_option')

        if selected_option is None:
            return jsonify({"error": "selected_option is required"}), 400

        is_correct = mcq_manager.check_answer(mcq_id, selected_option)
        return jsonify({"is_correct": is_correct}), 200

    except Exception as e:
        logger.error(f"Error in answer_mcq: {str(e)}")
        return jsonify({"error": str(e)}), 500
from app.models.user import User
from app.utils.ai_helpers import get_recommendations_for_user   