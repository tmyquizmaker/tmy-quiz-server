import customtkinter as ctk
from auth_client import session

BG = "#121620"
CARD = "#1E222D"
BORDER = "#2B303C"
NEUTRAL = "#2B2D42"
NEUTRAL_HOVER = "#3A3D52"
ACCENT_TEAL = "#008080"
ACCENT_TEAL_HOVER = "#004D4D"


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, back_callback, account_callback):
        super().__init__(master, fg_color=BG)
        self.back_callback = back_callback
        self.account_callback = account_callback

        # --- En-tête ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkButton(
            header, text="← Retour", width=100, fg_color=NEUTRAL,
            hover_color=NEUTRAL_HOVER, command=self.back_callback,
        ).pack(side="left")

        ctk.CTkLabel(
            self, text="⚙️  Paramètres", font=("Arial", 22, "bold"), text_color="#FFFFFF"
        ).pack(pady=(10, 25))

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=60, pady=0, fill="x")

        # --- Carte Statistiques ---
        stats_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        stats_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            stats_card, text="📊  Statistiques", font=("Arial", 15, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=25, pady=(20, 12))

        stats_row = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=25, pady=(0, 22))

        self.total_label = self._stat_box(stats_row, "—", "Parties jouées")
        self.best_label = self._stat_box(stats_row, "—", "Meilleur score")

        self._charger_stats()

        # --- Carte Compte ---
        account_card = ctk.CTkFrame(container, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        account_card.pack(fill="x")

        row = ctk.CTkFrame(account_card, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=20)

        user = session.user or {}
        ctk.CTkLabel(
            row, text=f"👤  @{user.get('username', '')}",
            font=("Arial", 14, "bold"), text_color="#FFFFFF",
        ).pack(side="left")

        ctk.CTkButton(
            row, text="Compte", font=("Arial", 12, "bold"),
            fg_color=ACCENT_TEAL, hover_color=ACCENT_TEAL_HOVER, width=120, height=36,
            corner_radius=10, command=self.account_callback,
        ).pack(side="right")

    def _stat_box(self, parent, valeur, label):
        box = ctk.CTkFrame(parent, fg_color=BG, corner_radius=12)
        box.pack(side="left", expand=True, fill="x", padx=(0, 12))
        val_lbl = ctk.CTkLabel(box, text=valeur, font=("Arial", 24, "bold"), text_color="#FFFFFF")
        val_lbl.pack(pady=(16, 2))
        ctk.CTkLabel(box, text=label, font=("Arial", 11), text_color="#AAAAAA").pack(pady=(0, 16))
        return val_lbl

    def _charger_stats(self):
        succes, resultat = session.recuperer_stats()
        if succes:
            self.total_label.configure(text=str(resultat.get("total_parties", 0)))
            self.best_label.configure(text=str(resultat.get("meilleur_score", 0)))
        else:
            self.total_label.configure(text="0")
            self.best_label.configure(text="0")
