import customtkinter as ctk

class StudentView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#0b132b")
        self.controller = controller
        self.option_buttons = []

        # --- HEADER / EN-TÊTE ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", px=20, py=10)

        self.logo_label = ctk.CTkLabel(
            self.header_frame, 
            text="🎮 TMY QUIZ", 
            font=("Arial", 16, "bold"), 
            text_color="#00b4d8"
        )
        self.logo_label.pack(side="left")

        self.stats_label = ctk.CTkLabel(
            self.header_frame, 
            text="🏅 3ème  🔥 x1  ⚡ 1241 XP", 
            font=("Arial", 14, "bold"), 
            text_color="#ffd166"
        )
        self.stats_label.pack(side="right")

        # --- INFOS QUESTION & TIMER ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", px=20, py=(5, 0))

        self.question_num_label = ctk.CTkLabel(
            self.info_frame, 
            text="Question -- / --", 
            font=("Arial", 14, "bold"), 
            text_color="#ffffff"
        )
        self.question_num_label.pack(side="left")

        self.timer_label = ctk.CTkLabel(
            self.info_frame, 
            text="⏳ --s", 
            font=("Arial", 14, "bold"), 
            text_color="#4cc9f0"
        )
        self.timer_label.pack(side="right")

        # --- BARRE DE PROGRESSION ---
        self.progress_bar = ctk.CTkProgressBar(
            self, 
            progress_color="#00b4d8", 
            fg_color="#1c2541", 
            height=8
        )
        self.progress_bar.pack(fill="x", px=20, py=10)
        self.progress_bar.set(0.5)

        # --- INTITULÉ DE LA QUESTION ---
        self.question_card = ctk.CTkFrame(self, fg_color="#1c2541", corner_radius=12)
        self.question_card.pack(fill="x", px=20, py=15, ipady=20)

        self.question_label = ctk.CTkLabel(
            self.question_card, 
            text="En attente de la question...", 
            font=("Arial", 18, "bold"), 
            text_color="#ffffff",
            wraplength=600
        )
        self.question_label.pack(expand=True)

        # --- CONTENEUR DES BOUTONS D'OPTIONS ---
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(fill="both", expand=True, px=20, py=10)

        # --- LABEL DE STATUT (ex: "Réponse envoyée !") ---
        self.status_label = ctk.CTkLabel(
            self, 
            text="", 
            font=("Arial", 14, "italic"), 
            text_color="#4cc9f0"
        )
        self.status_label.pack(pady=10)

    # =========================================================================
    # MÉTHODES LOGIQUES
    # =========================================================================

    def load_question(self, question_data):
        """
        Chargement d'une nouvelle question reçue du serveur
        """
        # Réinitialisation
        self.status_label.configure(text="")

        # Mise à jour de l'intitulé
        self.question_label.configure(
            text=question_data.get("question", "Question")
        )

        # Suppression des anciens boutons de réponse
        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons.clear()

        # Génération des nouveaux boutons de réponse
        options = question_data.get("options", [])
        letters = ["A", "B", "C", "D", "E", "F"]

        for idx, option_text in enumerate(options):
            prefix = letters[idx] if idx < len(letters) else str(idx + 1)
            
            btn = ctk.CTkButton(
                self.options_frame,
                text=f"{prefix}.   {option_text}",
                font=("Arial", 14),
                fg_color="#1c2541",
                hover_color="#3a506b",
                corner_radius=10,
                height=50,
                anchor="w",
                command=lambda opt=option_text: self.submit_answer(opt)
            )
            btn.pack(fill="x", pady=6)
            self.option_buttons.append(btn)

    def submit_answer(self, chosen_option):
        """
        Envoie la réponse de l'élève et désactive les choix
        """
        # Désactiver les boutons de réponse après le clic
        for btn in self.option_buttons:
            btn.configure(state="disabled")

        self.status_label.configure(text="🔒 Réponse enregistrée ! En attente du professeur...")

        # Transmettre la réponse au contrôleur réseau
        if hasattr(self.controller, "send_answer"):
            self.controller.send_answer(chosen_option)