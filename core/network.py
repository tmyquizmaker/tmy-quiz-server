"""
===========================================
TMY Quiz Maker - Client Network Socket.IO
===========================================
"""

import time
import socketio


class NetworkClient:

    def __init__(self, server_url="https://tmy-quiz-server.onrender.com"):
        self.sio = socketio.Client(request_timeout=20)
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
        self.on_quiz_cancelled_callback = None
        self.on_room_created_callback = None

        # --- Callbacks Mode Multijoueur "Questions entre amis" (Niveau 1) ---
        self.on_party_auto_start_scheduled_callback = None
        self.on_party_force_start_callback = None
        self.on_party_started_callback = None
        self.on_party_question_callback = None
        self.on_party_error_callback = None

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

        @self.sio.on('room_created')
        def on_room_created(data):
            if self.on_room_created_callback:
                self.on_room_created_callback(data)

        @self.sio.on("join_response")
        def on_join_response(data):
            if self.on_join_response_callback:
                self.on_join_response_callback(data)

        @self.sio.on("player_joined")
        def on_player_joined(data):
            if self.on_player_joined_callback:
                self.on_player_joined_callback(data)

        # Écouteur de l'événement de lancement du quiz
        @self.sio.on("quiz_started")
        def on_quiz_started(data=None):
            print("🚀 Quiz lancé par l'hôte !")
            if self.on_quiz_started_callback:
                # Transmet l'ensemble des données (questions, teacher_name, title) au callback
                self.on_quiz_started_callback(data)

        # ----------------------------------------------------
        # 📊 Mise à jour du classement
        # ----------------------------------------------------
        @self.sio.on("leaderboard_update")
        def on_leaderboard_update(data):
            if self.on_leaderboard_update_callback:
                self.on_leaderboard_update_callback(data)

        # ----------------------------------------------------
        # ⏭️ Nouveaux écouteurs pour la gestion synchrone
        # ----------------------------------------------------
        @self.sio.on("change_question")
        def on_change_question(data):
            print(
                f"⏭️ Ordre reçu : passage à la question index {data.get('question_index')}"
            )
            if self.on_change_question_callback:
                self.on_change_question_callback(data)

        @self.sio.on("quiz_ended")
        def on_quiz_ended(data):
            print("🏁 Quiz terminé par le professeur !")
            if self.on_quiz_ended_callback:
                self.on_quiz_ended_callback(data)

        @self.sio.on("quiz_cancelled")
        def on_quiz_cancelled(data):
            print("🛑 Quiz annulé par le professeur !")
            if self.on_quiz_cancelled_callback:
                self.on_quiz_cancelled_callback(data)

        # ----------------------------------------------------
        # 🎉 Mode "Questions entre amis" (Niveau 1)
        # ----------------------------------------------------
        @self.sio.on("party_auto_start_scheduled")
        def on_party_auto_start_scheduled(data):
            if self.on_party_auto_start_scheduled_callback:
                self.on_party_auto_start_scheduled_callback(data)

        @self.sio.on("party_force_start")
        def on_party_force_start(data=None):
            if self.on_party_force_start_callback:
                self.on_party_force_start_callback(data)

        @self.sio.on("party_started")
        def on_party_started(data):
            print("🎉 Partie 'Questions entre amis' lancée !")
            if self.on_party_started_callback:
                self.on_party_started_callback(data)

        @self.sio.on("party_question")
        def on_party_question(data):
            if self.on_party_question_callback:
                self.on_party_question_callback(data)

        @self.sio.on("party_error")
        def on_party_error(data):
            print(f"⚠️ Erreur mode party : {data}")
            if self.on_party_error_callback:
                self.on_party_error_callback(data)

    def connect(self, max_retries=8):
        """Tente de se connecter au serveur avec réessai en cas d'endormissement de Render."""
        if self.is_connected:
            return

        for attempt in range(max_retries):
            try:
                print(f"Connexion au serveur... (tentative {attempt + 1}/{max_retries})")
                self.sio.connect(self.server_url, wait_timeout=20)
                if self.is_connected:
                    return
            except Exception as e:
                print(f"Le serveur se réveille ou est indisponible... ({e})")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    print("❌ Erreur définitive : impossible de contacter le serveur.")

    def create_room(self, pin, title, teacher_name="Professeur", response_callback=None):
        """Crée une nouvelle salle sur le serveur WebSocket et attend la confirmation réelle."""
        self.on_room_created_callback = response_callback
        self.connect()
        if self.is_connected:
            self.sio.emit('create_room', {
                'pin': pin,
                'title': title,
                'teacher_name': teacher_name
            })
        elif response_callback:
            response_callback({'success': False, 'message': '❌ Impossible de contacter le serveur.'})

    def join_room(self, pin, player_name, response_callback):
        self.connect()
        self.on_join_response_callback = response_callback
        if self.is_connected:
            self.sio.emit("join_room", {"pin": pin, "name": player_name})
        else:
            response_callback(
                {
                    "success": False,
                    "message": "❌ Impossible de contacter le serveur.",
                }
            )

    # Méthode pour envoyer l'ordre de démarrage du quiz + les questions + le nom du prof + le titre
    def start_quiz(
        self, pin, questions=None, teacher_name="Professeur", title="Mon Quiz"
    ):
        """Envoie l'ordre de démarrage au serveur avec toutes les informations nécessaires."""
        self.connect()
        if self.is_connected:
            self.sio.emit(
                "start_quiz",
                {
                    "pin": pin,
                    "questions": questions or [],
                    "teacher_name": teacher_name,
                    "title": title,
                },
            )

    # ----------------------------------------------------
    # 📤 Nouveaux événements et émissions
    # ----------------------------------------------------
    def send_next_question(self, pin):
        """Appelé uniquement par le PROFESSEUR pour faire passer tout le monde à la suite."""
        if self.is_connected:
            self.sio.emit("next_question", {"pin": pin})

    def send_score_update(self, pin, player_name, score, combo=0, avg_time=0):
        """Appelé par L'ÉLÈVE lorsqu'il valide une réponse pour mettre à jour son score sur l'hôte."""
        if self.is_connected:
            self.sio.emit(
                "update_score",
                {
                    "pin": pin,
                    "player": player_name,
                    "score": score,
                    "combo": combo,
                    "avg_time": avg_time,
                },
            )

    def cancel_quiz(self, pin):
        """Appelé par le PROFESSEUR pour annuler le quiz en cours pour toute la salle."""
        if self.is_connected:
            self.sio.emit("cancel_quiz", {"pin": pin})

    # ----------------------------------------------------
    # 🎉 Mode "Questions entre amis" (Niveau 1)
    # ----------------------------------------------------
    def create_party_room(self, pin, name, subject, max_players, question_mode="infinite", question_limit=None, response_callback=None):
        """Crée une salle du mode party avec le sujet de l'hôte.
        question_mode: 'infinite' (boucle sans fin sur les sujets) ou 'fixed'
        (s'arrête après question_limit questions)."""
        self.on_room_created_callback = response_callback
        self.connect()
        if self.is_connected:
            self.sio.emit("create_party_room", {
                "pin": pin, "name": name, "subject": subject, "max_players": max_players,
                "question_mode": question_mode, "question_limit": question_limit,
            })
        elif response_callback:
            response_callback({"success": False, "message": "❌ Impossible de contacter le serveur."})

    def join_party_room(self, pin, name, subject, response_callback):
        """Rejoint (ou se reconnecte à) une salle du mode party avec son sujet."""
        self.connect()
        self.on_join_response_callback = response_callback
        if self.is_connected:
            self.sio.emit("join_party_room", {"pin": pin, "name": name, "subject": subject})
        else:
            response_callback({"success": False, "message": "❌ Impossible de contacter le serveur."})

    def start_party_quiz(self, pin):
        """Appelé par l'hôte pour lancer manuellement la partie (bouton 'Lancer la partie')."""
        if self.is_connected:
            self.sio.emit("start_party_quiz", {"pin": pin})

    def send_party_answer(self, pin, player, correct, score, combo=0, avg_time=0):
        """Envoie la réponse d'un joueur à la question du mode party en cours."""
        if self.is_connected:
            self.sio.emit("party_answer", {
                "pin": pin, "player": player, "correct": correct,
                "score": score, "combo": combo, "avg_time": avg_time,
            })

    def send_player_abandon(self, pin, player):
        """Signale que le joueur quitte volontairement la partie en cours."""
        if self.is_connected:
            self.sio.emit("player_abandon", {"pin": pin, "player": player})
