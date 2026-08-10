import cv2
import os
import cv2
import mediapipe as mp
import os
import numpy as np

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')


# Initialiser MediaPipe Pose et Drawing
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Liste des noms des points clés (PoseLandmark)
landmark_names = {
    mp_pose.PoseLandmark.NOSE: "Nez",
    mp_pose.PoseLandmark.LEFT_EYE_INNER: "Oeil gauche (interieur)",
    mp_pose.PoseLandmark.LEFT_EYE: "Oeil gauche",
    mp_pose.PoseLandmark.LEFT_EYE_OUTER: "Oeil gauche (exterieur)",
    mp_pose.PoseLandmark.RIGHT_EYE_INNER: "Oeil droit (interieur)",
    mp_pose.PoseLandmark.RIGHT_EYE: "Oeil droit",
    mp_pose.PoseLandmark.RIGHT_EYE_OUTER: "Oeil droit (exterieur)",
    mp_pose.PoseLandmark.LEFT_EAR: "Oreille gauche",
    mp_pose.PoseLandmark.RIGHT_EAR: "Oreille droite",
    mp_pose.PoseLandmark.MOUTH_LEFT: "Coin de la bouche gauche",
    mp_pose.PoseLandmark.MOUTH_RIGHT: "Coin de la bouche droite",
    mp_pose.PoseLandmark.LEFT_SHOULDER: "Epaule gauche",
    mp_pose.PoseLandmark.RIGHT_SHOULDER: "Epaule droite",
    mp_pose.PoseLandmark.LEFT_ELBOW: "Coude gauche",
    mp_pose.PoseLandmark.RIGHT_ELBOW: "Coude droit",
    mp_pose.PoseLandmark.LEFT_WRIST: "Poignet gauche",
    mp_pose.PoseLandmark.RIGHT_WRIST: "Poignet droit",
    mp_pose.PoseLandmark.LEFT_HIP: "Hanche gauche",
    mp_pose.PoseLandmark.RIGHT_HIP: "Hanche droite",
    mp_pose.PoseLandmark.LEFT_KNEE: "Genou gauche",
    mp_pose.PoseLandmark.RIGHT_KNEE: "Genou droit",
    mp_pose.PoseLandmark.LEFT_ANKLE: "Cheville gauche",
    mp_pose.PoseLandmark.RIGHT_ANKLE: "Cheville droite",
    mp_pose.PoseLandmark.LEFT_FOOT_INDEX: "Orteil gauche",
    mp_pose.PoseLandmark.RIGHT_FOOT_INDEX: "Orteil droit"
}

def load_image(image_path):
    """Charge une image depuis un chemin spécifié et la convertit en RGB."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Erreur : impossible de charger l'image {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), image

def detect_pose(image_rgb):
    """Détecte les poses humaines sur une image en utilisant MediaPipe."""
    with mp_pose.Pose() as pose:
        return pose.process(image_rgb)

def annotate_image(image, results):
    """Ajoute des points clés et des labels sur l'image en fonction des résultats de la détection."""
    if results.pose_landmarks:
        h, w, _ = image.shape
        # Dessiner les points clés
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Ajouter les labels à côté des points
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            x, y = int(landmark.x * w), int(landmark.y * h)
            if mp_pose.PoseLandmark(idx) in landmark_names:
                label = landmark_names[mp_pose.PoseLandmark(idx)]
                cv2.putText(image, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
    return image

def extract_landmarks(results, image):
    """Extrait les coordonnées des points clés sous forme de dictionnaire {partie_du_corps: {x, y}}."""
    landmarks_dict = {}
    if results.pose_landmarks:
        h, w, _ = image.shape
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            if mp_pose.PoseLandmark(idx) in landmark_names:
                part_name = landmark_names[mp_pose.PoseLandmark(idx)]
                landmarks_dict[part_name] = {"x": landmark.x * w, "y": landmark.y * h}
    return landmarks_dict

def save_image(image, output_path):
    """Enregistre l'image annotée à l'emplacement spécifié."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, image)

def process_and_save_pose_image(image_path, output_path, save_images=True):
    """Pipeline complet pour charger, traiter, annoter et sauvegarder une image avec la reconnaissance de poses.
       Renvoie également un dictionnaire avec les coordonnées des points clés."""
    image_rgb, image = load_image(image_path)
    results = detect_pose(image_rgb)
    landmarks_dict = extract_landmarks(results, image)
    
    if save_images:
        annotated_image = annotate_image(image, results)
        save_image(annotated_image, output_path)

    return landmarks_dict

def process_images_in_folder(input_folder, output_folder, save_images=True):
    """Applique la fonction process_and_save_pose_image à toutes les images d'un dossier.
       Retourne un tableau de dictionnaires contenant les points clés pour chaque image."""
    landmarks_list = []
    
    # Parcourir tous les fichiers du dossier
    for filename in os.listdir(input_folder):
        # Vérifier si le fichier est une image (tu peux étendre cette liste à d'autres formats si nécessaire)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
                        
            # Appliquer la fonction process_and_save_pose_image à chaque image et récupérer les landmarks
            try:
                landmarks_dict = process_and_save_pose_image(input_path, output_path, save_images)
                landmarks_list.append(landmarks_dict)
            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {e}")
    
    return landmarks_list











def afficher_positions(landmarks_dict):
    """Affiche les coordonnées (x, y) de chaque partie du corps dans le dictionnaire."""
    for part, coordinates in landmarks_dict.items():
        x = coordinates['x']
        y = coordinates['y']
        print(f"{part}: x = {x:.2f}, y = {y:.2f}")


def calculate_angle(p1, p2, p3):     
    a = np.array([p1['x'], p1['y']])
    b = np.array([p2['x'], p2['y']])
    c = np.array([p3['x'], p3['y']])
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    
    angle = np.degrees(angle)
    return angle


interval_time_ms = 200  # Temps en millisecondes entre chaque frame

def calculate_angle_speed(angle1, angle2, step):
    angle_speed = (angle2 - angle1) / step
    return angle_speed





nbr_curl_biceps_done = 0
number_of_frames_checked = 0
interval_time_ms = 200  # Temps en millisecondes entre chaque frame
move_state = -1

def check_curl_biceps(frame):
    global nbr_curl_biceps_done
    global number_of_frames_checked
    global move_state

    pos = process_and_save_pose_image(frame, "", save_images=False)
    angle_droit = calculate_angle(pos['Poignet droit'], pos['Coude droit'], pos['Epaule droite'])
    angle_gauche = calculate_angle(pos['Poignet gauche'], pos['Coude gauche'], pos['Epaule gauche'])
    number_of_frames_checked += 1

    if move_state == -1:  
        if angle_droit > 150 and angle_gauche > 150:
            move_state = 0 
        return

    if move_state == 0:
        if angle_droit < 30 and angle_gauche < 30: 
            move_state = 1
        return

    elif move_state == 1:
        if angle_droit > 150 and angle_gauche > 150:
            if number_of_frames_checked * interval_time_ms > 1500:
                nbr_curl_biceps_done += 1  

            move_state = 0
            number_of_frames_checked = 0





# Il faut faire essayer de faire attention au temps que prend l'exécution de la fonction check_curl_biceps
nbr_curl_biceps_done = 0
nbr_frames = 78
for i in range(nbr_frames):
    img_path = './video/lou/frame_' + str(i+1) + '.jpg'
    check_curl_biceps(img_path)
    print("Frame", i)
    print("Nombre de curl biceps effectués :", nbr_curl_biceps_done)
    print()