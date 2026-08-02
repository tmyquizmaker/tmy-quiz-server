"""
Page de choix entre créer un nouveau quiz manuel (côté hôte) ou rejoindre
une salle existante avec un code PIN (côté élève) — remplace l'ancien
bouton "CRÉER MANUELLEMENT" isolé et le bouton "REJOINDRE" du pied de page.
"""
import customtkinter as ctk

BG = "#121620"
CARD = "#1E222D"
BORDER = "#2B303C"
BTN_NEUTRAL = "#2B2D42"
BTN_NEUTRAL_HOVER = "#3A3D52"


class ManualQuizChoicePage(ctk.CTkFrame):
    def __init__(self, master, create_callback, join_callback, back_callback):
        super().__init__(master, fg_color=BG)
        self.create_callback = create_callback
        self.join_callback = join_callback
        self.back_callback = back_callback

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkButton(
            header, text="← Retour", width=100, fg_color=BTN_NEUTRAL,
            hover_color=BTN_NEUTRAL_HOVER, command=self.back_callback,
        ).pack(side="left")

        ctk.CTkLabel(self, text="🎓 Mode Classe", font=("Arial", 22, "bold"), text_color="#FFFFFF").pack(pady=(15, 4))
        ctk.CTkLabel(
            self, text="Crée ton propre quiz, ou rejoins une salle déjà lancée",
            font=("Arial", 13), text_color="#9AA0B4",
        ).pack(pady=(0, 30))

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True)

        self._carte(
            grid, icon="✍️", titre="Créer un quiz",
            desc="Rédige tes propres questions, réponses et minuteurs, puis génère un code PIN pour ta salle.",
            btn_text="CRÉER", btn_color="#1F6AA5", hover_color="#144870",
            command=self.create_callback, col=0,
        )
        self._carte(
            grid, icon="🔑", titre="Rejoindre une salle",
            desc="Entre le code PIN donné par l'hôte pour rejoindre sa salle et jouer en direct.",
            btn_text="REJOINDRE", btn_color="#008080", hover_color="#004D4D",
            command=self.join_callback, col=1,
        )

    def _carte(self, parent, icon, titre, desc, btn_text, btn_color, hover_color, command, col):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER, width=280)
        card.grid(row=0, column=col, padx=15, pady=10, sticky="n")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=25, pady=25)

        ctk.CTkLabel(inner, text=icon, font=("Arial", 36)).pack(pady=(0, 10))
        ctk.CTkLabel(inner, text=titre, font=("Arial", 15, "bold"), text_color="#FFFFFF").pack(pady=(0, 6))
        ctk.CTkLabel(inner, text=desc, font=("Arial", 11), text_color="#AAAAAA", wraplength=220, justify="center").pack(pady=(0, 16))

        ctk.CTkButton(
            inner, text=btn_text, font=("Arial", 12, "bold"), width=200, height=40,
            fg_color=btn_color, hover_color=hover_color, command=command,
        ).pack()
