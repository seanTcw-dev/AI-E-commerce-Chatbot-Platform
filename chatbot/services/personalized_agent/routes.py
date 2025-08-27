from flask import Blueprint, jsonify, request, render_template
from .agent_manager import PersonalizedAgentManager

personalized_agent_bp = Blueprint(
    'personalized_agent_bp',
    __name__,
    template_folder='../../templates', # Access templates from the root 'templates' folder
    static_folder='../../static' # Access static from the root 'static' folder
)

agent_manager = PersonalizedAgentManager()

@personalized_agent_bp.route('/beauty_companion')
def beauty_companion_page():
    """Render the main page for managing Beauty Companions."""
    return render_template('beauty_companion.html')

@personalized_agent_bp.route('/api/companion/profiles', methods=['GET'])
def get_profiles():
    """API endpoint to get all companion profiles."""
    profiles = agent_manager.get_all_profiles()
    return jsonify(profiles)

@personalized_agent_bp.route('/api/companion/profiles', methods=['POST'])
def create_profile():
    """API endpoint to create a new companion profile."""
    profile_data = request.json
    if not profile_data or 'name' not in profile_data:
        return jsonify({"error": "Name is required"}), 400
    
    new_profile = agent_manager.create_profile(profile_data)
    return jsonify(new_profile), 201

@personalized_agent_bp.route('/api/companion/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """API endpoint to get a specific profile by ID."""
    profile = agent_manager.get_profile(profile_id)
    if profile:
        return jsonify(profile)
    return jsonify({"error": "Profile not found"}), 404

@personalized_agent_bp.route('/api/companion/profiles/<profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """API endpoint to update a companion profile."""
    update_data = request.json
    updated_profile = agent_manager.update_profile(profile_id, update_data)
    if updated_profile:
        return jsonify(updated_profile)
    return jsonify({"error": "Profile not found"}), 404

@personalized_agent_bp.route('/api/companion/profiles/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """API endpoint to delete a companion profile."""
    if agent_manager.delete_profile(profile_id):
        return jsonify({"message": "Profile deleted"}), 200
    return jsonify({"error": "Profile not found or cannot be deleted"}), 404
