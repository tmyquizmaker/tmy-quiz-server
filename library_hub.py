import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from library_manager import LibraryManager
from data.quiz_storage import load_quizzes, delete_quiz  # Utilise le stockage officiel dans data/
from ui.history_detail_page import HistoryDetailPage

class LibraryHubWindow(ctk.CTkFrame):
    def __init__(self, master, app_controller=None, **kwargs):
        super().__init__(master, fg_color="#0f172a", **kwargs)  # Fond Sombre Premium (Slate 900)
        self.app_controller = app_controller

        # ----------------------------------------------------
        # BARRE D'EN-TÊTE / HEADER HAUT
        # ----------------------------------------------------
        self.header_bar = ctk.CTkFrame(self, fg_color="#1e293b", height=75, corner_radius=12)
        self.header_bar.pack(fill="x", padx=20, pady=(20, 10))

        # Bouton Retour (à gauche)
        if self.app_controller and hasattr(self.app_controller, "show_home"):
            self.btn_back = ctk.CTkButton(
                self.header_bar,
                text="← Accueil",
                font=("Roboto", 13, "bold"),
                fg_color="#334155",
                hover_color="#475569",
                width=100,
                height=38,
                corner_radius=8,
                command=self.app_controller.show_home
            )
            self.btn_back.pack(side="left", padx=15, pady=18)

        # Conteneur Logo + Titre (au centre / gauche)
        brand_frame = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        brand_frame.pack(side="left", padx=10, pady=10)

        # 🖼️ Chargement et Intégration du Logo
        logo_path = os.path.join("assets", "logo.png")  # Modifiez le chemin vers votre fichier image
        logo_image = self.load_logo(logo_path, size=(40, 40))

        if logo_image:
            self.logo_label = ctk.CTkLabel(brand_frame, image=logo_image, text="")
            self.logo_label.pack(side="left", padx=(0, 10))
        else:
            # Badge icône de secours si le logo n'est pas encore présent
            fallback_badge = ctk.CTkLabel(
                brand_frame,
                text="TMY",
                font=("Roboto", 12, "bold"),
                fg_color="#6366f1",
                text_color="#ffffff",
                corner_radius=6,
                width=38,
                height=38
            )
            fallback_badge.pack(side="left", padx=(0, 10))

        # Titre Principal
        self.title_label = ctk.CTkLabel(
            brand_frame,
            text="BIBLIOTHÈQUE HUB",
            font=("Roboto", 20, "bold"),
            text_color="#f8fafc"
        )
        self.title_label.pack(side="left")

        # ----------------------------------------------------
        # ONGLET STYLISÉ (TABVIEW)
        # ----------------------------------------------------
        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#1e293b",
            segmented_button_fg_color="#0f172a",
            segmented_button_selected_color="#6366f1",  # Accent violet indigo
            segmented_button_selected_hover_color="#4f46e5",
            segmented_button_unselected_color="#1e293b",
            segmented_button_unselected_hover_color="#334155",
            corner_radius=14
        )
        self.tabview.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Création des onglets
        self.tab_creations = self.tabview.add("🛠 Mes Créations")
        self.tab_history = self.tabview.add("📊 Historique des Parties")

        # Chargement Initial
        self.build_creations_tab()
        self.build_history_tab()

    def load_logo(self, logo_path, size=(40, 40)):
        """Charge une image de logo et la convertit en CTkImage."""
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            except Exception as e:
                print(f"Erreur lors du chargement du logo : {e}")
                return None
        return None

    # ====================================================
    # TAB 1 : MES CRÉATIONS
    # ====================================================
    def build_creations_tab(self):
        for widget in self.tab_creations.winfo_children():
            widget.destroy()

        top_bar = ctk.CTkFrame(self.tab_creations, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, 
            text="Vos Quiz créés et personnalisés", 
            font=("Roboto", 15, "bold"),
            text_color="#cbd5e1"
        ).pack(side="left")

        ctk.CTkButton(
            top_bar, 
            text="🗑 Tout supprimer", 
            fg_color="#ef4444", 
            hover_color="#dc2626",
            font=("Roboto", 12, "bold"),
            height=32,
            corner_radius=8,
            command=self.confirm_clear_creations
        ).pack(side="right")

        scroll_frame = ctk.CTkScrollableFrame(
            self.tab_creations, 
            fg_color="transparent",
            scrollbar_button_color="#334155"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Récupération de la liste réelle des quiz depuis data/quizzes.json
        creations = load_quizzes()
        creations = sorted(creations, key=self._parse_session_date, reverse=True)

        if not creations:
            empty_box = ctk.CTkFrame(scroll_frame, fg_color="#0f172a", corner_radius=12)
            empty_box.pack(fill="x", pady=40, padx=20)
            ctk.CTkLabel(
                empty_box, 
                text="📝 Aucun quiz disponible.\nCréez-en un nouveau depuis le menu principal !", 
                font=("Roboto", 14), 
                text_color="#94a3b8"
            ).pack(pady=30)
            return

        for quiz in creations:
            card = ctk.CTkFrame(scroll_frame, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#334155")
            card.pack(fill="x", pady=6, padx=5)

            title = quiz.get("title", "Quiz sans titre")
            q_count = len(quiz.get("questions", []))
            
            # Recherche flexible de la clé de date
            date_created = (
                quiz.get("created_at") or 
                quiz.get("date") or 
                quiz.get("created_date") or 
                quiz.get("timestamp") or 
                "Date inconnue"
            )

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=12, fill="both", expand=True)

            ctk.CTkLabel(
                info_frame, 
                text=title, 
                font=("Roboto", 15, "bold"), 
                text_color="#f8fafc",
                anchor="w"
            ).pack(fill="x")

            subtitle = f"❓ {q_count} Questions   |   📅 Créé le : {date_created}"
            ctk.CTkLabel(
                info_frame, 
                text=subtitle, 
                font=("Roboto", 12), 
                text_color="#94a3b8",
                anchor="w"
            ).pack(fill="x", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=10)

            ctk.CTkButton(
                btn_frame, text="▶ Lancer", fg_color="#22c55e", hover_color="#16a34a",
                font=("Roboto", 12, "bold"), width=85, height=34, corner_radius=6,
                command=lambda q=quiz: self.play_quiz(q)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_frame, text="✏️ Éditer", fg_color="#3b82f6", hover_color="#2563eb",
                font=("Roboto", 12, "bold"), width=85, height=34, corner_radius=6,
                command=lambda q=quiz: self.edit_quiz(q)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_frame, text="🗑", fg_color="#ef4444", hover_color="#dc2626",
                font=("Roboto", 12, "bold"), width=40, height=34, corner_radius=6,
                command=lambda q_id=quiz.get("id"): self.delete_single_creation(q_id)
            ).pack(side="left", padx=4)

    def delete_single_creation(self, quiz_id):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce quiz ?"):
            delete_quiz(quiz_id)
            self.build_creations_tab()

    def confirm_clear_creations(self):
        if messagebox.askyesno("Attention", "Voulez-vous supprimer TOUS vos quiz créés ?"):
            LibraryManager.delete_all_creations()
            self.build_creations_tab()

    def edit_quiz(self, quiz_data):
        if self.app_controller and hasattr(self.app_controller, "open_editor"):
            self.app_controller.open_editor(quiz_data)

    def play_quiz(self, quiz_data):
        if self.app_controller and hasattr(self.app_controller, "start_game"):
            self.app_controller.start_game(quiz_data)

    # ====================================================
    # TAB 2 : HISTORIQUE DES PARTIES
    # ====================================================
    def _parse_session_date(self, session):
        """Convertit la date d'une session en objet datetime, peu importe le format utilisé."""
        raw = (
            session.get("played_at") or
            session.get("date") or
            session.get("created_at") or
            session.get("timestamp") or
            ""
        )
        for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt)
            except (ValueError, TypeError):
                continue
        return datetime.min  # Dates illisibles envoyées tout en bas

    def build_history_tab(self):
        for widget in self.tab_history.winfo_children():
            widget.destroy()

        top_bar = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            top_bar, 
            text="Historique récent de vos sessions", 
            font=("Roboto", 15, "bold"),
            text_color="#cbd5e1"
        ).pack(side="left")

        ctk.CTkButton(
            top_bar, 
            text="🧹 Vider l'historique", 
            fg_color="#ef4444", 
            hover_color="#dc2626",
            font=("Roboto", 12, "bold"),
            height=32,
            corner_radius=8,
            command=self.confirm_clear_history
        ).pack(side="right")

        scroll_frame = ctk.CTkScrollableFrame(
            self.tab_history, 
            fg_color="transparent",
            scrollbar_button_color="#334155"
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        history = LibraryManager.get_history()
        history = sorted(history, key=self._parse_session_date, reverse=True)

        if not history:
            empty_box = ctk.CTkFrame(scroll_frame, fg_color="#0f172a", corner_radius=12)
            empty_box.pack(fill="x", pady=40, padx=20)
            ctk.CTkLabel(
                empty_box, 
                text="🎮 Aucune partie enregistrée dans l'historique.", 
                font=("Roboto", 14), 
                text_color="#94a3b8"
            ).pack(pady=30)
            return

        for session in history:
            card = ctk.CTkFrame(scroll_frame, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#334155")
            card.pack(fill="x", pady=6, padx=5)

            title = session.get("quiz_title", "Session Quiz")
            mode = session.get("mode", "Solo")
            date_played = (
                session.get("played_at") or 
                session.get("date") or 
                session.get("created_at") or 
                session.get("timestamp") or 
                "Date inconnue"
            )
            score = session.get("score", "0/0")

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=12, fill="both", expand=True)

            ctk.CTkLabel(
                info_frame, 
                text=f"{title}  ({mode})", 
                font=("Roboto", 15, "bold"), 
                text_color="#f8fafc",
                anchor="w"
            ).pack(fill="x")

            subtitle = f"🏆 Score : {score}   |   📅 Joué le : {date_played}"
            ctk.CTkLabel(
                info_frame, 
                text=subtitle, 
                font=("Roboto", 12), 
                text_color="#94a3b8",
                anchor="w"
            ).pack(fill="x", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15, pady=10)

            ctk.CTkButton(
                btn_frame, text="🔍 Détails", fg_color="#6366f1", hover_color="#4f46e5",
                font=("Roboto", 12, "bold"), width=95, height=34, corner_radius=6,
                command=lambda s=session: self.show_session_details(s)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                btn_frame, text="🗑", fg_color="#ef4444", hover_color="#dc2626",
                font=("Roboto", 12, "bold"), width=40, height=34, corner_radius=6,
                command=lambda s_id=session.get("session_id"): self.delete_single_history(s_id)
            ).pack(side="left", padx=4)

    def delete_single_history(self, session_id):
        if messagebox.askyesno("Confirmation", "Supprimer cette session de l'historique ?"):
            LibraryManager.delete_history_session(session_id)
            self.build_history_tab()

    def confirm_clear_history(self):
        if messagebox.askyesno("Attention", "Voulez-vous vider TOUT l'historique des parties ?"):
            LibraryManager.clear_history()
            self.build_history_tab()

    def show_session_details(self, session):
        """Masque le HUB et affiche la nouvelle page complète de détails."""
        self.header_bar.pack_forget()
        self.tabview.pack_forget()

        # Instancie la nouvelle vue créée dans ui/history_detail_page.py
        self.detail_page = HistoryDetailPage(
            master=self,
            session_data=session,
            on_back_callback=self.close_session_details
        )
        self.detail_page.pack(fill="both", expand=True)

    def close_session_details(self):
        """Détruit la page de détails et réaffiche le HUB principal."""
        if hasattr(self, "detail_page") and self.detail_page:
            self.detail_page.destroy()

        self.header_bar.pack(fill="x", padx=20, pady=(20, 10))
        self.tabview.pack(padx=20, pady=(0, 20), fill="both", expand=True)