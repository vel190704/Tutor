# /app/api/routes_diagrams.py

import os
from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from networkx import is_path
from app.models.diagrams import Diagram
from app.services.diagram_creator import generate_mermaid_code, render_diagram_image
from app.utils.file_handlers import save_diagram_file
from app.utils.export_tools import export_as_svg, export_as_png
import json
import uuid

diagrams_bp = Blueprint('diagrams', __name__)
db = SQLAlchemy()

@diagrams_bp.route('/api/diagrams/generate', methods=['POST'])
def generate_diagram():
    """
    Generate diagram from text content
    Expects JSON payload with:
    - content: text to convert to diagram
    - diagram_type: flowchart/mindmap/sequence/etc.
    - style: optional styling preferences
    """
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
            
        diagram_type = data.get('diagram_type', 'flowchart')
        style = data.get('style', {})
        
        # Generate Mermaid code
        mermaid_code = generate_mermaid_code(
            data['content'],
            diagram_type,
            style
        )
        
        # Render diagram image
        image_data = render_diagram_image(mermaid_code)
        
        # Create diagram record
        diagram_id = str(uuid.uuid4())
        new_diagram = Diagram(
            id=diagram_id,
            mermaid_code=mermaid_code,
            diagram_type=diagram_type,
            style=json.dumps(style),
            image_data=image_data
        )
        db.session.add(new_diagram)
        db.session.commit()
        
        # Save to filesystem
        file_path = save_diagram_file(diagram_id, image_data)
        
        return jsonify({
            "diagram_id": diagram_id,
            "mermaid_code": mermaid_code,
            "image_url": f"/diagrams/{diagram_id}.svg",
            "file_path": file_path
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@diagrams_bp.route('/api/diagrams/<diagram_id>', methods=['GET'])
def get_diagram(diagram_id):
    """Get diagram by ID"""
    diagram = Diagram.query.get(diagram_id)
    if not diagram:
        return jsonify({"error": "Diagram not found"}), 404
        
    return jsonify({
        "diagram_id": diagram.id,
        "mermaid_code": diagram.mermaid_code,
        "diagram_type": diagram.diagram_type,
        "created_at": diagram.created_at,
        "image_url": f"/diagrams/{diagram.id}.svg",
        "style": json.loads(diagram.style) if diagram.style else {}
    }), 200

@diagrams_bp.route('/api/diagrams/<diagram_id>/render', methods=['GET'])
def render_diagram(diagram_id):
    """Get rendered diagram image"""
    format = request.args.get('format', 'svg')
    
    diagram = Diagram.query.get(diagram_id)
    if not diagram:
        return jsonify({"error": "Diagram not found"}), 404
        
    try:
        if format == 'svg':
            return export_as_svg(diagram.mermaid_code)
        elif format == 'png':
            return export_as_png(diagram.mermaid_code)
        else:
            return jsonify({"error": "Invalid format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diagrams_bp.route('/api/diagrams/<diagram_id>/update', methods=['PUT'])
def update_diagram(diagram_id):
    """Update diagram code and regenerate image"""
    try:
        data = request.get_json()
        diagram = Diagram.query.get(diagram_id)
        if not diagram:
            return jsonify({"error": "Diagram not found"}), 404
            
        if 'mermaid_code' in data:
            diagram.mermaid_code = data['mermaid_code']
        
        if 'style' in data:
            diagram.style = json.dumps(data['style'])
            
        # Regenerate image
        diagram.image_data = render_diagram_image(diagram.mermaid_code)
        db.session.commit()
        
        # Update filesystem
        save_diagram_file(diagram_id, diagram.image_data)
        
        return jsonify({
            "message": "Diagram updated successfully",
            "image_url": f"/diagrams/{diagram_id}.svg"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@diagrams_bp.route('/api/diagrams/<diagram_id>/animate', methods=['POST'])
def animate_diagram(diagram_id):
    """Convert diagram to animated sequence"""
    try:
        data = request.get_json()
        steps = data.get('steps', [])
        
        diagram = Diagram.query.get(diagram_id)
        if not diagram:
            return jsonify({"error": "Diagram not found"}), 404
            
        # Convert steps to Mermaid sequence
        animated_code = convert_to_sequence_diagram(diagram.mermaid_code, steps)
        
        return jsonify({
            "animated_code": animated_code,
            "preview_url": f"/diagrams/{diagram_id}/animate.svg"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def convert_to_sequence_diagram(base_code, steps):
    """Helper to convert base diagram to animated sequence"""
    # Implementation would depend on your specific animation requirements
    return base_code  # Placeholder

@diagrams_bp.route('/api/diagrams/<diagram_id>/export', methods=['GET'])
def export_diagram(diagram_id):
    """Export diagram in various formats"""
    format = request.args.get('format', 'svg')
    diagram = Diagram.query.get(diagram_id)
    if not diagram:
        return jsonify({"error": "Diagram not found"}), 404
        
    try:
        if format == 'svg':
            return export_as_svg(diagram.mermaid_code)
        elif format == 'png':
            return export_as_png(diagram.mermaid_code)
        elif format == 'mmd':
            return diagram.mermaid_code, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename={diagram_id}.mmd'
            }
        else:
            return jsonify({"error": "Invalid format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register blueprint in your main application file:
# from app.api.routes_diagrams import diagrams_bp
# app.register_blueprint(diagrams_bp)
        response_data = {
            'status': 'success',
            'filename': filename,
            'file_path': file_path,
            'metadata': meta_data,
            'content': text_content,
            'images': []
        }
        return jsonify(response_data), 201
    except Exception as e:
        current_app.logger.error(f"Error processing PDF file: {e}")
        if os.path.exists(is_path):
            os.remove(is_path)
        return jsonify({'error': 'Unexpected error occurred', 'details': str(e)}), 500  