"""
===========================================
TMY Quiz Maker
Version 5.2

leaderboard_overlay.py - Affichage des rangs en direct (Élève & Créateur)
===========================================
"""

import customtkinter as ctk


class StudentRankWidget(ctk.CTkFrame):
    """Carte compacte de classement en direct : médailles pour le Top 3
    + le rang de l'utilisateur courant s'il n'y figure pas."""

    MEDAILLES = {1: "🥇", 2: "🥈", 3: "🥉"}
    ACCENTS = {1: "#FFD700", 2: "#C7CDD8", 3: "#D08A4C"}
    ACCENT_MOI = "#00B4D8"
    ACCENT_DEFAUT = "#3A3F4E"

    def __init__(self, master, current_player_name="Moi"):
        super().__init__(
            master,
            fg_color="#161A24",
            corner_radius=14,
            border_width=1,
            border_color="#252A38",
        )
        self.current_player_name = current_player_name
        self._rows_cache = []  # Pour réutiliser les widgets sans détruire l'UI

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            header,
            text="🔥 QUI PREND LA TÊTE ?",
            font=("Arial", 12, "bold"),
            text_color="#FFD700",
        ).pack(side="left")

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="⏳ Le duel commence bientôt...",
            font=("Arial", 10, "italic"),
            text_color="#6B7280",
        )

    def update_ranks(self, leaderboard_data):
        """
        leaderboard_data format:
        [{"rank": 1, "name": "Jean", "xp": 1200}, ...]
        """
        if not leaderboard_data:
            self._clear_rows()
            self.empty_label.pack(pady=6)
            return

        self.empty_label.pack_forget()

        # Construction de la liste des joueurs à afficher (Top 3 + joueur courant si hors top 3)
        top_3 = leaderboard_data[:3]
        display_list = list(top_3)

        player_in_top_3 = any(
            p["name"] == self.current_player_name for p in top_3
        )

        if not player_in_top_3:
            my_data = next(
                (
                    p
                    for p in leaderboard_data
                    if p["name"] == self.current_player_name
                ),
                None,
            )
            if my_data:
                display_list.append(
                    {"is_separator": True}
                )  # Indicateur de séparateur
                display_list.append(my_data)

        # Ajustement du nombre de lignes en cache
        self._sync_rows_cache(len(display_list))

        # Mise à jour des widgets existants sans les détruire
        for idx, item in enumerate(display_list):
            widgets = self._rows_cache[idx]
            frame, badge, name_lbl, xp_lbl, sep_label = (
                widgets["frame"],
                widgets["badge"],
                widgets["name_lbl"],
                widgets["xp_lbl"],
                widgets["sep_label"],
            )

            if item.get("is_separator"):
                frame.pack_forget()
                sep_label.pack(pady=2)
                continue

            sep_label.pack_forget()

            rang = item.get("rank", idx + 1)
            is_me = item["name"] == self.current_player_name
            medaille = self.MEDAILLES.get(rang, f"#{rang}")
            accent = self.ACCENT_MOI if is_me else self.ACCENTS.get(rang, self.ACCENT_DEFAUT)

            frame.configure(
                fg_color="#1B2E3D" if is_me else "#1B1F2B",
                border_color=accent,
                border_width=2 if (rang in self.MEDAILLES or is_me) else 1,
            )
            badge.configure(text=medaille, text_color=accent)

            nom_affiche = item["name"] + ("  •  Toi" if is_me else "")
            name_lbl.configure(
                text=nom_affiche,
                text_color="#FFFFFF" if (is_me or rang in self.MEDAILLES) else "#C4C9D4",
            )
            xp_lbl.configure(text=f"{item.get('xp', 0)} XP")

            frame.pack(fill="x", pady=3)

    def _sync_rows_cache(self, required_count):
        """Ajuste le nombre de conteneurs de lignes réutilisables."""
        while len(self._rows_cache) < required_count:
            row_frame = ctk.CTkFrame(
                self.list_frame,
                fg_color="#1B1F2B",
                corner_radius=8,
                border_width=1,
                border_color="#2B303C",
                height=34,
            )
            row_frame.pack_propagate(False)

            badge = ctk.CTkLabel(
                row_frame, text="", font=("Arial", 13, "bold"), width=24,
            )
            badge.pack(side="left", padx=(10, 6))

            name_lbl = ctk.CTkLabel(
                row_frame,
                text="",
                font=("Arial", 11, "bold"),
                text_color="#FFFFFF",
                anchor="w",
            )
            name_lbl.pack(side="left", fill="x", expand=True)

            xp_lbl = ctk.CTkLabel(
                row_frame, text="", font=("Arial", 10, "bold"), text_color="#FFD700"
            )
            xp_lbl.pack(side="right", padx=10)

            sep_label = ctk.CTkLabel(
                self.list_frame,
                text="⋯",
                font=("Arial", 10, "bold"),
                text_color="#4B5563",
            )

            self._rows_cache.append(
                {
                    "frame": row_frame,
                    "badge": badge,
                    "name_lbl": name_lbl,
                    "xp_lbl": xp_lbl,
                    "sep_label": sep_label,
                }
            )

        # Cacher les lignes excédentaires
        for idx in range(required_count, len(self._rows_cache)):
            self._rows_cache[idx]["frame"].pack_forget()
            self._rows_cache[idx]["sep_label"].pack_forget()

    def _clear_rows(self):
        for w in self._rows_cache:
            w["frame"].pack_forget()
            w["sep_label"].pack_forget()


