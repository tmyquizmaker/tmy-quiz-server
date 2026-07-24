"""
===========================================
TMY Quiz Maker
Version 5.0

leaderboard_overlay.py - Affichage des rangs en direct (Élève & Créateur)
===========================================
"""

import customtkinter as ctk

class StudentRankWidget(ctk.CTkFrame):
    """Affiche le Top 3 (1er, 2ème, 3ème) et le rang du joueur pendant le quiz"""

    def __init__(self, master, current_player_name="Moi"):
        super().__init__(master, fg_color="#1E222D", corner_radius=12, border_width=1, border_color="#2B303C")
        self.current_player_name = current_player_name

        ctk.CTkLabel(self, text="🏆 RANG EN DIRECT", font=("Arial", 11, "bold"), text_color="#FFD700").pack(pady=(8, 4), padx=12)

        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="x", padx=8, pady=(0, 8))

    def update_ranks(self, leaderboard_data):
        """
        leaderboard_data format:
        [{"rank": 1, "name": "Jean", "xp": 1200}, ...]
        """
        for w in self.list_frame.winfo_children():
            w.destroy()

        top_3 = leaderboard_data[:3]
        for p in top_3:
            is_me = p["name"] == self.current_player_name
            bg_col = "#1F6AA5" if is_me else "#121620"

            row = ctk.CTkFrame(self.list_frame, fg_color=bg_col, corner_radius=6)
            row.pack(fill="x", pady=2)

            rank_text = f"{p['rank']}er" if p['rank'] == 1 else f"{p['rank']}ème"
            ctk.CTkLabel(row, text=f"{rank_text} {p['name']}", font=("Arial", 10, "bold"), text_color="#FFFFFF").pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(row, text=f"{p['xp']} XP", font=("Arial", 10), text_color="#FFD700").pack(side="right", padx=8)


class TeacherFullDashboard(ctk.CTkFrame):
    """Tableau de bord complet réservé au créateur (Nom, XP, Combo, Temps Moyen)"""

    def __init__(self, master):
        super().__init__(master, fg_color="#121620", corner_radius=15, border_width=1, border_color="#2B303C")

        ctk.CTkLabel(self, text="📊 TABLEAU DE BORD DU CRÉATEUR", font=("Arial", 13, "bold"), text_color="#FFFFFF").pack(pady=10)

        # En-têtes
        headers = ctk.CTkFrame(self, fg_color="#1E222D")
        headers.pack(fill="x", padx=12, pady=2)

        ctk.CTkLabel(headers, text="Rang", width=45, font=("Arial", 10, "bold"), text_color="#AAAAAA").pack(side="left", padx=2)
        ctk.CTkLabel(headers, text="Nom", width=110, font=("Arial", 10, "bold"), text_color="#AAAAAA", anchor="w").pack(side="left", padx=2)
        ctk.CTkLabel(headers, text="XP", width=65, font=("Arial", 10, "bold"), text_color="#AAAAAA").pack(side="left", padx=2)
        ctk.CTkLabel(headers, text="Combo", width=55, font=("Arial", 10, "bold"), text_color="#AAAAAA").pack(side="left", padx=2)
        ctk.CTkLabel(headers, text="Temps Moy.", width=75, font=("Arial", 10, "bold"), text_color="#AAAAAA").pack(side="left", padx=2)

        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=8, pady=5)

    def update_dashboard(self, players_full_data):
        """
        players_full_data format:
        [{"rank": 1, "name": "Jean", "xp": 1200, "combo": 4, "avg_time": "2.1s"}, ...]
        """
        for w in self.table_scroll.winfo_children():
            w.destroy()

        for p in players_full_data:
            row = ctk.CTkFrame(self.table_scroll, fg_color="#1E222D", corner_radius=6)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=f"{p['rank']}e", width=45, font=("Arial", 10, "bold"), text_color="#FFD700").pack(side="left", padx=2, pady=5)
            ctk.CTkLabel(row, text=p['name'], width=110, font=("Arial", 10, "bold"), text_color="#FFFFFF", anchor="w").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{p['xp']} XP", width=65, font=("Arial", 10), text_color="#00E676").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"🔥 x{p['combo']}", width=55, font=("Arial", 10), text_color="#FF9800").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=p['avg_time'], width=75, font=("Arial", 10), text_color="#AAAAAA").pack(side="left", padx=2)