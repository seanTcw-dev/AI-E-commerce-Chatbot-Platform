# chatbot/routes/studio_routes.py
import os
from flask import Blueprint, render_template

# --- Path Configuration ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
studio_template_folder = os.path.join(project_root, 'beauty-companion-studio', 'templates')
studio_static_folder = os.path.join(project_root, 'beauty-companion-studio', 'static')
# Create the Studio Blueprint
studio_bp = Blueprint('studio', 
                      __name__,
                      template_folder=studio_template_folder,
                      static_folder=studio_static_folder,
                      url_prefix='/studio')

@studio_bp.route('/')
def studio_page():
    """Serves the main studio page."""
    return render_template('studio.html')