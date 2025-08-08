from flask import Blueprint, request, jsonify
import requests
import logging
from collections import deque
from datetime import datetime
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask Blueprint
doubts_bp = Blueprint('doubts', __name__)

# Ollama configuration
OLLAMA_HOST = 'http://localhost:11434'
OLLAMA_MODEL = 'llama3'  # Change this if using a different model

class DoubtResolver:
    def __init__(self):
        self.conversation_contexts = {}  # {user_id: context}
        self.message_history_limit = 8
        self.timeout = 120  # Timeout in seconds
        
    def _call_ollama(self, prompt: str, conversation_history: list = None) -> str:
        """Make API call to local Ollama instance"""
        try:
            messages = self._format_messages(prompt, conversation_history)
            
            response = requests.post(
                f'{OLLAMA_HOST}/api/chat',
                json={
                    'model': OLLAMA_MODEL,
                    'messages': messages,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_ctx': 4096  # Context window size
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.text}")
                return "Sorry, I'm having trouble responding right now."
                
            return response.json()['message']['content']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {str(e)}")
            return "Connection to AI service failed."
    
    def _format_messages(self, prompt: str, history: list) -> list:
        """Format messages for Ollama API"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert tutor helping students with academic doubts. "
                          "Provide clear, detailed explanations with examples. "
                          "If you don't know something, say so."
            }
        ]
        
        if history:
            messages.extend(history[-self.message_history_limit:])
            
        messages.append({"role": "user", "content": prompt})
        return messages
    
    def resolve_doubt(self, user_id: str, question: str) -> dict:
        """Resolve a student's doubt using Llama3"""
        try:
            # Get or create conversation context
            if user_id not in self.conversation_contexts:
                self.conversation_contexts[user_id] = {
                    'history': deque(maxlen=self.message_history_limit),
                    'document_context': None
                }
                
            context = self.conversation_contexts[user_id]
            
            # Get response from Ollama
            answer = self._call_ollama(question, list(context['history']))
            
            # Update conversation history
            context['history'].append({"user": question, "assistant": answer})
            
            return {
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error resolving doubt: {str(e)}")
            return {"answer": "An error occurred while processing your request", "timestamp": datetime.now().isoformat()}

# Initialize the doubt resolver
doubt_resolver = DoubtResolver()

# API Routes
@doubts_bp.route('/api/doubts/ask', methods=['POST'])
def ask_doubt():
    """Endpoint to ask a doubt and get an AI-generated answer"""
    try:
        data = request.json
        user_id = data.get('user_id')
        question = data.get('question')
        
        if not user_id or not question:
            return jsonify({"error": "user_id and question are required"}), 400
            
        result = doubt_resolver.resolve_doubt(user_id, question)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in ask_doubt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@doubts_bp.route('/api/doubts/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history for a user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
            
        if user_id not in doubt_resolver.conversation_contexts:
            return jsonify({"history": []}), 200
            
        history = list(doubt_resolver.conversation_contexts[user_id]['history'])
        return jsonify({"history": history}), 200
        
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@doubts_bp.route('/api/doubts/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a user"""
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
            
        if user_id in doubt_resolver.conversation_contexts:
            doubt_resolver.conversation_contexts[user_id]['history'].clear()
            
        return jsonify({"status": "conversation cleared"}), 200
        
    except Exception as e:
        logger.error(f"Error in clear_conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

