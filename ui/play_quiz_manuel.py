"""
===========================================
TMY Quiz Maker
Version 5.2

play_quiz_manuel.py - Interface Élève Synchronisée
===========================================
"""

import customtkinter as ctk
import winsound

from voice import parler, parler_sequence, stop
import ui.colors as colors
import ui.fonts as fonts


class PlayQuizManuelPage(ctk.CTkFrame):

    def __init__(self, master, network_controller=None, titre_quiz="Quiz", nom_prof="Professeur", nom_eleve="Élève", title=None, home_callback=None):
        super().__init__(master)

        self.network_controller = network_controller
        self.home_callback = home_callback

        # Métadonnées transmises
        self.titre_quiz = title if title is not None else titre_quiz
        self.nom_prof = nom_prof
        self.nom_eleve = nom_eleve
        self.home_callback = home_callback

        #Statistiques

        self.index = 0
        self.total_questions = 1
        self.score = 0
        self.points_earned = 0
        self.total_points_possible = 0
        self.current_question_points = 10
        self.combo = 0
        self.max_combo = 0

        # Détail des réponses
        self.bonnes_reponses = 0
        self.mauvaises_reponses = 0
        self.non_repondues = 0

        self.answered = False
        self.selected_choice = None
        self.current_question = None
        self.resultats_affiches = False
        self.latest_leaderboard = []

        # Callback pour la fin du quiz
        self.on_quiz_ended_callback = self.afficher_resultats

        # Gestion du Chronomètre
        self.current_time = 0
        self.remaining_time = 0
        self.timer_running = False

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=25)

        self.create_interface()

    # =========================================
    # Bruitages
    # =========================================
    def start_sound(self):
        try: winsound.Beep(1500, 300)
        except Exception: pass

    def beep(self):
        try: winsound.Beep(1000, 150)
        except Exception: pass

    def timeout_sound(self):
        try: winsound.Beep(500, 600)
        except Exception: pass

    def correct_sound(self):
        try: winsound.Beep(1800, 200)
        except Exception: pass

    def wrong_sound(self):
        try: winsound.Beep(350, 400)
        except Exception: pass

    # =========================================
    # Interface
    # =========================================
    def create_interface(self):
        # 1. En-tête
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text=f"🎮 {self.titre_quiz.upper()}",
            font=("Arial", 16, "bold"),
            text_color="#1F6AA5"
        )
        self.title_lbl.pack(side="left")

        self.stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.stats_frame.pack(side="right")

        self.rank_label = ctk.CTkLabel(
            self.stats_frame,
            text="🥇 1er",
            font=("Arial", 13, "bold"),
            text_color="#00E676"
        )
        self.rank_label.pack(side="left", padx=(0, 10))

        self.combo_label = ctk.CTkLabel(
            self.stats_frame,
            text="🔥 x0",
            font=("Arial", 13, "bold"),
            text_color="#FF9800"
        )
        self.combo_label.pack(side="left", padx=(0, 10))

        self.points_label = ctk.CTkLabel(
            self.stats_frame,
            text="🏆 0/0 pts",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        self.points_label.pack(side="left")

        # 2. Barre de progression & Chrono
        self.info_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.info_bar.pack(fill="x", pady=(0, 5))

        self.counter = ctk.CTkLabel(
            self.info_bar,
            text="Question -- / --",
            font=("Arial", 14, "bold"),
            text_color="#FFFFFF"
        )
        self.counter.pack(side="left")

        self.timer_label = ctk.CTkLabel(
            self.info_bar,
            text="⏱ --s",
            font=("Arial", 14, "bold"),
            text_color="#4CC9F0"
        )
        self.timer_label.pack(side="right")

        self.timer_bar = ctk.CTkProgressBar(
            self.container,
            height=8,
            corner_radius=4,
            progress_color="#1F6AA5",
            fg_color="#1E222D"
        )
        self.timer_bar.set(1.0)
        self.timer_bar.pack(fill="x", pady=(2, 20))

        # 3. Carte Question
        self.question_card = ctk.CTkFrame(
            self.container,
            fg_color="#1E222D",
            corner_radius=16,
            border_width=1,
            border_color="#2B303C"
        )
        self.question_card.pack(fill="x", ipady=20, pady=(0, 20))

        self.question = ctk.CTkLabel(
            self.question_card,
            text="En attente de la question...",
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF",
            wraplength=650,
            justify="center"
        )
        self.question.pack(expand=True, padx=25, pady=20)

        # 4. Réponses
        self.answers_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.answers_frame.pack(fill="both", expand=True)

        self.buttons = {}
        self.button_frames = {}

        for lettre in ["A", "B", "C", "D"]:
            btn_frame = ctk.CTkFrame(
                self.answers_frame,
                fg_color="#1E222D",
                corner_radius=12,
                border_width=1,
                border_color="#2B303C"
            )
            btn_frame.pack(fill="x", pady=6)

            badge = ctk.CTkLabel(
                btn_frame,
                text=lettre,
                font=("Arial", 12, "bold"),
                width=32,
                height=32,
                corner_radius=8,
                fg_color="#2B2D42",
                text_color="#FFFFFF"
            )
            badge.pack(side="left", padx=10, pady=8)

            bouton = ctk.CTkButton(
                btn_frame,
                text="",
                font=("Arial", 13),
                anchor="w",
                fg_color="transparent",
                hover_color="#252A37",
                text_color="#FFFFFF",
                command=lambda l=lettre: self.submit_answer(l)
            )
            bouton.pack(side="left", fill="both", expand=True, padx=(0, 10))

            self.buttons[lettre] = bouton
            self.button_frames[lettre] = (btn_frame, badge)

        # 5. Message de statut
        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 14, "italic"),
            text_color="#4CC9F0"
        )
        self.status_label.pack(pady=(15, 0))

    # =========================================
    # Chargement Question & Séquence Vocale
    # =========================================
    def load_network_question(self, question_data, current_index=1, total_questions=1):
        try: stop()
        except Exception: pass

        self.timer_running = False
        self.current_question = question_data
        self.index = current_index
        self.total_questions = total_questions

        prof_recup = (
            question_data.get("teacher_name") or 
            question_data.get("nom_prof") or 
            question_data.get("prof_name") or 
            question_data.get("professeur")
        )
        if prof_recup:
            self.nom_prof = prof_recup

        titre_recup = question_data.get("titre_quiz") or question_data.get("title")
        if titre_recup:
            self.titre_quiz = titre_recup
            self.title_lbl.configure(text=f"🎮 {self.titre_quiz.upper()}")

        self.answered = False
        self.selected_choice = None

        self.counter.configure(text=f"Question {self.index} / {self.total_questions}")
        self.status_label.configure(text="")

        time_setting = question_data.get("time") or question_data.get("time_limit") or 20
        try:
            digits = "".join(ch for ch in str(time_setting) if ch.isdigit())
            self.current_time = int(digits) if digits else 20
        except (ValueError, TypeError):
            self.current_time = 20

        self.remaining_time = self.current_time
        self.update_timer_display()

        points_setting = question_data.get("points", 10)
        try:
            self.current_question_points = int(points_setting)
        except (ValueError, TypeError):
            self.current_question_points = 10

        self.total_points_possible += self.current_question_points
        self.points_label.configure(text=f"🏆 {self.points_earned}/{self.total_points_possible} pts")

        texte_question = question_data.get("question", "")
        self.question.configure(text=texte_question)

        options = question_data.get("options", {})
        if isinstance(options, list):
            options = {lettre: options[i] for i, lettre in enumerate(["A", "B", "C", "D"]) if i < len(options)}
        elif not isinstance(options, dict):
            options = {}

        self.parsed_answers = {
            "A": str(question_data.get("A") or options.get("A", "")),
            "B": str(question_data.get("B") or options.get("B", "")),
            "C": str(question_data.get("C") or options.get("C", "")),
            "D": str(question_data.get("D") or options.get("D", ""))
        }

        # Masquer les réponses et désactiver les boutons au début de la lecture
        for lettre in ["A", "B", "C", "D"]:
            self.buttons[lettre].configure(text="", state="disabled")
            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E222D", border_color="#2B303C")
            badge.configure(fg_color="#2B2D42")

        # Préparation des textes pour la lecture séquentielle
        self.audio_cache = {
            "A": [("A", 0.2), (self.parsed_answers["A"], 0.3)],
            "B": [("B", 0.2), (self.parsed_answers["B"], 0.3)],
            "C": [("C", 0.2), (self.parsed_answers["C"], 0.3)],
            "D": [("D", 0.2), (self.parsed_answers["D"], 0.3)]
        }

        # ÉTAPE 1 : Lecture de la question
        parler_sequence(
            [(texte_question, 0.3)],
            callback=lambda: self.after(0, self.lire_etape_A)
        )

    # --- Étapes Audio de lecture progressive ---
    def lire_etape_A(self):
        self.buttons["A"].configure(text=self.parsed_answers["A"])
        parler_sequence(self.audio_cache["A"], callback=lambda: self.after(0, self.lire_etape_B))

    def lire_etape_B(self):
        self.buttons["B"].configure(text=self.parsed_answers["B"])
        parler_sequence(self.audio_cache["B"], callback=lambda: self.after(0, self.lire_etape_C))

    def lire_etape_C(self):
        self.buttons["C"].configure(text=self.parsed_answers["C"])
        parler_sequence(self.audio_cache["C"], callback=lambda: self.after(0, self.lire_etape_D))

    def lire_etape_D(self):
        self.buttons["D"].configure(text=self.parsed_answers["D"])
        parler_sequence(self.audio_cache["D"], callback=lambda: self.after(0, self.lire_etape_fin))

    def lire_etape_fin(self):
        texte_fin = f"Vous avez {self.current_time} secondes."
        parler_sequence([(texte_fin, 0)], callback=lambda: self.after(0, self.start_timer))

    # =========================================
    # Gestion du Timer & Décompte
    # =========================================
    def start_timer(self):
        self.start_sound()
        # Activer les boutons pour permettre la réponse
        for btn in self.buttons.values():
            btn.configure(state="normal")
        self.timer_running = True
        self.count_down()

    def count_down(self):
        if not self.timer_running:
            return

        if self.remaining_time <= 0:
            self.timer_running = False
            self.on_time_out()
            return

        self.update_timer_display()

        if 0 < self.remaining_time <= 5:
            self.beep()

        self.remaining_time -= 1
        self.after(1000, self.count_down)

    def update_timer_display(self):
        if self.current_time == 0:
            return

        ratio = max(0, self.remaining_time / self.current_time)
        self.timer_bar.set(ratio)
        self.timer_label.configure(text=f"⏱ {self.remaining_time}s")
        
        if ratio <= 0.25:
            self.timer_label.configure(text_color="#FF5252")
            self.timer_bar.configure(progress_color="#FF5252")
        elif ratio <= 0.50:
            self.timer_label.configure(text_color="#FF9800")
            self.timer_bar.configure(progress_color="#FF9800")
        else:
            self.timer_label.configure(text_color="#1F6AA5")
            self.timer_bar.configure(progress_color="#1F6AA5")

    # =========================================
    # Choix de la réponse & Fin du Temps
    # =========================================
    def submit_answer(self, lettre):
        if self.answered:
            return

        self.answered = True
        self.selected_choice = lettre

        # Bloquer les boutons pour éviter les clics multiples
        for l, btn in self.buttons.items():
            btn.configure(state="disabled")

        frame, badge = self.button_frames[lettre]
        frame.configure(fg_color="#252A37", border_color="#1F6AA5")
        badge.configure(fg_color="#1F6AA5")

        self.status_label.configure(
            text="🔒 Réponse enregistrée ! Le chrono continue..."
        )

        if self.network_controller and hasattr(self.network_controller, "send_answer"):
            self.network_controller.send_answer(lettre)

    def get_correct_answer(self):
        """Récupère dynamiquement la bonne réponse de la question"""
        if not self.current_question:
            return "A"

        c = (
            self.current_question.get("correct") or 
            self.current_question.get("reponse") or 
            self.current_question.get("correct_answer") or 
            self.current_question.get("answer") or
            "A"
        )
        return str(c).strip().upper()

    def on_time_out(self):
        """Déclenché automatiquement lorsque le chrono passe à 0"""
        try: stop()
        except Exception: pass
        self.timeout_sound()

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        bonne = self.get_correct_answer()

        # Coloration de la BONNE réponse en Vert
        if bonne in self.button_frames:
            frame_c, badge_c = self.button_frames[bonne]
            frame_c.configure(fg_color="#1E4620", border_color="#2E7D32")
            badge_c.configure(fg_color="#2E7D32")

        # Analyse du choix de l'élève
        if self.selected_choice is not None:
            if self.selected_choice == bonne:
                self.correct_sound()
                self.score += 1
                self.bonnes_reponses += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)

                self.points_earned += self.current_question_points

                self.status_label.configure(text=f"✅ Bonne réponse ! (+{self.current_question_points} points)")
                
                try: parler("Bonne réponse.")
                except Exception: pass
            else:
                self.wrong_sound()
                self.mauvaises_reponses += 1
                if self.selected_choice in self.button_frames:
                    frame_w, badge_w = self.button_frames[self.selected_choice]
                    frame_w.configure(fg_color="#4A151B", border_color="#C62828")
                    badge_w.configure(fg_color="#C62828")
                
                self.combo = 0
                self.status_label.configure(text=f"❌ Mauvaise réponse. La bonne était la [{bonne}].")
                
                # La voix parle à la fin et donne la bonne réponse
                try: parler(f"Mauvaise réponse. La bonne réponse était la {bonne}.")
                except Exception: pass
        else:
            self.combo = 0
            self.non_repondues += 1
            self.status_label.configure(text=f"⏰ Temps écoulé ! La réponse était la [{bonne}].")
            
            # La voix parle si aucune réponse n'a été donnée
            try: parler(f"Temps écoulé. La bonne réponse était la {bonne}.")
            except Exception: pass

        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.points_label.configure(text=f"🏆 {self.points_earned}/{self.total_points_possible} pts")

        # Mise à jour du score sur le réseau
        if self.network_controller and hasattr(self.network_controller, "send_score_update"):
            pin = getattr(self.master, "current_active_pin", "")
            self.network_controller.send_score_update(pin, self.nom_eleve, self.points_earned)

        # Si c'est la dernière question, on affiche les résultats après quelques secondes
        if self.index >= self.total_questions:
            print("🏁 Dernière question terminée côté élève !")
            self.after(3500, self.afficher_resultats)

    # =========================================
    # Navigation : Redirection vers ResultElevePage
    # =========================================
    
    def mettre_a_jour_classement(self, data):
        """Reçoit en direct le classement de la salle à chaque score mis à jour."""
        if isinstance(data, dict):
            self.latest_leaderboard = data.get('players', [])

    def recevoir_classement_final(self, data):
        """Reçoit le classement final envoyé par le serveur quand le prof termine le quiz."""
        if isinstance(data, dict) and data.get('leaderboard'):
            self.latest_leaderboard = data['leaderboard']
        self.afficher_resultats()

    def calculer_classement(self):
        """Calcule le rang de l'élève, le nombre de participants et la moyenne de la salle."""
        classement = list(self.latest_leaderboard)

        if not any(p.get("name") == self.nom_eleve for p in classement):
            classement.append({"name": self.nom_eleve, "score": self.points_earned})

        classement_trie = sorted(classement, key=lambda p: p.get("score", 0), reverse=True)

        total_participants = len(classement_trie)
        rang = next(
            (i + 1 for i, p in enumerate(classement_trie) if p.get("name") == self.nom_eleve),
            total_participants
        )

        scores = [p.get("score", 0) for p in classement_trie]
        moyenne = round(sum(scores) / len(scores), 1) if scores else 0

        return rang, total_participants, moyenne

    def afficher_resultats(self):
        """Redirige vers l'écran des résultats élèves"""
        if self.resultats_affiches:
            return
        self.resultats_affiches = True

        try:
            from ui.result_eleve import ResultElevePage
        except ImportError:
            from result_eleve import ResultElevePage

        self.pack_forget()

        rang, total_participants, moyenne = self.calculer_classement()

        page_resultats = ResultElevePage(
            master=self.master,
            titre_quiz=self.titre_quiz,
            nom_prof=self.nom_prof,
            nom_eleve=self.nom_eleve,
            score=self.score,
            total=self.total_questions,
            points_earned=self.points_earned,
            total_points=self.total_points_possible,
            max_combo=self.max_combo,
            average_time=round(self.current_time / max(1, self.total_questions), 1),
            bonnes_reponses=self.bonnes_reponses,
            mauvaises_reponses=self.mauvaises_reponses,
            non_repondues=self.non_repondues,
            rang=rang,
            total_participants=total_participants,
            moyenne_classe=moyenne,
            certificat_callback=lambda: print("Génération du certificat..."),
            home_callback=self.retour_accueil
        )
        page_resultats.pack(expand=True, fill="both")

    def retour_accueil(self):
        """Action du bouton Accueil sur la page des résultats"""
        for widget in self.master.winfo_children():
            widget.destroy()
        if self.home_callback:
            self.home_callback()