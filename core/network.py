"""
===========================================
TMY Quiz Maker - Client Network Socket.IO
===========================================
"""

import time
import socketio

class NetworkClient:
    def __init__(self, server_url="https://tmy-quiz-server.onrender.com"):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.is_connected = False
        
        self.on_join_response_callback = None
        self.on_player_joined_callback = None
        # Callback exécuté lors du lancement du quiz par l'hôte
        self.on_quiz_started_callback = None
        # Nouveaux callbacks pour la synchronisation des questions par le prof
        self.on_change_question_callback = None
        self.on_quiz_ended_callback = None
        self.on_leaderboard_update_callback = None

        self.setup_events()

    def setup_events(self):
        @self.sio.event
        def connect():
            self.is_connected = True
            print("🟢 Connecté au serveur WebSocket !")

        @self.sio.event
        def disconnect():
            self.is_connected = False
            print("🔴 Déconnecté du serveur.")

        @self.sio.on('join_response')
        def on_join_response(data):
            if self.on_join_response_callback:
                self.on_join_response_callback(data)

        @self.sio.on('player_joined')
        def on_player_joined(data):
            if self.on_player_joined_callback:
                self.on_player_joined_callback(data)

        # Écouteur de l'événement de lancement du quiz
        @self.sio.on('quiz_started')
        def on_quiz_started(data=None):
            print("🚀 Quiz lancé par l'hôte !")
            if self.on_quiz_started_callback:
                # Transmet l'ensemble des données (questions, teacher_name, title) au callback
                self.on_quiz_started_callback(data)

        # ----------------------------------------------------
        # 📊 Mise à jour du classement
        # ----------------------------------------------------
        @self.sio.on('leaderboard_update')
        def on_leaderboard_update(data):
            if self.on_leaderboard_update_callback:
                self.on_leaderboard_update_callback(data)

        # ----------------------------------------------------
        # ⏭️ Nouveaux écouteurs pour la gestion synchrone
        # ----------------------------------------------------
        @self.sio.on('change_question')
        def on_change_question(data):
            print(f"⏭️ Ordre reçu : passage à la question index {data.get('question_index')}")
            if self.on_change_question_callback:
                self.on_change_question_callback(data)

        @self.sio.on('quiz_ended')
        def on_quiz_ended(data):
            print("🏁 Quiz terminé par le professeur !")
            if self.on_quiz_ended_callback:
                self.on_quiz_ended_callback(data)

    def connect(self, max_retries=3):
        """Tente de se connecter au serveur avec réessai en cas d'endormissement de Render."""
        if self.is_connected:
            return

        for attempt in range(max_retries):
            try:
                print(f"Connexion au serveur... (tentative {attempt + 1}/{max_retries})")
                # wait_timeout=30 laisse à Render 30 secondes pour se réveiller
                self.sio.connect(self.server_url, wait_timeout=30)
                if self.is_connected:
                    return
            except Exception as e:
                print(f"Le serveur se réveille ou est indisponible... ({e})")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Petite pause avant la tentative suivante
                else:
                    print("❌ Erreur définitive : impossible de contacter le serveur.")

    def create_room(self, pin, title, teacher_name="Professeur"):
        """Crée une nouvelle salle sur le serveur WebSocket."""
        self.connect()
        if self.is_connected:
            self.sio.emit('create_room', {
                'pin': pin,
                'title': title,
                'teacher_name': teacher_name
            })

    def join_room(self, pin, player_name, response_callback):
        self.connect()
        self.on_join_response_callback = response_callback
        if self.is_connected:
            self.sio.emit('join_room', {'pin': pin, 'name': player_name})
        else:
            response_callback({'success': False, 'message': '❌ Impossible de contacter le serveur.'})

    # Méthode pour envoyer l'ordre de démarrage du quiz + les questions + le nom du prof + le titre
    def start_quiz(self, pin, questions=None, teacher_name="Professeur", title="Mon Quiz"):
        """Envoie l'ordre de démarrage au serveur avec toutes les informations nécessaires."""
        self.connect()
        if self.is_connected:
            self.sio.emit('start_quiz', {
                'pin': pin,
                'questions': questions or [],
                'teacher_name': teacher_name,
                'title': title
            })

    # ----------------------------------------------------
    # 📤 Nouvelles méthodes d'émission
    # ----------------------------------------------------
    def send_next_question(self, pin):
        """Appelé uniquement par le PROFESSEUR pour faire passer tout le monde à la suite."""
        if self.is_connected:
            self.sio.emit('next_question', {'pin': pin})

    def send_score_update(self, pin, player_name, score):
        """Appelé par L'ÉLÈVE lorsqu'il valide une réponse pour mettre à jour son score sur l'hôte."""
        if self.is_connected:
            self.sio.emit('update_score', {'pin': pin, 'player': player_name, 'score': score})