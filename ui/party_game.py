"""
===========================================
TMY Quiz Maker
party_game.py - Écran de jeu du mode "Questions entre amis" (Niveau 1)

Contrairement à PlayQuizManuelPage (qui reçoit TOUTES les questions
d'un coup), ici les questions arrivent UNE PAR UNE depuis le serveur
(événement 'party_question'), avec une difficulté qui s'ajuste en
direct selon le taux de réussite de la salle.
===========================================
"""

import time
import customtkinter as ctk

try:
    from ui.leaderboard_overlay import StudentRankWidget
except ImportError:
    from leaderboard_overlay import StudentRankWidget

try:
    from voice import parler
except ImportError:
    def parler(*args, **kwargs):
        pass

try:
    from auth_client import session
except ImportError:
    session = None


POINTS_BASE = 100


class PartyGamePage(ctk.CTkFrame):

    def __init__(self, master, network_controller, nom_joueur, pin, home_callback):
        super().__init__(master, fg_color="#0b132b")

        self.network = network_controller
        self.nom_joueur = nom_joueur
        self.pin = pin
        self.home_callback = home_callback

        self.score_total = 0
        self.combo = 0
        self.temps_reponses = []
        self.option_buttons = []
        self.question_courante = None
        self.temps_debut_question = None
        self.timer_job = None
        self.temps_restant = 0
        self.a_repondu = False

        self._build_ui()

        # Abandon propre si la fenêtre se ferme pendant la partie
        self.bind("<Destroy>", self._on_destroy, add="+")

    # ---------------------------------------------
    def _build_ui(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=20, pady=15)

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text="🎉 QUESTIONS ENTRE AMIS", font=("Arial", 15, "bold"), text_color="#00b4d8"
        ).pack(side="left")

        self.stats_label = ctk.CTkLabel(
            header, text=f"⚡ 0 pts  🔥 x0", font=("Arial", 13, "bold"), text_color="#ffd166"
        )
        self.stats_label.pack(side="right")

        # Quitter la partie
        ctk.CTkButton(
            header, text="🚪 Quitter", width=90, fg_color="#37474F", hover_color="#263238",
            command=self.abandonner_partie
        ).pack(side="right", padx=10)

        info_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        info_frame.pack(fill="x", pady=(10, 0))

        self.question_num_label = ctk.CTkLabel(
            info_frame, text="Question -- / --", font=("Arial", 13, "bold"), text_color="#ffffff"
        )
        self.question_num_label.pack(side="left")

        self.difficulty_label = ctk.CTkLabel(
            info_frame, text="", font=("Arial", 12, "bold"), text_color="#4cc9f0"
        )
        self.difficulty_label.pack(side="left", padx=15)

        self.timer_label = ctk.CTkLabel(
            info_frame, text="⏳ --s", font=("Arial", 13, "bold"), text_color="#4cc9f0"
        )
        self.timer_label.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(self.container, progress_color="#00b4d8", fg_color="#1c2541", height=8)
        self.progress_bar.pack(fill="x", pady=10)
        self.progress_bar.set(1.0)

        self.question_card = ctk.CTkFrame(self.container, fg_color="#1c2541", corner_radius=12)
        self.question_card.pack(fill="x", pady=10, ipady=20)

        self.subject_label = ctk.CTkLabel(
            self.question_card, text="", font=("Arial", 11, "bold"), text_color="#8A8F9E"
        )
        self.subject_label.pack(pady=(5, 0))

        self.question_label = ctk.CTkLabel(
            self.question_card, text="En attente de la première question...",
            font=("Arial", 17, "bold"), text_color="#ffffff", wraplength=600, justify="center"
        )
        self.question_label.pack(expand=True, padx=20)

        self.options_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.options_frame.pack(fill="both", expand=True, pady=10)

        self.status_label = ctk.CTkLabel(self.container, text="", font=("Arial", 12, "italic"), text_color="#4cc9f0")
        self.status_label.pack(pady=(5, 0))

        # Classement en direct — Top 3 + mon rang, mis à jour après chaque réponse
        self.rank_widget = StudentRankWidget(self.container, current_player_name=self.nom_joueur)
        self.rank_widget.pack(fill="x", pady=(10, 0))

    # ---------------------------------------------
    # RÉCEPTION DES ÉVÉNEMENTS RÉSEAU
    # ---------------------------------------------
    def charger_question(self, data):
        """Appelé quand le serveur envoie 'party_question'."""
        self.question_courante = data.get("question", {})
        index = data.get("question_index", 0)
        total = data.get("total_questions", index)
        sujet = data.get("subject", "")
        difficulte = data.get("difficulty", "easy")

        self.a_repondu = False
        self.status_label.configure(text="")
        self.question_num_label.configure(text=f"Question {index} / {total}")
        self.subject_label.configure(text=f"📚 Sujet : {sujet}")

        badge_diff = {"easy": "🟢 Facile", "medium": "🟠 Moyen", "hard": "🔴 Difficile"}.get(difficulte, difficulte)
        self.difficulty_label.configure(text=badge_diff)

        self.question_label.configure(text=self.question_courante.get("question", "Question"))

        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons.clear()

        for lettre in ["A", "B", "C", "D"]:
            texte = self.question_courante.get(lettre, "")
            btn = ctk.CTkButton(
                self.options_frame, text=f"{lettre}.   {texte}", font=("Arial", 14),
                fg_color="#1c2541", hover_color="#3a506b", corner_radius=10, height=50, anchor="w",
                command=lambda l=lettre: self.repondre(l)
            )
            btn.pack(fill="x", pady=6)
            self.option_buttons.append(btn)

        parler(f"Question sur {sujet}")

        self.temps_debut_question = time.time()
        self.temps_total = int(self.question_courante.get("time", 20))
        self._demarrer_minuteur(self.temps_total)

    def _demarrer_minuteur(self, secondes):
        self.temps_restant = secondes
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self._tick_minuteur()

    def _tick_minuteur(self):
        self.timer_label.configure(text=f"⏳ {self.temps_restant}s")
        self.progress_bar.set(max(0.0, self.temps_restant / self.temps_total))

        if self.temps_restant <= 0:
            if not self.a_repondu:
                self.repondre(None)  # Temps écoulé sans réponse
            return

        self.temps_restant -= 1
        self.timer_job = self.after(1000, self._tick_minuteur)

    # ---------------------------------------------
    def repondre(self, lettre_choisie):
        if self.a_repondu or not self.question_courante:
            return
        self.a_repondu = True

        if self.timer_job:
            self.after_cancel(self.timer_job)

        for btn in self.option_buttons:
            btn.configure(state="disabled")

        bonne_reponse = self.question_courante.get("correct", "A")
        est_correct = (lettre_choisie == bonne_reponse)

        temps_ecoule = time.time() - (self.temps_debut_question or time.time())
        self.temps_reponses.append(temps_ecoule)

        if est_correct:
            ratio_temps = max(0.0, min(1.0, 1 - (temps_ecoule / max(self.temps_total, 1))))
            points = int(POINTS_BASE * (0.5 + 0.5 * ratio_temps))
            self.combo += 1
            self.status_label.configure(text=f"✅ Bonne réponse ! +{points} pts", text_color="#00E676")
        else:
            points = 0
            self.combo = 0
            self.status_label.configure(text=f"❌ Mauvaise réponse (bonne réponse : {bonne_reponse})", text_color="#FF5252")

        self.score_total += points
        avg_time = sum(self.temps_reponses) / len(self.temps_reponses) if self.temps_reponses else 0
        self.stats_label.configure(text=f"⚡ {self.score_total} pts  🔥 x{self.combo}")

        self.network.send_party_answer(
            self.pin, self.nom_joueur, est_correct, self.score_total, self.combo, round(avg_time, 1)
        )

    def mettre_a_jour_classement(self, data):
        """Reçoit le classement en direct (après CHAQUE réponse, de n'importe quel joueur)."""
        if isinstance(data, dict):
            joueurs = data.get("players", [])
            classement_widget = [
                {"rank": p.get("rank", i + 1), "name": p.get("name", "?"), "xp": p.get("score", 0)}
                for i, p in enumerate(joueurs)
            ]
            self.rank_widget.update_ranks(classement_widget)

    def afficher_fin_partie(self, data=None):
        """Reçoit 'quiz_ended' — affiche un résumé simple de fin de partie."""
        if self.timer_job:
            self.after_cancel(self.timer_job)

        # Crédite l'XP gagnée sur le compte connecté (mode "Questions entre amis")
        if session is not None and session.est_connecte():
            try:
                session.crediter_xp(self.score_total)
            except Exception as e:
                print(f"⚠️ Erreur lors du crédit d'XP (party) : {e}")

        message = None
        if isinstance(data, dict):
            message = data.get("message")

        for w in self.container.winfo_children():
            w.destroy()

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.pack(expand=True)

        ctk.CTkLabel(center, text="🏁", font=("Arial", 50)).pack(pady=(0, 10))
        ctk.CTkLabel(center, text="Partie terminée !", font=("Arial", 20, "bold"), text_color="#FFFFFF").pack()

        if message:
            ctk.CTkLabel(center, text=message, font=("Arial", 12, "italic"), text_color="#FFD700").pack(pady=(5, 0))

        ctk.CTkLabel(
            center, text=f"⚡ Score final : {self.score_total} pts",
            font=("Arial", 15, "bold"), text_color="#00E676"
        ).pack(pady=(15, 20))

        ctk.CTkButton(
            center, text="🏠 Retour à l'accueil", fg_color="#1F6AA5", hover_color="#144870",
            command=self.home_callback
        ).pack()

    # ---------------------------------------------
    def abandonner_partie(self):
        self.network.send_player_abandon(self.pin, self.nom_joueur)
        self.home_callback()

    def _on_destroy(self, event=None):
        # Sécurité : si la fenêtre se ferme brutalement pendant la partie
        pass
