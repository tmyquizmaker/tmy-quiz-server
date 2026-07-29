"""
===========================================
TMY Quiz Maker
levels_menu.py - Sélection du niveau du Mode Multijoueur (10 niveaux)
===========================================
"""

import customtkinter as ctk

LEVELS = [
    {
        "num": 1,
        "title": "Questions entre amis",
        "desc": "Crée une salle, invite tes amis, chacun propose son sujet.",
        "icon": "🎉",
        "color": "#8A2BE2",
        "unlocked": True,
    },
]

for _n in range(2, 11):
    LEVELS.append({
        "num": _n,
        "title": f"Niveau {_n}",
        "desc": "Bientôt disponible",
        "icon": "🔒",
        "color": "#3A3D52",
        "unlocked": False,
    })


class LevelsMenuPage(ctk.CTkFrame):
    """Grille des 10 niveaux du mode multijoueur. Seul le Niveau 1
    ('Questions entre amis') est jouable pour l'instant, les 9 autres
    sont affichés verrouillés (cadenas) en attendant leur développement."""

    def __init__(self, master, back_callback, level1_callback):
        super().__init__(master, fg_color="#121620")

        self.back_callback = back_callback
        self.level1_callback = level1_callback

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=30, pady=20)

        self._build_header()
        self._build_grid()

    # ---------------------------------------------
    def _build_header(self):
        top_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=12)
        top_bar.pack(fill="x", pady=(0, 20), ipady=8)

        ctk.CTkButton(
            top_bar, text="← Retour", width=100, fg_color="#2B2D42",
            hover_color="#3A3D52", command=self.back_callback
        ).pack(side="left", padx=15)

        title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=10)

        ctk.CTkLabel(
            title_frame, text="🌐 MODE MULTIJOUEUR — 10 NIVEAUX",
            font=("Arial", 17, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame, text="Choisis un niveau pour lancer une partie entre amis",
            font=("Arial", 11), text_color="#8A8F9E"
        ).pack(anchor="w")

    # ---------------------------------------------
    def _build_grid(self):
        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        cols = 5
        for i in range(cols):
            scroll.grid_columnconfigure(i, weight=1, uniform="lvl")

        for idx, lvl in enumerate(LEVELS):
            row, col = divmod(idx, cols)
            self._create_level_card(scroll, lvl, row, col)

    # ---------------------------------------------
    def _create_level_card(self, parent, lvl, row, col):
        unlocked = lvl["unlocked"]

        card = ctk.CTkFrame(
            parent,
            fg_color="#1E222D" if unlocked else "#181B24",
            corner_radius=16,
            border_width=1,
            border_color=lvl["color"] if unlocked else "#2B303C",
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=14, pady=16)

        badge = ctk.CTkFrame(
            content, fg_color=lvl["color"] if unlocked else "#2B2D42",
            corner_radius=25, width=50, height=50
        )
        badge.pack(pady=(0, 10))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=lvl["icon"], font=("Arial", 20)).pack(expand=True)

        ctk.CTkLabel(
            content, text=f"NIVEAU {lvl['num']}",
            font=("Arial", 9, "bold"),
            text_color=lvl["color"] if unlocked else "#666B7A",
        ).pack()

        ctk.CTkLabel(
            content, text=lvl["title"],
            font=("Arial", 12, "bold"),
            text_color="#FFFFFF" if unlocked else "#666B7A",
            wraplength=130, justify="center",
        ).pack(pady=(2, 6))

        ctk.CTkLabel(
            content, text=lvl["desc"],
            font=("Arial", 9), text_color="#8A8F9E" if unlocked else "#4E525E",
            wraplength=130, justify="center",
        ).pack(pady=(0, 10))

        if unlocked:
            ctk.CTkButton(
                content, text="JOUER", font=("Arial", 11, "bold"),
                height=32, fg_color=lvl["color"], hover_color=lvl["color"],
                corner_radius=8,
                command=self.level1_callback,
            ).pack(fill="x", side="bottom")
        else:
            ctk.CTkLabel(
                content, text="🔒 Verrouillé",
                font=("Arial", 10, "bold"), text_color="#4E525E",
            ).pack(side="bottom", pady=(0, 4))
