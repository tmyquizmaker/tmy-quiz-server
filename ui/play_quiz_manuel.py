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

    def __init__(self, master, network_controller=None, titre_quiz="Quiz", nom_prof="Professeur", nom_eleve="Élève"):
        super().__init__(master)

        self.network_controller = network_controller

        # Métadonnées transmises
        self.titre_quiz = titre_quiz
        self.nom_prof = nom_prof
        self.nom_eleve = nom_eleve

        # Statistiques & État
        self.index = 0
        self.total_questions = 1
        self.score = 0
        self.total_xp = 0
        self.combo = 0
        self.max_combo = 0

        # Détail des réponses
        self.bonnes_reponses = 0
        self.mauvaises_reponses = 0
        self.non_repondues = 0

        self.answered = False
        self.selected_choice = None
        self.current_question = None

        # Callback pour la fin du quiz (Redirection par défaut vers la page résultat)
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
        winsound.Beep(1500, 300)

    def beep(self):
        winsound.Beep(1000, 150)

    def timeout_sound(self):
        winsound.Beep(500, 600)

    def correct_sound(self):
        winsound.Beep(1800, 200)

    def wrong_sound(self):
        winsound.Beep(350, 400)

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

        self.xp_label = ctk.CTkLabel(
            self.stats_frame,
            text="⚡ 0 XP",
            font=("Arial", 13, "bold"),
            text_color="#FFD700"
        )
        self.xp_label.pack(side="left")

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
    # Chargement Question & Voix
    # =========================================
    def load_network_question(self, question_data, current_index=1, total_questions=1):
        stop()
        self.timer_running = False
        
        self.current_question = question_data
        self.index = current_index
        self.total_questions = total_questions
        
        self.answered = False
        self.selected_choice = None

        # Mise à jour de l'affichage
        self.counter.configure(text=f"Question {self.index} / {self.total_questions}")
        self.status_label.configure(text="")

        time_setting = question_data.get("time") or question_data.get("time_limit") or 20
        try:
            self.current_time = int(time_setting)
        except (ValueError, TypeError):
            self.current_time = 20

        self.remaining_time = self.current_time
        self.update_timer_display()

        texte_question = question_data.get("question", "")
        self.question.configure(text=texte_question)

        # Désactiver les boutons pendant la lecture vocale
        for lettre in ["A", "B", "C", "D"]:
            self.buttons[lettre].configure(text="", state="disabled")
            frame, badge = self.button_frames[lettre]
            frame.configure(fg_color="#1E222D", border_color="#2B303C")
            badge.configure(fg_color="#2B2D42")

        # Préparation des séquences vocales
        self.audio_cache = {
            "A": [("Petit A", 0.3), (question_data.get("A", ""), 0.3)],
            "B": [("Petit B", 0.3), (question_data.get("B", ""), 0.3)],
            "C": [("Petit C", 0.3), (question_data.get("C", ""), 0.3)],
            "D": [("Petit D", 0.3), (question_data.get("D", ""), 0.3)]
        }

        # Démarrer la lecture
        parler_sequence(
            [(texte_question, 0.3)],
            callback=lambda: self.after(0, self.lire_etape_A)
        )

    # --- Étapes Audio de lecture ---
    def lire_etape_A(self):
        if self.answered: return
        self.buttons["A"].configure(text=self.current_question.get("A", ""))
        parler_sequence(self.audio_cache["A"], callback=lambda: self.after(0, self.lire_etape_B))

    def lire_etape_B(self):
        if self.answered: return
        self.buttons["B"].configure(text=self.current_question.get("B", ""))
        parler_sequence(self.audio_cache["B"], callback=lambda: self.after(0, self.lire_etape_C))

    def lire_etape_C(self):
        if self.answered: return
        self.buttons["C"].configure(text=self.current_question.get("C", ""))
        parler_sequence(self.audio_cache["C"], callback=lambda: self.after(0, self.lire_etape_D))

    def lire_etape_D(self):
        if self.answered: return
        self.buttons["D"].configure(text=self.current_question.get("D", ""))
        parler_sequence(self.audio_cache["D"], callback=lambda: self.after(0, self.lire_etape_fin))

    def lire_etape_fin(self):
        if self.answered: return
        texte_fin = f"Vous disposez de {self.current_time} secondes."
        parler_sequence([(texte_fin, 0)], callback=lambda: self.after(0, self.start_timer))

    # =========================================
    # Gestion du Timer & Décompte
    # =========================================
    def start_timer(self):
        self.start_sound()
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

    def on_time_out(self):
        """Déclenché automatiquement lorsque le chrono passe à 0"""
        stop()
        self.timeout_sound()

        for btn in self.buttons.values():
            btn.configure(state="disabled")

        bonne = self.current_question.get("correct", "A")

        frame_c, badge_c = self.button_frames[bonne]
        frame_c.configure(fg_color="#1E4620", border_color="#2E7D32")
        badge_c.configure(fg_color="#2E7D32")

        if self.selected_choice is not None:
            if self.selected_choice == bonne:
                self.correct_sound()
                self.score += 1
                self.bonnes_reponses += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)

                time_bonus = int((self.remaining_time / max(1, self.current_time)) * 50)
                combo_bonus = self.combo * 10
                earned_xp = 100 + time_bonus + combo_bonus
                self.total_xp += earned_xp

                self.status_label.configure(text=f"✅ Bonne réponse ! (+{earned_xp} XP)")
                parler("Bonne réponse.")
            else:
                self.wrong_sound()
                self.mauvaises_reponses += 1
                frame_w, badge_w = self.button_frames[self.selected_choice]
                frame_w.configure(fg_color="#4A151B", border_color="#C62828")
                badge_w.configure(fg_color="#C62828")
                
                self.combo = 0
                self.status_label.configure(text=f"❌ Mauvaise réponse. La bonne était la {bonne}.")
                parler(f"Mauvaise réponse. La bonne réponse était la {bonne}.")
        else:
            self.combo = 0
            self.non_repondues += 1
            self.status_label.configure(text=f"⏰ Temps écoulé ! La réponse était la {bonne}.")
            parler(f"Temps écoulé. La bonne réponse était la {bonne}.")

        self.combo_label.configure(text=f"🔥 x{self.combo}")
        self.xp_label.configure(text=f"⚡ {self.total_xp} XP")

        # 🚀 Si c'est la dernière question, basculer sur l'écran résultat
        if self.index >= self.total_questions:
            print("🏁 Dernière question terminée côté élève !")
            if hasattr(self, 'on_quiz_ended_callback') and self.on_quiz_ended_callback:
                self.after(3000, self.on_quiz_ended_callback)

    # =========================================
    # Navigation : Redirection vers ResultElevePage
    # =========================================
    def afficher_resultats(self):
        """Redirige vers l'écran des résultats élèves (ui/result_eleve.py)"""
        try:
            from ui.result_eleve import ResultElevePage
        except ImportError:
            from result_eleve import ResultElevePage

        # Masquer la page du quiz
        self.pack_forget()

        # Instancier et afficher la page de résultats
        page_resultats = ResultElevePage(
            master=self.master,
            titre_quiz=self.titre_quiz,
            nom_prof=self.nom_prof,
            nom_eleve=self.nom_eleve,
            score=self.score,
            total=self.total_questions,
            total_xp=self.total_xp,
            max_combo=self.max_combo,
            average_time=round(self.current_time / max(1, self.total_questions), 1),
            bonnes_reponses=self.bonnes_reponses,
            mauvaises_reponses=self.mauvaises_reponses,
            non_repondues=self.non_repondues,
            certificat_callback=lambda: print("Génération du certificat..."),
            home_callback=self.retour_accueil
        )
        page_resultats.pack(expand=True, fill="both")

    def retour_accueil(self):
        """Action du bouton Accueil sur la page des résultats"""
        for widget in self.master.winfo_children():
            widget.pack_forget()
        if hasattr(self.master, "show_home"):
            self.master.show_home()