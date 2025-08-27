from flask import Blueprint, render_template

# 1. Create the main application Blueprint.
# It will use the 'templates' and 'static' folders from the main app directory ('chatbot/').
main_bp = Blueprint('main', 
                    __name__,
                    template_folder='../templates',
                    static_folder='../static')


@main_bp.route('/')
def index():
    """Serves the main homepage (index.html)."""
    return render_template('index.html')


@main_bp.route('/agent-chat/<session_id>')
def agent_chat_page(session_id):
    """Serves the dedicated chat page for support agents."""
    return render_template('agent_chat.html', session_id=session_id)