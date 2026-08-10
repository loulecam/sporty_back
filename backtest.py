from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import json
import time
import cv2
from curl_analysis import check_curl_biceps, check_squat
from flask_socketio import SocketIO


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

socketio = SocketIO(app, cors_allowed_origins="*")

nbr_curl_biceps_done = 0


# Create directory to store received frames if it doesn't exist
if not os.path.exists('received_frames'):
    os.makedirs('received_frames')

# Endpoint for frame analysis (existing functionality)
'''@app.route('/frame-analysis', methods=['POST'])
@cross_origin()
def frame_analysis():
    print(request.files)
    if 'frame' not in request.files:
        return jsonify({'error': 'No frame provided'}), 400

    frame = request.files['frame']
    #print(f"Received frame: {frame.filename}")
    
    temp_path = os.path.join('received_frames', frame.filename)
    frame.save(temp_path)

    
    try:

        biceps_done = check_curl_biceps(temp_path)
        print(biceps_done)
        if(biceps_done):
            nbr_curl_biceps_done = nbr_curl_biceps_done + 1
            print("Nombre de curl biceps effectués :", nbr_curl_biceps_done)
            socketio.emit('biceps_update', {'nbr_curl_biceps_done': nbr_curl_biceps_done})
        os.remove(temp_path)

        return jsonify({'message': 'Frame processed successfully!'}), 200
    except Exception as e:

        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500
'''
@socketio.on('connect')
def handle_connect():
    print("Client connecté")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client déconnecté")

@socketio.on('frame')
def handle_frame(data):
    """
    Gestion d'une image envoyée par le front.
    """
    global nbr_curl_biceps_done

    try:
        # Sauvegarder l'image temporairement
        file_name = f"frame_{int(time.time())}.jpeg"
        file_path = os.path.join('received_frames', file_name)
        
        with open(file_path, 'wb') as f:
            f.write(data)  # Écrire le contenu binaire dans un fichier

        # Analyse de l'image
        biceps_done = check_curl_biceps(file_path)
        if biceps_done:
            nbr_curl_biceps_done += 1
            print(f"Nombre de curls détectés : {nbr_curl_biceps_done}")
            # Envoyer la mise à jour au front
            socketio.emit('biceps_update', {'nbr_curl_biceps_done': nbr_curl_biceps_done})

        # Nettoyage du fichier temporaire
        os.remove(file_path)

    except Exception as e:
        print(f"Erreur lors du traitement de l'image : {e}")





@socketio.on('squat_frame')
def handle_squat_frame(data):
    """
    Gestion d'une image envoyée par le front.
    """
    global nbr_squat_done

    try:
        # Sauvegarder l'image temporairement
        file_name = f"frame_{int(time.time())}.jpeg"
        file_path = os.path.join('received_frames', file_name)
        
        with open(file_path, 'wb') as f:
            f.write(data)  # Écrire le contenu binaire dans un fichier

        # Analyse de l'image
        squat_done = check_squat(file_path)
        if squat_done:
            nbr_squat_done += 1
            print(f"Nombre de squats détectés : {nbr_squat_done}")
            # Envoyer la mise à jour au front
            socketio.emit('squat_update', {'nbr_squat_done': nbr_squat_done})

        # Nettoyage du fichier temporaire
        os.remove(file_path)

    except Exception as e:
        print(f"Erreur lors du traitement de l'image : {e}")




# Endpoint for login
@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()

    # Vérifiez que les champs email et password sont présents dans la requête
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email']
    password = data['password']

    # Charger le fichier JSON avec les identifiants d'utilisateurs
    try:
        with open('admin.json', 'r') as file:
            users_data = json.load(file)
    except FileNotFoundError:
        return jsonify({'error': 'User database not found'}), 500

    # Vérifier si les identifiants correspondent à un utilisateur dans le fichier JSON
    for user in users_data.get('users', []):
        if user['email'] == email and user['password'] == password:
            return jsonify({'message': 'Login successful'}), 200

    # Si aucun utilisateur ne correspond, renvoyer une erreur
    return jsonify({'error': 'Invalid email or password'}), 401



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
