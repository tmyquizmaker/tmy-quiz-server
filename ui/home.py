"""
===========================================
TMY Quiz Maker
Version 4.5

home.py - Écran d'accueil Pro & Moderne avec Mode Multijoueur
===========================================
"""

import os
import customtkinter as ctk
from PIL import Image

import ui.colors as colors
import ui.fonts as fonts
from auth_client import session


class HomePage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        tmy_callback,
        manual_callback,
        quizzes_callback=None,
        multiplayer_callback=None,
        join_callback=None,
        settings_callback=None,
        account_callback=None
    ):
        super().__init__(master)

        self.tmy_callback = tmy_callback
        self.manual_callback = manual_callback
        self.quizzes_callback = quizzes_callback
        self.multiplayer_callback = multiplayer_callback
        self.join_callback = join_callback
        self.settings_callback = settings_callback
        self.account_callback = account_callback

        self.configure(fg_color=colors.BACKGROUND)

        # Conteneur principal avec décalage
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=20)

        # =========================================================
        # 1. BANNIÈRE / EN-TÊTE DASHBOARD
        # =========================================================
        self.header_card = ctk.CTkFrame(
            self.container, 
            fg_color="#1E222D", 
            corner_radius=15,
            border_width=1,
            border_color="#2B303C"
        )
        self.header_card.pack(fill="x", pady=(0, 20), ipady=5)

        self.header_content = ctk.CTkFrame(self.header_card, fg_color="transparent")
        self.header_content.pack(fill="x", padx=20, pady=10)

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                self.logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(60, 60))
                self.logo_label = ctk.CTkLabel(self.header_content, image=self.logo_img, text="")
                self.logo_label.pack(side="left", padx=(5, 15))
            except Exception:
                pass

        # Titre + Sous-titre
        self.title_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        self.title_frame.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="TMY QUIZ MAKER",
            font=("Arial", 22, "bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(anchor="w")

        self.subtitle = ctk.CTkLabel(
            self.title_frame,
            text="Smart Learning & Party Experience",
            font=("Arial", 12),
            text_color="#AAAAAA"
        )
        self.subtitle.pack(anchor="w")

        # Badge Joueur / XP cliquable (ouvre le compte, ou la connexion si non connecté)
        user = session.user or {}
        niveau = user.get("niveau", 1)
        xp = user.get("xp", 0)
        badge_kwargs = dict(
            font=("Arial", 12, "bold"),
            text_color="#FFD700",
            fg_color="#121620",
            hover_color="#1B2030",
            corner_radius=10,
            height=36,
            command=self.open_account,
        )
        avatar_img = session.avatar_image() if session.est_connecte() else None
        if avatar_img:
            self._avatar_ctk_img = ctk.CTkImage(light_image=avatar_img, dark_image=avatar_img, size=(24, 24))
            self.player_badge = ctk.CTkButton(
                self.header_content, text=f"  NIVEAU {niveau}  •  {xp} XP",
                image=self._avatar_ctk_img, compound="left", **badge_kwargs,
            )
        else:
            self.player_badge = ctk.CTkButton(
                self.header_content, text=f"👤 NIVEAU {niveau}  •  {xp} XP", **badge_kwargs,
            )
        self.player_badge.pack(side="right", padx=(6, 10))

        # Icône Paramètres (⚙️), séparée du badge compte
        self.settings_icon_btn = ctk.CTkButton(
            self.header_content,
            text="⚙️",
            font=("Arial", 15),
            width=36, height=36,
            fg_color="#121620",
            hover_color="#1B2030",
            corner_radius=10,
            command=self.settings
        )
        self.settings_icon_btn.pack(side="right", padx=(0, 4))

        # =========================================================
        # 2. GRILLE DE SÉLECTION DE MODE DE JEU (2x2)
        # =========================================================
        self.grid_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, pady=10)

        self.grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="group_home")
        self.grid_frame.grid_rowconfigure((0, 1), weight=1, uniform="group_home_row")

        # --- CARTE 1 : GÉNÉRER AVEC TMY (IA) - Couleur Bleue ---
        self.card_tmy = self.create_action_card(
            parent=self.grid_frame,
            icon="🧠",
            tag="INTELLIGENCE ARTIFICIELLE",
            title="GÉNÉRER AVEC TMY",
            desc="Laisse l'IA créer un quiz sur-mesure en quelques secondes sur n'importe quel sujet.",
            btn_text="LANCER L'IA",
            btn_color="#1F6AA5",
            hover_color="#144870",
            command=self.open_tmy,
            row=0, col=0
        )

        # --- CARTE 2 : MULTIJOUEUR - Couleur Violette ---
        self.card_multi = self.create_action_card(
            parent=self.grid_frame,
            icon="🌐",
            tag="MULTIJOUEUR SOCIAL",
            title="DÉFIS ENTRE AMIS",
            desc="Défie tes amis en direct ! 10 niveaux de jeu, classement en temps réel.",
            btn_text="VOIR LES NIVEAUX",
            btn_color="#8A2BE2",
            hover_color="#6A1B9A",
            command=self.open_multiplayer,
            row=0, col=1
        )

        # --- CARTE 3 : MODE CLASSE - Même Couleur Violette que Défis entre amis ---
        self.card_manual = self.create_action_card(
            parent=self.grid_frame,
            icon="🎓",
            tag="CRÉATION & SALLE EN DIRECT",
            title="MODE CLASSE",
            desc="Crée ton propre quiz avec tes questions, ou rejoins une salle déjà lancée avec un code PIN.",
            btn_text="COMMENCER",
            btn_color="#8A2BE2",
            hover_color="#6A1B9A",
            command=self.open_manual,
            row=1, col=0
        )

        # --- CARTE 4 : MES QUIZ & BIBLIOTHÈQUE - Même Couleur Bleue que Lancer l'IA ---
        self.card_quizzes = self.create_action_card(
            parent=self.grid_frame,
            icon="📚",
            tag="BIBLIOTHÈQUE",
            title="MES QUIZ",
            desc="Consulte tes quiz créés, rejoue à tes préférés ou exporte-les pour tes proches.",
            btn_text="BIBLIOTHÈQUE",
            btn_color="#1F6AA5",
            hover_color="#144870",
            command=self.my_quizzes,
            row=1, col=1
        )

        # =========================================================
        # 3. BARRE D'OUTILS (pied de page)
        # =========================================================
        self.footer_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=(15, 0))

    def create_action_card(self, parent, icon, tag, title, desc, btn_text, btn_color, hover_color, command, row, col):
        """Créateur dynamique de carte UI moderne (v2 pro : liseré, badge icône, étiquette de catégorie)"""
        card = ctk.CTkFrame(parent, fg_color="#1E222D", corner_radius=16, border_width=1, border_color="#2B303C")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Liseré supérieur coloré = identité visuelle de la carte
        accent = ctk.CTkFrame(card, fg_color=btn_color, height=3, corner_radius=0)
        accent.pack(fill="x", side="top")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(14, 15))

        # Ligne du haut : badge icône circulaire
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        icon_badge = ctk.CTkFrame(top_row, fg_color=btn_color, corner_radius=14, width=48, height=48)
        icon_badge.pack(side="left")
        icon_badge.pack_propagate(False)
        ctk.CTkLabel(icon_badge, text=icon, font=("Arial", 20)).pack(expand=True)

        # Étiquette de catégorie
        ctk.CTkLabel(content, text=tag, font=("Arial", 9, "bold"), text_color=btn_color).pack(anchor="w", pady=(10, 0))

        lbl_title = ctk.CTkLabel(content, text=title, font=("Arial", 16, "bold"), text_color="#FFFFFF")
        lbl_title.pack(anchor="w", pady=(2, 5))

        lbl_desc = ctk.CTkLabel(content, text=desc, font=("Arial", 11), text_color="#AAAAAA", justify="left", wraplength=260)
        lbl_desc.pack(anchor="w", pady=(0, 10))

        # Bouton d'action bas de carte, avec un petit effet de "flash" au clic
        btn = ctk.CTkButton(
            content,
            text=btn_text,
            font=("Arial", 12, "bold"),
            height=38,
            corner_radius=10,
            fg_color=btn_color,
            hover_color=hover_color,
            command=lambda c=command, b_color=btn_color: self._effet_clic(btn_ref[0], b_color, c)
        )
        btn_ref = [btn]
        btn.pack(fill="x", side="bottom")

        return card

    def _effet_clic(self, bouton, couleur_originale, command):
        """Petit flash blanc bref sur le bouton pour un retour visuel satisfaisant au clic,
        avant d'exécuter réellement l'action."""
        bouton.configure(fg_color="#FFFFFF")
        self.after(90, lambda: bouton.configure(fg_color=couleur_originale))
        if command:
            command()

    # =====================================
    # Callbacks & Actions
    # =====================================
    def open_tmy(self):
        if self.tmy_callback:
            self.tmy_callback()

    def open_manual(self):
        if self.manual_callback:
            self.manual_callback()

    def my_quizzes(self):
        if self.quizzes_callback:
            self.quizzes_callback()
        else:
            print("Ouverture Bibliothèque Quiz")

    def open_multiplayer(self):
        if self.multiplayer_callback:
            self.multiplayer_callback()
        else:
            print("Ouverture Mode Multijoueur")

    def join_with_code(self):
        if self.join_callback:
            self.join_callback()
        else:
            print("Saisie du code de salon multijoueur")

    def open_account(self):
        if self.account_callback:
            self.account_callback()
        else:
            print("Ouverture Compte / Connexion")

    def settings(self):
        if self.settings_callback:
            self.settings_callback()
        else:
            print("Ouverture Paramètres")