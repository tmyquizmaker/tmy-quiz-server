"""
===========================================
TMY Quiz Maker
Version 5.1

leaderboard_overlay.py - Affichage des rangs en direct (Élève & Créateur)
===========================================
"""

import customtkinter as ctk


class StudentRankWidget(ctk.CTkFrame):
    """Affiche le Top 3 et le rang actuel du joueur s'il est au-delà du rang 3."""

    def __init__(self, master, current_player_name="Moi"):
        super().__init__(
            master,
            fg_color="#1E222D",
            corner_radius=12,
            border_width=1,
            border_color="#2B303C",
        )
        self.current_player_name = current_player_name
        self._rows_cache = []  # Pour réutiliser les widgets sans détruire l'UI

        ctk.CTkLabel(
            self,
            text="🏆 RANG EN DIRECT",
            font=("Arial", 11, "bold"),
            text_color="#FFD700",
        ).pack(pady=(8, 4), padx=12)

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="En attente des résultats...",
            font=("Arial", 10, "italic"),
            text_color="#AAAAAA",
        )

    def update_ranks(self, leaderboard_data):
        """
        leaderboard_data format:
        [{"rank": 1, "name": "Jean", "xp": 1200}, ...]
        """
        if not leaderboard_data:
            self._clear_rows()
            self.empty_label.pack(pady=4)
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
            frame, left_label, right_label, sep_label = (
                widgets["frame"],
                widgets["left_label"],
                widgets["right_label"],
                widgets["sep_label"],
            )

            if item.get("is_separator"):
                frame.pack_forget()
                sep_label.pack(pady=1)
            else:
                sep_label.pack_forget()
                is_me = item["name"] == self.current_player_name
                bg_col = "#1F6AA5" if is_me else "#121620"
                frame.configure(fg_color=bg_col)

                rank_suffix = "er" if item["rank"] == 1 else "ème"
                name_suffix = " (Moi)" if is_me else ""
                rank_str = f"{item['rank']}{rank_suffix} {item['name']}{name_suffix}"

                left_label.configure(text=rank_str)
                right_label.configure(text=f"{item['xp']} XP")
                frame.pack(fill="x", pady=2)

    def _sync_rows_cache(self, required_count):
        """Ajuste le nombre de conteneurs de lignes réutilisables."""
        while len(self._rows_cache) < required_count:
            row_frame = ctk.CTkFrame(
                self.list_frame, fg_color="#121620", corner_radius=6
            )
            lbl_left = ctk.CTkLabel(
                row_frame,
                text="",
                font=("Arial", 10, "bold"),
                text_color="#FFFFFF",
            )
            lbl_left.pack(side="left", padx=8, pady=4)

            lbl_right = ctk.CTkLabel(
                row_frame, text="", font=("Arial", 10), text_color="#FFD700"
            )
            lbl_right.pack(side="right", padx=8)

            lbl_sep = ctk.CTkLabel(
                self.list_frame,
                text="• • •",
                font=("Arial", 8),
                text_color="#AAAAAA",
            )

            self._rows_cache.append(
                {
                    "frame": row_frame,
                    "left_label": lbl_left,
                    "right_label": lbl_right,
                    "sep_label": lbl_sep,
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
    """Tableau de bord complet réservé au créateur (Nom, XP, Combo, Temps Moyen)."""

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
            text="XP",
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
        players_full_data format:
        [{"rank": 1, "name": "Jean", "xp": 1200, "combo": 4, "avg_time": "2.1s"}, ...]
        """
        if not players_full_data:
            self._hide_all_rows()
            self.empty_label.pack(pady=20)
            return

        self.empty_label.pack_forget()
        self._sync_rows_cache(len(players_full_data))

        for idx, p in enumerate(players_full_data):
            row_widgets = self._rows_cache[idx]

            rank_str = f"{p['rank']}er" if p["rank"] == 1 else f"{p['rank']}e"

            row_widgets["lbl_rank"].configure(text=rank_str)
            row_widgets["lbl_name"].configure(text=p["name"])
            row_widgets["lbl_xp"].configure(text=f"{p['xp']} XP")
            row_widgets["lbl_combo"].configure(text=f"🔥 x{p['combo']}")
            row_widgets["lbl_time"].configure(text=p["avg_time"])

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