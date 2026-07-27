"""
===========================================
TMY Quiz Maker - Serveur WebSocket Central
===========================================
"""

from flask import Flask
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionnaire des salons actifs :
# { "PIN": {"title": str, "players": [str], "questions": [], "current_question": 0, "teacher_name": str} }
active_lobbies = {}

def build_leaderboard(lobby):
    """Construit le classement en incluant TOUS les joueurs de la salle,
    même ceux qui n'ont pas encore répondu (score 0 par défaut)."""
    scores = lobby.get("scores", {})
    noms = list(lobby.get("players", []))

    for nom_deja_note in scores.keys():
        if nom_deja_note not in noms:
            noms.append(nom_deja_note)

    classement = sorted(
        [{"name": n, "score": scores.get(n, 0)} for n in noms],
        key=lambda p: p["score"],
        reverse=True
    )
    return classement

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
        "players": [],
        "questions": [],
        "current_question": 0,
        "teacher_name": "Professeur"
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
# 🚀 DÉMARRAGE DU QUIZ ET TRANSMISSION DE LA 1ÈRE QUESTION
# ========================================================
@socketio.on('start_quiz')
def handle_start_quiz(data):
    pin = data.get('pin', '').replace(" ", "")
    questions = data.get('questions', [])
    teacher_name = data.get('teacher_name', 'Professeur')
    title = data.get('title', 'Mon Quiz')

    if pin in active_lobbies:
        active_lobbies[pin]["questions"] = questions
        active_lobbies[pin]["current_question"] = 0
        active_lobbies[pin]["teacher_name"] = teacher_name
        active_lobbies[pin]["title"] = title

        print(f"🚀 Lancement du quiz '{title}' par '{teacher_name}' pour le salon [{pin}] avec {len(questions)} questions")

        # Diffuser à tous les élèves de la salle (avec teacher_name et title)
        emit('quiz_started', {
            'pin': pin, 
            'questions': questions, 
            'current_question': 0,
            'teacher_name': teacher_name,
            'title': title
        }, to=pin)

# ========================================================
# ⏭️ PASSAGE À LA QUESTION SUIVANTE (PROFESSEUR SEULEMENT)
# ========================================================
@socketio.on('next_question')
def handle_next_question(data):
    pin = data.get('pin', '').replace(" ", "")

    if pin in active_lobbies:
        lobby = active_lobbies[pin]
        lobby["current_question"] += 1
        
        total_questions = len(lobby["questions"])
        current_index = lobby["current_question"]

        if current_index < total_questions:
            print(f"⏭️ Salon [{pin}] -> Passage à la question {current_index + 1}/{total_questions}")
            # On informe TOUS les élèves du salon de changer de question
            emit('change_question', {
                'question_index': current_index
            }, to=pin)
        else:
            print(f"🏁 Salon [{pin}] -> Quiz terminé !")
            leaderboard = build_leaderboard(lobby)
            emit('quiz_ended', {'pin': pin, 'leaderboard': leaderboard}, to=pin)

# ========================================================
# 📊 MISE À JOUR DU CLASSEMENT HÔTE EN TEMPS RÉEL
# ========================================================
@socketio.on('update_score')
def handle_update_score(data):
    pin = data.get('pin', '').replace(" ", "")
    player = data.get('player')
    score = data.get('score', 0)

    if pin in active_lobbies:
        active_lobbies[pin].setdefault("scores", {})
        active_lobbies[pin]["scores"][player] = score

        leaderboard = build_leaderboard(active_lobbies[pin])
        emit('leaderboard_update', {"players": leaderboard}, to=pin)

if __name__ == '__main__':
    print("🚀 Serveur TMY Quiz Maker démarré sur http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)