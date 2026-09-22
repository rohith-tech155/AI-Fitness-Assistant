import os
import json
from flask import Flask, request, jsonify, send_from_directory
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from dotenv import load_dotenv

from database import (
    init_db, register_user, login_user,
    add_progress, get_progress_history,
    save_workout, get_user_workouts,
    save_chat_message, get_chat_history
)
from chatbot import generate_ai_response
from workout import generate_workout_routine

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-fitness-secret')

if HAS_CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        return response


# Initialize Database on launch
init_db()

# Serve Frontend Pages & Static Files
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_frontend_files(filename):
    if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return send_from_directory(FRONTEND_DIR, filename)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# ================= AUTHENTICATION ENDPOINTS =================
@app.route('/api/register', methods=['POST'])
def handle_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    result = register_user(username, email, password)
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.get_json() or {}
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username/Email and Password required.'}), 400

    result = login_user(username_or_email, password)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 401

# ================= CHATBOT ENDPOINTS =================
@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    user_id = data.get('user_id', 1)
    image_data = data.get('image_data', None)
    file_name = data.get('file_name', None)

    if not message and not image_data and not file_name:
        return jsonify({'success': False, 'message': 'Message or file attachment required.'}), 400

    # Format history message for user
    log_text = message
    if file_name and not message:
        log_text = f"📎 [Uploaded file: {file_name}]"
    elif file_name:
        log_text = f"📎 [{file_name}] {message}"
    elif image_data and not message:
        log_text = "📷 [Sent photo snapshot]"

    # Save user message
    save_chat_message(user_id, 'user', log_text)

    # Get AI response (supports multimodal Gemini 1.5 Flash + fallback)
    reply = generate_ai_response(message, image_data=image_data, file_name=file_name)

    # Save bot message
    save_chat_message(user_id, 'bot', reply)

    return jsonify({'success': True, 'reply': reply}), 200

@app.route('/api/chat/history', methods=['GET'])
def handle_chat_history():
    user_id = request.args.get('user_id', 1, type=int)
    history = get_chat_history(user_id)
    return jsonify({'success': True, 'history': history}), 200

# ================= WORKOUT ENDPOINTS =================
@app.route('/api/workout/generate', methods=['POST'])
def handle_generate_workout():
    data = request.get_json() or {}
    goal = data.get('goal', 'Muscle Gain')
    level = data.get('level', 'Beginner')
    user_id = data.get('user_id', 1)

    routine = generate_workout_routine(goal, level)
    
    # Save workout routine to database
    save_workout(
        user_id=user_id,
        goal=goal,
        level=level,
        title=routine.get('title', f'{goal} Routine'),
        routine_json=json.dumps(routine)
    )

    return jsonify({'success': True, 'routine': routine}), 200

@app.route('/api/workouts', methods=['GET'])
def handle_get_workouts():
    user_id = request.args.get('user_id', 1, type=int)
    workouts = get_user_workouts(user_id)
    # Parse json routines
    for w in workouts:
        try:
            w['routine'] = json.loads(w['routine_json'])
        except Exception:
            w['routine'] = {}
    return jsonify({'success': True, 'workouts': workouts}), 200

# ================= PROGRESS ENDPOINTS =================
@app.route('/api/progress', methods=['GET', 'POST'])
def handle_progress():
    if request.method == 'POST':
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        weight = data.get('weight')
        date = data.get('date')
        notes = data.get('notes', '')

        if not weight or not date:
            return jsonify({'success': False, 'message': 'Weight and Date are required.'}), 400

        res = add_progress(user_id, float(weight), str(date), notes)
        return jsonify(res), 201

    # GET Request
    user_id = request.args.get('user_id', 1, type=int)
    records = get_progress_history(user_id)
    return jsonify({'success': True, 'records': records}), 200

# Server status endpoint
@app.route('/api/status', methods=['GET'])
def handle_status():
    return jsonify({
        'status': 'online',
        'app': 'AI Fitness Assistant API',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 AI Fitness Assistant server starting on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