class TeacherFullDashboard(ctk.CTkFrame):
    """Tableau de bord complet réservé au créateur (Nom, Points, Combo, Temps Moyen)."""

    def __init__(self, master):
        super().__init__(
            master,
            fg_color="#121620",
            corner_radius=15,
            border_width=1,
            border_color="#2B303C",
        )
        self._rows_cache = []

        ctk.CTkLabel(
            self,
            text="📊 TABLEAU DE BORD DU CRÉATEUR",
            font=("Arial", 13, "bold"),
            text_color="#FFFFFF",
        ).pack(pady=10)

        # En-têtes
        headers = ctk.CTkFrame(self, fg_color="#1E222D")
        headers.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(
            headers,
            text="Rang",
            width=45,
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA",
        ).pack(side="left", padx=2)
        ctk.CTkLabel(
            headers,
            text="Nom",
            width=110,
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA",
            anchor="w",
        ).pack(side="left", padx=2)
        ctk.CTkLabel(
            headers,
            text="Points",
            width=65,
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA",
        ).pack(side="left", padx=2)
        ctk.CTkLabel(
            headers,
            text="Combo",
            width=55,
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA",
        ).pack(side="left", padx=2)
        ctk.CTkLabel(
            headers,
            text="Temps Moy.",
            width=75,
            font=("Arial", 10, "bold"),
            text_color="#AAAAAA",
        ).pack(side="left", padx=2)

        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=8, pady=5)

        self.empty_label = ctk.CTkLabel(
            self.table_scroll,
            text="Aucun joueur connecté",
            font=("Arial", 11, "italic"),
            text_color="#AAAAAA",
        )

    def update_dashboard(self, players_full_data):
        """
        players_full_data format (déjà calculé par le serveur, avec égalités) :
        [{"rank": 1, "name": "Jean", "score": 30, "combo": 2, "avg_time": 8.5}, ...]
        """
        if not players_full_data:
            self._hide_all_rows()
            self.empty_label.pack(pady=20)
            return

        self.empty_label.pack_forget()
        self._sync_rows_cache(len(players_full_data))

        for idx, p in enumerate(players_full_data):
            row_widgets = self._rows_cache[idx]

            rang = p.get("rank", idx + 1)
            rank_str = f"{rang}er" if rang == 1 else f"{rang}e"

            row_widgets["lbl_rank"].configure(text=rank_str)
            row_widgets["lbl_name"].configure(text=p.get("name", "?"))
            row_widgets["lbl_xp"].configure(text=f"{p.get('score', 0)} pts")
            row_widgets["lbl_combo"].configure(text=f"🔥 x{p.get('combo', 0)}")
            temps = p.get("avg_time", 0)
            row_widgets["lbl_time"].configure(text=f"{temps}s" if temps else "--")

            row_widgets["frame"].pack(fill="x", pady=2)

    def _sync_rows_cache(self, required_count):
        while len(self._rows_cache) < required_count:
            row = ctk.CTkFrame(
                self.table_scroll, fg_color="#1E222D", corner_radius=6
            )

            lbl_rank = ctk.CTkLabel(
                row,
                text="",
                width=45,
                font=("Arial", 10, "bold"),
                text_color="#FFD700",
            )
            lbl_rank.pack(side="left", padx=2, pady=5)

            lbl_name = ctk.CTkLabel(
                row,
                text="",
                width=110,
                font=("Arial", 10, "bold"),
                text_color="#FFFFFF",
                anchor="w",
            )
            lbl_name.pack(side="left", padx=2)

            lbl_xp = ctk.CTkLabel(
                row,
                text="",
                width=65,
                font=("Arial", 10),
                text_color="#00E676",
            )
            lbl_xp.pack(side="left", padx=2)

            lbl_combo = ctk.CTkLabel(
                row,
                text="",
                width=55,
                font=("Arial", 10),
                text_color="#FF9800",
            )
            lbl_combo.pack(side="left", padx=2)

            lbl_time = ctk.CTkLabel(
                row,
                text="",
                width=75,
                font=("Arial", 10),
                text_color="#AAAAAA",
            )
            lbl_time.pack(side="left", padx=2)

            self._rows_cache.append(
                {
                    "frame": row,
                    "lbl_rank": lbl_rank,
                    "lbl_name": lbl_name,
                    "lbl_xp": lbl_xp,
                    "lbl_combo": lbl_combo,
                    "lbl_time": lbl_time,
                }
            )

        for idx in range(required_count, len(self._rows_cache)):
            self._rows_cache[idx]["frame"].pack_forget()

    def _hide_all_rows(self):
        for r in self._rows_cache:
            r["frame"].pack_forget()
