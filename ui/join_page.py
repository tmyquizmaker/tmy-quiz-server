"""
===========================================
TMY Quiz Maker
Version 5.3

join_page.py - Page complète pour rejoindre une salle
===========================================
"""

import customtkinter as ctk
from auth_client import session


class JoinRoomPage(ctk.CTkFrame):

    def __init__(self, master, verify_join_callback, back_callback, demander_sujet=False):
        super().__init__(master, fg_color="#121620")

        self.verify_join_callback = verify_join_callback
        self.back_callback = back_callback
        # 👈 Activé uniquement pour le mode "Questions entre amis" : chaque joueur
        # propose son propre sujet, l'IA génère une question par sujet unique reçu.
        self.demander_sujet = demander_sujet
        self.sujet_entry = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=30, pady=20)

        self.create_interface()

    def create_interface(self):
        # En-tête avec bouton retour
        self.top_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=12)
        self.top_bar.pack(fill="x", pady=(0, 20), ipady=5)

        self.back_btn = ctk.CTkButton(
            self.top_bar, text="← Retour à l'accueil", width=120, fg_color="#2B2D42",
            hover_color="#3A3D52", command=self.back_callback
        )
        self.back_btn.pack(side="left", padx=15)

        self.title_lbl = ctk.CTkLabel(
            self.top_bar, text="🔑 REJOINDRÈ UN QUIZ EN DIRECT",
            font=("Arial", 16, "bold"), text_color="#FFFFFF"
        )
        self.title_lbl.pack(side="left", padx=10)

        # Formulaire au centre
        self.form_card = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=15, border_width=1, border_color="#2B303C")
        self.form_card.pack(expand=True, fill="y", ipadx=40, ipady=20)

        ctk.CTkLabel(
            self.form_card, text="ENTRER LES INFORMATIONS",
            font=("Arial", 18, "bold"), text_color="#FFFFFF"
        ).pack(pady=(20, 20))

        # Champ Nom
        ctk.CTkLabel(self.form_card, text="Ton Nom :", font=("Arial", 12, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=30)
        self.nom_entry = ctk.CTkEntry(self.form_card, placeholder_text="Ex: Dupuis", font=("Arial", 13), fg_color="#121620", border_color="#2B303C", height=42, width=320)
        self.nom_entry.pack(padx=30, pady=(4, 15))

        # Champ Prénom
        ctk.CTkLabel(self.form_card, text="Ton Prénom :", font=("Arial", 12, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=30)
        self.prenom_entry = ctk.CTkEntry(self.form_card, placeholder_text="Ex: Marc", font=("Arial", 13), fg_color="#121620", border_color="#2B303C", height=42, width=320)
        self.prenom_entry.pack(padx=30, pady=(4, 15))

        # Si l'utilisateur est connecté, son nom/prénom sont déjà connus :
        # on les préremplit et on verrouille les champs pour éviter toute confusion d'identité.
        if session.est_connecte():
            self.nom_entry.insert(0, session.user.get("nom", ""))
            self.nom_entry.configure(state="disabled")
            self.prenom_entry.insert(0, session.user.get("prenom", ""))
            self.prenom_entry.configure(state="disabled")

        # Champ Sujet (uniquement pour le mode "Questions entre amis")
        if self.demander_sujet:
            ctk.CTkLabel(self.form_card, text="Sujet de TES questions :", font=("Arial", 12, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=30)
            self.sujet_entry = ctk.CTkEntry(self.form_card, placeholder_text="Ex: Histoire de France, Foot, Cinéma...", font=("Arial", 13), fg_color="#121620", border_color="#2B303C", height=42, width=320)
            self.sujet_entry.pack(padx=30, pady=(4, 15))

        # Champ Code PIN
        ctk.CTkLabel(self.form_card, text="Code PIN de la salle :", font=("Arial", 12, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=30)
        self.pin_entry = ctk.CTkEntry(self.form_card, placeholder_text="Ex: 291714", font=("Arial", 16, "bold"), fg_color="#121620", border_color="#1F6AA5", height=45, width=320)
        self.pin_entry.pack(padx=30, pady=(4, 10))

        # Zone de message d'erreur
        self.error_lbl = ctk.CTkLabel(self.form_card, text="", font=("Arial", 11, "bold"), text_color="#FF5252")
        self.error_lbl.pack(pady=5)

        # Bouton Valider
        self.submit_btn = ctk.CTkButton(
            self.form_card, text="ENTRER DANS LA SALLE", font=("Arial", 13, "bold"),
            fg_color="#1F6AA5", hover_color="#144870", height=45, width=320,
            command=self.submit
        )
        self.submit_btn.pack(padx=30, pady=(10, 20))

    def submit(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        pin = self.pin_entry.get().strip().replace(" ", "")
        sujet = self.sujet_entry.get().strip() if self.sujet_entry else None

        if not nom or not prenom:
            self.show_error("❌ Veuillez saisir votre nom et prénom.")
            return

        if not pin:
            self.show_error("❌ Veuillez entrer le code PIN de la salle.")
            return

        if self.demander_sujet and not sujet:
            self.show_error("❌ Veuillez indiquer un sujet pour tes questions.")
            return

        full_name = f"{prenom} {nom}"

        # Le callback gère maintenant tout de façon asynchrone :
        # écran de chargement -> navigation OU retour ici avec une erreur.
        if self.demander_sujet:
            self.verify_join_callback(pin, full_name, sujet)
        else:
            self.verify_join_callback(pin, full_name)

    def show_error(self, message):
        self.error_lbl.configure(text=message)