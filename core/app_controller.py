"""
===========================================
TMY Quiz Maker
Version 5.3

app_controller.py

Contrôle navigation + gestion des quiz locaux + Lobby Multijoueur
===========================================
"""

import threading
import customtkinter as ctk

from ui.loading import LoadingScreen
from ui.home import HomePage
from ui.tmy_generator import TMYGeneratorPage
from audio.music import stop_music, resume_music
from ui.play_quiz import PlayQuizPage
from ui.play_quiz_manuel import PlayQuizManuelPage  # 👈 CÔTÉ ÉLÈVE
from ui.result import ResultPage
from ui.quiz_loading import QuizLoadingPage
from ai.ai_generator import AIGenerator

from data.quiz_storage import save_quiz
from ui.my_quizzes import MyQuizzesPage
from ui.quiz_lobby import QuizLobbyPage
from ui.join_page import JoinRoomPage
from ui.leaderboard_overlay import TeacherFullDashboard
from core.network import NetworkClient

try:
    from ui.manual_quiz import ManualQuizPage
except ImportError:
    ManualQuizPage = None


class AppController:

    def __init__(self, root):
        self.root = root

        self.ai = AIGenerator()
        self.network = NetworkClient()  # Initialisation du client réseau WebSocket

        self.current_quiz_settings = {
            "sujet": "",
            "niveau": "",
            "nombre": 0
        }

        self.current_quiz = []
        self.loading_active = False

        # Métadonnées pour la session réseau (Élève / Prof)
        self.current_student_name = "Élève"
        self.current_quiz_title = "Quiz en direct"
        self.current_teacher_name = "Professeur"

        # Dictionnaire pour stocker les salons ouverts
        self.active_lobbies = {}

    # =====================================
    # Démarrage
    # =====================================
    def start(self):
        self.show_loading()

    # =====================================
    # Loading application
    # =====================================
    def show_loading(self):
        self.clear_page()
        self.loading_active = True

        self.loading = LoadingScreen(self.root)
        self.loading.pack(fill="both", expand=True)

        self.run_loading_animation()

    def run_loading_animation(self):
        etapes = self.loading.animation()

        def next_step(index=0):
            if not self.loading_active:
                return

            if index < len(etapes):
                valeur, message = etapes[index]
                self.loading.update_progress(valeur, message)
                self.root.after(500, lambda: next_step(index + 1))
            else:
                self.show_home()

        next_step()

    # =====================================
    # Accueil
    # =====================================
    def show_home(self):
        self.loading_active = False
        self.clear_page()

        self.home = HomePage(
            master=self.root,
            tmy_callback=self.show_tmy_generator,
            manual_callback=self.show_create_manual,
            quizzes_callback=self.show_my_quizzes,
            multiplayer_callback=self.show_multiplayer,
            join_callback=self.show_join_room,
            settings_callback=self.show_settings,
            stats_callback=self.show_stats
        )

        self.home.pack(fill="both", expand=True)

    # --- Callbacks complémentaires ---
    def show_multiplayer(self):
        print("Lancement du lobby multijoueur")

    # =====================================
    # 🔑 REJOINDRE UN QUIZ (ÉLÈVE)
    # =====================================
    def show_join_room(self):
        """Affiche la page complète pour entrer le nom, prénom et le code PIN"""
        self.clear_page()
        self.join_page = JoinRoomPage(
            self.root,
            verify_join_callback=self.verify_and_join_room,
            back_callback=self.show_home
        )
        self.join_page.pack(fill="both", expand=True)

    def verify_and_join_room(self, pin_code, full_name):
        """Demande au serveur WebSocket si la salle existe"""
        result = {"success": False, "message": ""}
        event_done = threading.Event()

        clean_pin = pin_code.replace(" ", "")

        def on_response(data):
            if data.get('success'):
                result["success"] = True
                # Stockage des infos élève & métadonnées du quiz
                self.current_student_name = full_name
                self.current_quiz_title = data.get('title') or data.get('quiz_title', 'Quiz en direct')
                
                # Récupérer le nom du prof depuis 'teacher_name', 'nom_prof' ou 'professeur'
                self.current_teacher_name = (
                    data.get('teacher_name') or 
                    data.get('nom_prof') or 
                    data.get('professeur') or 
                    "Professeur"
                )

                self.root.after(0, lambda: self.show_student_lobby(
                    clean_pin, 
                    self.current_quiz_title, 
                    full_name
                ))
            else:
                result["message"] = data.get('message', 'Erreur de connexion.')
            event_done.set()

        # Envoi de la demande au serveur via WebSocket
        self.network.join_room(clean_pin, full_name, on_response)
        
        event_done.wait(timeout=15)
        return result["success"], result["message"]

    def show_student_lobby(self, pin, title, full_name):
        """Affiche la salle d'attente pour l'élève et s'abonne au lancement du jeu"""
        self.clear_page()
        self.lobby_page = QuizLobbyPage(
            self.root,
            quiz_title=title,
            max_players=0,
            start_quiz_callback=None,
            back_callback=self.show_home,
            is_host=False
        )
        
        self.lobby_page.game_pin = pin
        if hasattr(self.lobby_page, 'pin_code'):
            formatted_pin = f"{pin[:3]} {pin[3:]}" if len(pin) == 6 else pin
            self.lobby_page.pin_code.configure(text=formatted_pin)

        self.lobby_page.add_player(full_name)

        # Mettre à jour la liste quand un joueur rejoint
        def on_player_joined(data):
            if isinstance(data, dict) and data.get('players'):
                players_list = data['players']
                self.root.after(0, lambda p=players_list: self.lobby_page.set_players(p))

        self.network.on_player_joined_callback = on_player_joined

        # 🚀 RÉCEPTION DE L'ÉVÉNEMENT DE DÉMARRAGE DU QUIZ
        def handle_start_quiz(data=None):
            print("🟢 ÉVÉNEMENT REÇU CÔTÉ ÉLÈVE : Lancement du Quiz !", data)
            
            questions = []
            if isinstance(data, dict):
                questions = data.get('questions', [])
                if 'title' in data and data['title']:
                    self.current_quiz_title = data['title']
                
                # Récupération sécurisée du nom du professeur
                prof = (
                    data.get('teacher_name') or 
                    data.get('nom_prof') or 
                    data.get('professeur')
                )
                if prof:
                    self.current_teacher_name = prof

            if questions:
                self.current_quiz = questions

            # Basculer l'affichage dans le thread Tkinter principal
            def update_ui():
                if hasattr(self, 'lobby_page') and self.lobby_page:
                    self.lobby_page.pack_forget()
                self.start_student_game(questions_list=questions)

            self.root.after(0, update_ui)

        # Enregistrement propre via la fonction de rappel de NetworkClient
        self.network.on_quiz_started_callback = handle_start_quiz

        self.lobby_page.pack(fill="both", expand=True)

    def start_student_game(self, questions_list=None):
        """Démarre la session de jeu MANUELLE pour l'élève"""
        print("▶️ Transition vers PlayQuizManuelPage pour l'élève...")
        self.clear_page()
        stop_music()

        if questions_list:
            self.current_quiz = questions_list

        # 🎯 Transmission du network_controller + métadonnées
        self.play = PlayQuizManuelPage(
            self.root,
            network_controller=self.network,
            titre_quiz=self.current_quiz_title,
            nom_prof=self.current_teacher_name,
            nom_eleve=self.current_student_name,
            home_callback=self.show_home
        )
        self.play.pack(fill="both", expand=True)

        # 🚀 Charger immédiatement la première question transmise
        if self.current_quiz and len(self.current_quiz) > 0:
            first_q = self.current_quiz[0]
            first_q['teacher_name'] = self.current_teacher_name
            self.play.load_network_question(
                question_data=first_q,
                current_index=1,
                total_questions=len(self.current_quiz)
            )

        def handle_change_question(data):
            new_index = data.get('question_index', 0)
            print(f"📩 Ordre serveur reçu côté élève : passer à l'index {new_index}")
            self.root.after(0, lambda: self.passer_question_suivante_eleve(new_index))

        # Liaison avec le réseau WebSocket
        self.network.on_change_question_callback = handle_change_question
        self.network.on_leaderboard_update_callback = lambda data: self.root.after(0, lambda d=data: self.play.mettre_a_jour_classement(d))
        self.network.on_quiz_ended_callback = lambda data=None: self.root.after(0, lambda d=data: self.play.recevoir_classement_final(d))

    def passer_question_suivante_eleve(self, index):
        """Passe la question de l'élève à l'index demandé par le serveur"""
        if hasattr(self, 'play') and isinstance(self.play, PlayQuizManuelPage):
            if self.current_quiz and 0 <= index < len(self.current_quiz):
                question_data = self.current_quiz[index]
                question_data['teacher_name'] = self.current_teacher_name
                self.play.load_network_question(
                    question_data=question_data,
                    current_index=index + 1,
                    total_questions=len(self.current_quiz)
                )

    def show_settings(self):
        print("Accès aux Paramètres")

    def show_stats(self):
        print("Accès aux Statistiques")

    # =====================================
    # 📁 MES QUIZ (HÔTE / PROFESSEUR)
    # =====================================
    def show_my_quizzes(self):
        self.clear_page()
        self.my_quizzes_page = MyQuizzesPage(
            self.root,
            launch_lobby_callback=self.open_quiz_lobby,
            back_callback=self.show_home
        )
        self.my_quizzes_page.pack(fill="both", expand=True)

    def host_start_quiz_callback(self):
        """Fonction appelée lorsque l'hôte clique sur LANCER LE QUIZ"""
        clean_pin = getattr(self, 'current_active_pin', None)
        print(f"🔴 L'hôte lance le quiz pour la salle PIN: {clean_pin}")

        if clean_pin:
            # Transmission alignée des 4 arguments : pin, questions, teacher_name, title
            self.network.start_quiz(
                clean_pin, 
                self.current_quiz, 
                self.current_teacher_name,
                self.current_quiz_title
            )

        # Fermer la vue du lobby si elle est ouverte
        if hasattr(self, 'lobby_page') and self.lobby_page:
            self.lobby_page.pack_forget()

        self.host_current_question_index = 0
        self.show_host_dashboard()

    def show_host_dashboard(self):
        """Affiche le Tableau de bord complet de supervision pour le créateur/hôte"""
        self.clear_page()
        stop_music()

        container = ctk.CTkFrame(self.root, fg_color="#121620")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        title_lbl = ctk.CTkLabel(
            header, 
            text=f"🔴 QUIZ EN COURS — PIN : {getattr(self, 'current_active_pin', '')}", 
            font=("Arial", 16, "bold"), 
            text_color="#FFD700"
        )
        title_lbl.pack(side="left")

        # ⏱ Chrono visible côté prof
        self.host_timer_lbl = ctk.CTkLabel(
            header,
            text="⏱ --s",
            font=("Arial", 14, "bold"),
            text_color="#4CC9F0"
        )
        self.host_timer_lbl.pack(side="left", padx=20)

        # ⏭️ BOUTON "QUESTION SUIVANTE" — désactivé tant que le chrono n'est pas fini
        self.next_q_btn = ctk.CTkButton(
            header,
            text="Question Suivante ➔",
            fg_color="#2FA572",
            hover_color="#1E6B49",
            font=("Arial", 14, "bold"),
            state="disabled",
            command=self.host_click_next_question
        )
        self.next_q_btn.pack(side="left", padx=20)

        back_btn = ctk.CTkButton(
            header, 
            text="Terminer la session", 
            fg_color="#D32F2F", 
            hover_color="#9A0007", 
            command=self.show_home
        )
        back_btn.pack(side="right")

        self.teacher_dashboard = TeacherFullDashboard(container)
        self.teacher_dashboard.pack(fill="both", expand=True)

        if hasattr(self.network, 'sio') and self.network.sio:
            @self.network.sio.on('leaderboard_update')
            def on_leaderboard_update(data):
                players_data = data.get('players', []) if isinstance(data, dict) else data
                self.root.after(0, lambda: self.teacher_dashboard.update_dashboard(players_data))

        self.start_host_timer()   # 👈 démarre le chrono pour la question 0

    def host_click_next_question(self):
        """Appelé lorsque le professeur clique sur le bouton Question Suivante (actif seulement chrono écoulé)"""
        clean_pin = getattr(self, 'current_active_pin', None)
        if clean_pin:
            print(f"⏭️ Le professeur demande le passage à la question suivante pour la salle [{clean_pin}]")
            self.network.send_next_question(clean_pin)

        self.host_current_question_index += 1

        if self.current_quiz and self.host_current_question_index < len(self.current_quiz):
            self.start_host_timer()
        else:
            self.next_q_btn.configure(state="disabled", text="🏁 Quiz terminé")
            self.host_timer_lbl.configure(text="")

    def start_host_timer(self):
        """Démarre le chrono du prof pour la question en cours et verrouille le bouton Suivant."""
        if not self.current_quiz or self.host_current_question_index >= len(self.current_quiz):
            return

        question = self.current_quiz[self.host_current_question_index]
        time_str = question.get("time", "20s")
        try:
            seconds = int("".join(ch for ch in str(time_str) if ch.isdigit()) or 20)
        except ValueError:
            seconds = 20

        self.host_remaining_time = seconds
        self.next_q_btn.configure(state="disabled")
        self._host_timer_tick()

    def _host_timer_tick(self):
        """Décompte du chrono prof, tick par seconde."""
        if not hasattr(self, 'next_q_btn'):
            return

        if self.host_remaining_time <= 0:
            self.next_q_btn.configure(state="normal", text="Question Suivante ➔")
            self.host_timer_lbl.configure(text="✅ Prêt")
            return

        self.host_timer_lbl.configure(text=f"⏱ {self.host_remaining_time}s")
        self.next_q_btn.configure(text=f"⏳ Patiente... ({self.host_remaining_time}s)")
        self.host_remaining_time -= 1
        self.root.after(1000, self._host_timer_tick)

    def open_quiz_lobby(self, quiz_title, questions, teacher_name="Professeur"):
        """Ouvre la salle d'attente (Lobby) et l'enregistre auprès du serveur WebSocket"""
        self.clear_page()
        self.current_quiz = questions
        self.current_quiz_title = quiz_title
        self.current_teacher_name = teacher_name  # Capturer le nom du professeur

        self.lobby_page = QuizLobbyPage(
            self.root,
            quiz_title=quiz_title,
            max_players=0,
            start_quiz_callback=self.host_start_quiz_callback,
            back_callback=self.show_my_quizzes,
            is_host=True
        )

        clean_pin = self.lobby_page.game_pin.replace(" ", "")
        self.current_active_pin = clean_pin

        # Créer la salle sur le réseau avec le nom du professeur
        if hasattr(self.network, 'create_room'):
            self.network.create_room(clean_pin, quiz_title, teacher_name=teacher_name)

        def on_player_joined_remote(data):
            if isinstance(data, dict) and data.get('players'):
                players_list = data['players']
                self.root.after(0, lambda p=players_list: self.lobby_page.set_players(p))

        self.network.on_player_joined_callback = on_player_joined_remote

        self.lobby_page.pack(fill="both", expand=True)

    # =====================================
    # 📝 Création manuelle
    # =====================================
    def show_create_manual(self):
        self.clear_page()

        if ManualQuizPage:
            self.manual_page = ManualQuizPage(
                self.root,
                on_quiz_created=self.on_manual_quiz_created,
                back_callback=self.show_home
            )
            self.manual_page.pack(fill="both", expand=True)
        else:
            print("Erreur : Le fichier ui/manual_quiz.py est introuvable.")

    def on_manual_quiz_created(self, quiz_title="Nouveau Quiz", teacher_name="Professeur", quiz_data=None, **kwargs):
        """
        Gère la création du quiz manuel en capturant le titre, le nom du professeur et les questions.
        """
        if quiz_data:
            save_quiz(quiz_title, quiz_data, teacher_name=teacher_name)
            print(f"Quiz '{quiz_title}' créé par {teacher_name} enregistré localement avec succès !")
        
        self.show_my_quizzes()

    # =====================================
    # Générateur TMY (IA)
    # =====================================
    def show_tmy_generator(self):
        self.clear_page()

        self.tmy_generator = TMYGeneratorPage(
            self.root,
            self.start_quiz,
            self.show_home
        )

        self.tmy_generator.pack(fill="both", expand=True)

    def start_quiz(self, sujet, nombre, niveau):
        self.current_quiz_settings = {
            "sujet": sujet,
            "nombre": nombre,
            "niveau": niveau
        }

        print("Création du quiz via TMY AI...")
        self.show_quiz_loading()

        threading.Thread(
            target=self.generate_quiz_background,
            daemon=True
        ).start()

    def generate_quiz_background(self):
        try:
            self.current_quiz = self.ai.generate_quiz(
                self.current_quiz_settings["sujet"],
                self.current_quiz_settings["nombre"],
                self.current_quiz_settings["niveau"]
            )

            self.root.after(0, self.show_play_quiz)

        except Exception as erreur:
            print("Erreur TMY :", erreur)

    # =====================================
    # Écran de chargement Quiz
    # =====================================
    def show_quiz_loading(self):
        self.clear_page()

        self.quiz_loading = QuizLoadingPage(self.root)
        self.quiz_loading.pack(fill="both", expand=True)

    # =====================================
    # Affichage du Quiz en cours (MODE SOLO)
    # =====================================
    def show_play_quiz(self):
        self.clear_page()
        stop_music()

        self.play = PlayQuizPage(
            self.root,
            self.current_quiz,
            self.show_result
        )

        self.play.pack(fill="both", expand=True)

    # =====================================
    # Écran des Résultats Solo
    # =====================================
    def show_result(
        self,
        score,
        total,
        total_xp,
        max_combo,
        average_time=0,
        quiz_data=None
    ):
        print("========== RESULT ==========")
        print("Score :", score)
        print("Total :", total)
        print("XP :", total_xp)
        print("Combo :", max_combo)
        print("============================")

        self.clear_page()

        self.root.after(2500, resume_music)

        self.result = ResultPage(
            self.root,
            score,
            total,
            total_xp,
            max_combo,
            average_time,
            self.regenerate_quiz,
            self.show_home
        )

        self.result.pack(fill="both", expand=True)

    # =====================================
    # Régénération du Quiz
    # =====================================
    def regenerate_quiz(self):
        settings = self.current_quiz_settings
        self.show_quiz_loading()

        def regen():
            try:
                self.current_quiz = self.ai.generate_quiz(
                    settings["sujet"],
                    settings["nombre"],
                    settings["niveau"],
                    regeneration=True
                )

                self.root.after(0, self.show_play_quiz)

            except Exception as erreur:
                print("Erreur régénération :", erreur)

        threading.Thread(target=regen, daemon=True).start()

    # =====================================
    # Nettoyage de l'écran
    # =====================================
    def clear_page(self):
        self.loading_active = False
        for widget in list(self.root.winfo_children()):
            widget.destroy()