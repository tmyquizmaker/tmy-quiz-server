import customtkinter as ctk
from leaderboard_overlay import StudentRankWidget

class StudentView(ctk.CTkFrame):
    def __init__(self, master, current_player_name="Élève", socket_client=None):
        super().__init__(master, fg_color="#121620")
        self.master = master
        self.current_player_name = current_player_name
        self.socket_client = socket_client
        self.option_buttons = []

        self.pack(fill="both", expand=True, padx=20, pady=20)
        self._build_ui()

    def _build_ui(self):
        # Header avec Widget de Rang en Direct (top 3)
        self.rank_widget = StudentRankWidget(self, current_player_name=self.current_player_name)
        self.rank_widget.pack(fill="x", pady=(0, 15))

        # Libellé de la question
        self.question_label = ctk.CTkLabel(
            self, 
            text="En attente du lancement de la question...", 
            font=("Arial", 16, "bold"), 
            text_color="#FFFFFF",
            wraplength=400
        )
        self.question_label.pack(pady=15)

        # Zone pour afficher l'état d'attente (masqué par défaut)
        self.status_label = ctk.CTkLabel(
            self, 
            text="", 
            font=("Arial", 13, "italic"), 
            text_color="#FFD700"
        )
        self.status_label.pack(pady=5)

        # Conteneur des options de réponse
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(fill="both", expand=True, pady=10)

    def load_question(self, question_data):
        """
        Appelé lors de la réception du signal 'NEW_QUESTION' par le serveur.
        Réinitialise l'interface et affiche la nouvelle question.
        """
        # 1. Effacer l'état d'attente
        self.status_label.configure(text="")
        
        # 2. Mettre à jour l'intitulé
        self.question_label.configure(text=question_data.get("question", "Question"))

        # 3. Supprimer les anciens boutons d'options
        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons.clear()

        # 4. Générer les nouveaux boutons d'options
        options = question_data.get("options", [])
        for idx, option_text in enumerate(options):
            btn = ctk.CTkButton(
                self.options_frame,
                text=option_text,
                font=("Arial", 13),
                fg_color="#1F6AA5",
                hover_color="#144870",
                corner_radius=8,
                height=45,
                command=lambda opt=option_text: self.submit_answer(opt)
            )
            btn.pack(fill="x", pady=5)
            self.option_buttons.append(btn)

    def submit_answer(self, selected_option):
        """Action déclenchée lors du clic sur une réponse."""
        # 1. Bloquer / Désactiver tous les boutons de réponse
        for btn in self.option_buttons:
            btn.configure(state="disabled")

        # 2. Afficher le message d'attente du professeur
        self.status_label.configure(text="⏳ Reponse enregistrée. En attente du professeur...")

        # 3. Envoyer la réponse au serveur
        if self.socket_client:
            self.socket_client.send({
                "action": "SUBMIT_ANSWER",
                "player": self.current_player_name,
                "answer": selected_option
            })

    def update_leaderboard(self, leaderboard_data):
        """Met à jour le Top 3 et le rang via le widget dédié"""
        self.rank_widget.update_ranks(leaderboard_data)