"""
===========================================
TMY Quiz Maker - Serveur WebSocket Central
===========================================
"""

from flask import Flask
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire des salons actifs : { "PIN": {"title": str, "players": [str]} }
active_lobbies = {}

@socketio.on('connect')
def handle_connect():
    print("🟢 Un client s'est connecté au serveur.")

@socketio.on('disconnect')
def handle_disconnect():
    print("🔴 Un client s'est déconnecté du serveur.")

@socketio.on('create_room')
def handle_create_room(data):
    pin = data.get('pin', '').replace(" ", "")
    title = data.get('title', 'Mon Quiz')
    
    active_lobbies[pin] = {
        "title": title,
        "players": []
    }
    join_room(pin)
    print(f"🎮 Salon créé : PIN [{pin}] | Titre : {title}")
    emit('room_created', {'success': True, 'pin': pin})

@socketio.on('join_room')
def handle_join_room(data):
    pin = data.get('pin', '').replace(" ", "")
    player_name = data.get('name', '').strip()

    if pin in active_lobbies:
        if player_name not in active_lobbies[pin]["players"]:
            active_lobbies[pin]["players"].append(player_name)
        
        join_room(pin)
        
        # 1. Confirmer à l'élève
        emit('join_response', {'success': True, 'pin': pin, 'title': active_lobbies[pin]["title"]})
        
        # 2. Prévenir le salon (prof et camarades)
        emit('player_joined', {'name': player_name, 'players': active_lobbies[pin]["players"]}, to=pin)
        print(f"✅ '{player_name}' a rejoint le salon [{pin}]")
    else:
        emit('join_response', {'success': False, 'message': f"❌ Salle introuvable pour le PIN '{pin}'."})
        print(f"❌ Échec : PIN [{pin}] inexistant.")

# ========================================================
# 🚀 DÉMARRAGE DU QUIZ ET TRANSMISSION DES QUESTIONS AUX ÉLÈVES
# ========================================================
@socketio.on('start_quiz')
def handle_start_quiz(data):
    pin = data.get('pin', '').replace(" ", "")
    questions = data.get('questions', [])

    print(f"🚀 Lancement du quiz pour le salon [{pin}] avec {len(questions)} questions")

    # Émettre l'ordre de lancement à TOUS les élèves dans le salon avec les questions
    emit('quiz_started', {'pin': pin, 'questions': questions}, to=pin)

# ========================================================
# 📊 MISE À JOUR DU CLASSEMENT HÔTE EN TEMPS RÉEL
# ========================================================
@socketio.on('update_score')
def handle_update_score(data):
    pin = data.get('pin', '').replace(" ", "")
    # Transmettre les résultats des élèves au tableau de bord de l'hôte
    emit('leaderboard_update', data, to=pin)

if __name__ == '__main__':
    print("🚀 Serveur TMY Quiz Maker démarré sur http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)