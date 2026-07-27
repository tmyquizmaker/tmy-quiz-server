"""
===========================================
TMY Quiz Maker
Version 5.0

quiz_lobby.py - Salle d'attente Multijoueur Sans Démarrage Auto
===========================================
"""

import random
import customtkinter as ctk

class QuizLobbyPage(ctk.CTkFrame):

    def __init__(self, master, quiz_title="Mon Quiz", max_players=0, start_quiz_callback=None, back_callback=None, is_host=True):
        super().__init__(master, fg_color="#121620")

        self.quiz_title = quiz_title
        # 0 = Joueurs illimités
        self.max_players = max_players
        self.start_quiz_callback = start_quiz_callback
        self.back_callback = back_callback
        self.is_host = is_host  # Distinguer si la vue appartient à l'hôte ou à un élève

        # Génération du Game PIN uniquement si hôte, sinon sera mis à jour par l'app
        self.game_pin = f"{random.randint(100, 999)} {random.randint(100, 999)}"
        
        # Liste des joueurs connectés
        self.players = []

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=30, pady=20)

        self.create_interface()

    def create_interface(self):
        # ---------------------------------------------
        # 1. EN-TÊTE
        # ---------------------------------------------
        self.header = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.header.pack(fill="x", pady=(0, 15), ipady=5)

        self.head_content = ctk.CTkFrame(self.header, fg_color="transparent")
        self.head_content.pack(fill="x", padx=20, pady=10)

        self.title_lbl = ctk.CTkLabel(
            self.head_content, text=f"👥 SALLE EN DIRECT : {self.quiz_title.upper()}",
            font=("Arial", 18, "bold"), text_color="#FFFFFF"
        )
        self.title_lbl.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            self.head_content, text="🟢 Salle Ouverte",
            font=("Arial", 11, "bold"), text_color="#00E676"
        )
        self.status_badge.pack(side="right")

        # ---------------------------------------------
        # 2. ZONE CENTRALE (2 Colonnes)
        # ---------------------------------------------
        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(fill="both", expand=True, pady=(0, 15))

        # === GAUCHE: CODE PIN & PARAMS ===
        self.left_col = ctk.CTkFrame(self.body, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.pin_box = ctk.CTkFrame(self.left_col, fg_color="#121620", corner_radius=12, border_width=1, border_color="#1F6AA5")
        self.pin_box.pack(fill="x", padx=20, pady=20)

        self.pin_title = ctk.CTkLabel(self.pin_box, text="CODE DE LA SALLE (PIN)", font=("Arial", 10, "bold"), text_color="#AAAAAA")
        self.pin_title.pack(pady=(10, 2))

        self.pin_code = ctk.CTkLabel(self.pin_box, text=self.game_pin, font=("Arial", 34, "bold"), text_color="#FFD700")
        self.pin_code.pack(pady=(0, 10))

        capa_text = "Illimité" if self.max_players == 0 else f"{self.max_players} étudiants max"
        params_text = (
            f"• Capacité : {capa_text}\n"
            "• Démarrage : Contrôlé manuellement par l'hôte\n"
            "• Mode : En direct avec Classement Temps Réel"
        )
        self.params_info = ctk.CTkLabel(self.left_col, text=params_text, font=("Arial", 11), text_color="#8A8F9E", justify="left")
        self.params_info.pack(anchor="w", padx=20, pady=10)

        # === DROITE: LISTE ÉTUDIANTS REJOINTS ===
        self.right_col = ctk.CTkFrame(self.body, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.players_header = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.players_header.pack(fill="x", padx=20, pady=15)

        self.players_title = ctk.CTkLabel(self.players_header, text="ÉTUDIANTS REJOINTS", font=("Arial", 13, "bold"), text_color="#FFFFFF")
        self.players_title.pack(side="left")

        self.count_lbl = ctk.CTkLabel(self.players_header, text=self.get_count_string(), font=("Arial", 13, "bold"), text_color="#1F6AA5")
        self.count_lbl.pack(side="right")

        self.players_list_frame = ctk.CTkScrollableFrame(self.right_col, fg_color="transparent")
        self.players_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # ---------------------------------------------
        # 3. BARRE INFÉRIEURE
        # ---------------------------------------------
        self.bottom_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.bottom_bar.pack(fill="x", ipady=5)

        if self.back_callback:
            self.back_btn = ctk.CTkButton(
                self.bottom_bar, text="← Quitter", width=100, fg_color="#2B2D42",
                hover_color="#3A3D52", command=self.back_callback
            )
            self.back_btn.pack(side="left", padx=20, pady=10)

        # Affiche le bouton de lancement SEULEMENT si c'est l'hôte
        if self.is_host:
            self.start_btn = ctk.CTkButton(
                self.bottom_bar, text="▶ LANCER LE QUIZ MAINTENANT",
                font=("Arial", 13, "bold"), fg_color="#2E7D32", hover_color="#1E4620",
                height=45, command=self.launch_quiz
            )
            self.start_btn.pack(side="right", padx=20, pady=10)
        else:
            # Pour l'élève, on affiche un message d'attente
            self.waiting_lbl = ctk.CTkLabel(
                self.bottom_bar, text="⏳ En attente du lancement par l'hôte...",
                font=("Arial", 12, "bold", "italic"), text_color="#FFD700"
            )
            self.waiting_lbl.pack(side="right", padx=20, pady=10)

        self.update_players_ui()

    def get_count_string(self):
        if self.max_players == 0:
            return f"({len(self.players)} connectés)"
        return f"({len(self.players)}/{self.max_players})"

    def add_player(self, player_name):
        """Ajoute un joueur entré via la modale"""
        if self.max_players == 0 or len(self.players) < self.max_players:
            if player_name not in self.players:
                self.players.append(player_name)
                self.update_players_ui()

    def set_players(self, players_list):
        """Remplace la liste par la liste COMPLÈTE envoyée par le serveur,
        pour que chaque client soit synchronisé peu importe son ordre d'arrivée."""
        self.players = list(dict.fromkeys(players_list))  # garde l'ordre, sans doublons
        self.update_players_ui()

    def update_players_ui(self):
        for w in self.players_list_frame.winfo_children():
            w.destroy()

        self.count_lbl.configure(text=self.get_count_string())

        if not self.players:
            lbl = ctk.CTkLabel(self.players_list_frame, text="En attente des étudiants...", font=("Arial", 12), text_color="#AAAAAA")
            lbl.pack(pady=20)
            return

        for p in self.players:
            card = ctk.CTkFrame(self.players_list_frame, fg_color="#121620", corner_radius=8)
            card.pack(fill="x", pady=4)

            # Extraire les initiales/acronyme pour le badge d'avatar
            initials = "".join([part[0].upper() for part in p.split()[:2]]) or "🎓"
            avatar = ctk.CTkLabel(card, text=initials, width=32, height=32, fg_color="#1F6AA5", corner_radius=16, font=("Arial", 10, "bold"), text_color="#FFFFFF")
            avatar.pack(side="left", padx=(10, 5), pady=6)

            lbl = ctk.CTkLabel(card, text=f"  {p}", font=("Arial", 12, "bold"), text_color="#FFFFFF")
            lbl.pack(side="left", padx=5)

    def launch_quiz(self):
        """Lancement manuel par l'hôte uniquement"""
        if self.is_host and self.start_quiz_callback:
            self.start_quiz_callback()