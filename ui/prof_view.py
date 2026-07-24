import customtkinter as ctk
from leaderboard_overlay import TeacherFullDashboard

class ProfView(ctk.CTkFrame):
    def __init__(self, master, socket_client=None):
        super().__init__(master, fg_color="#121620")
        self.master = master
        self.socket_client = socket_client  # Référence au réseau/socket pour l'envoi d'ordres
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self._build_ui()

    def _build_ui(self):
        # Titre de la vue Professeur
        title = ctk.CTkLabel(self, text="👨‍🏫 ESPACE PROFESSEUR / HÔTE", font=("Arial", 18, "bold"), text_color="#FFFFFF")
        title.pack(pady=(0, 15))

        # Intégration du Tableau de Bord Complet (leaderboard_overlay.py)
        self.dashboard = TeacherFullDashboard(self)
        self.dashboard.pack(fill="both", expand=True, pady=10)

        # Panneau de contrôle du Professeur
        control_frame = ctk.CTkFrame(self, fg_color="#1E222D", corner_radius=12)
        control_frame.pack(fill="x", pady=(10, 0), ipady=10)

        # Bouton "Question Suivante"
        self.btn_next_question = ctk.CTkButton(
            control_frame,
            text="⏭️ Question Suivante",
            font=("Arial", 14, "bold"),
            fg_color="#1F6AA5",
            hover_color="#144870",
            corner_radius=8,
            height=40,
            command=self.on_click_next_question
        )
        self.btn_next_question.pack(padx=20, pady=10)

    def on_click_next_question(self):
        """Action au clic sur le bouton 'Question Suivante'"""
        print("[ProfView] Bouton 'Question Suivante' cliqué.")
        
        # Exemple d'envoi de signal via réseau/socket au serveur
        if self.socket_client:
            self.socket_client.send({"action": "NEXT_QUESTION"})
        
        # (Optionnel) Désactiver temporairement le bouton pour éviter le double-clic
        self.btn_next_question.configure(state="disabled")

    def update_dashboard_data(self, players_data):
        """Met à jour les classements réels reçus du serveur"""
        self.dashboard.update_dashboard(players_data)
        # Réactive le bouton une fois la nouvelle question lancée si besoin
        self.btn_next_question.configure(state="normal")