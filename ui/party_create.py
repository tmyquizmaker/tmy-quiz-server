"""
===========================================
TMY Quiz Maker
party_create.py - Création de salle "Questions entre amis" (Niveau 1)
===========================================
"""

import customtkinter as ctk


class PartyCreatePage(ctk.CTkFrame):

    def __init__(self, master, create_callback, back_callback):
        super().__init__(master, fg_color="#121620")

        self.create_callback = create_callback  # (nom_complet, sujet, nb_joueurs) -> None
        self.back_callback = back_callback

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=30, pady=20)

        self._build_ui()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self.container, fg_color="#1E222D", corner_radius=12)
        top_bar.pack(fill="x", pady=(0, 20), ipady=5)

        ctk.CTkButton(
            top_bar, text="← Retour", width=100, fg_color="#2B2D42",
            hover_color="#3A3D52", command=self.back_callback
        ).pack(side="left", padx=15)

        ctk.CTkLabel(
            top_bar, text="🎉 QUESTIONS ENTRE AMIS — Créer une salle",
            font=("Arial", 15, "bold"), text_color="#FFFFFF"
        ).pack(side="left", padx=10)

        form_card = ctk.CTkFrame(
            self.container, fg_color="#1E222D", corner_radius=15,
            border_width=1, border_color="#2B303C"
        )
        form_card.pack(expand=True, fill="y", ipadx=40, ipady=25)

        ctk.CTkLabel(
            form_card, text="PARAMÈTRES DE LA PARTIE",
            font=("Arial", 16, "bold"), text_color="#FFFFFF"
        ).pack(pady=(20, 20))

        def champ(label, placeholder):
            ctk.CTkLabel(form_card, text=label, font=("Arial", 12, "bold"), text_color="#AAAAAA").pack(anchor="w", padx=30)
            entry = ctk.CTkEntry(
                form_card, placeholder_text=placeholder, font=("Arial", 13),
                fg_color="#121620", border_color="#2B303C", height=42, width=340
            )
            entry.pack(padx=30, pady=(4, 15))
            return entry

        self.nom_entry = champ("Ton Nom :", "Ex: Dupuis")
        self.prenom_entry = champ("Ton Prénom :", "Ex: Marc")
        self.sujet_entry = champ("Sujet de TES questions :", "Ex: Histoire de France, Foot, Cinéma...")

        ctk.CTkLabel(
            form_card, text="Nombre de joueurs souhaité :",
            font=("Arial", 12, "bold"), text_color="#AAAAAA"
        ).pack(anchor="w", padx=30)
        self.nb_joueurs_opt = ctk.CTkOptionMenu(
            form_card, values=[str(n) for n in range(2, 13)],
            width=340, fg_color="#121620", button_color="#2B303C"
        )
        self.nb_joueurs_opt.set("4")
        self.nb_joueurs_opt.pack(padx=30, pady=(4, 10))

        ctk.CTkLabel(
            form_card,
            text=(
                "ℹ️ Chaque ami rejoindra avec son propre sujet — la partie contiendra\n"
                "une question par sujet unique proposé (les doublons sont fusionnés).\n"
                "La partie démarre automatiquement 30s après que ce nombre est atteint."
            ),
            font=("Arial", 10, "italic"), text_color="#8A8F9E", justify="left"
        ).pack(anchor="w", padx=30, pady=(0, 10))

        self.error_lbl = ctk.CTkLabel(form_card, text="", font=("Arial", 11, "bold"), text_color="#FF5252")
        self.error_lbl.pack(pady=5)

        ctk.CTkButton(
            form_card, text="🚀 GÉNÉRER LA SALLE", font=("Arial", 13, "bold"),
            fg_color="#8A2BE2", hover_color="#6A1B9A", height=45, width=340,
            command=self.submit
        ).pack(padx=30, pady=(10, 20))

    def submit(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        sujet = self.sujet_entry.get().strip()
        nb_joueurs = int(self.nb_joueurs_opt.get())

        if not nom or not prenom:
            self.show_error("❌ Veuillez saisir votre nom et prénom.")
            return
        if not sujet:
            self.show_error("❌ Veuillez indiquer un sujet pour vos questions.")
            return

        full_name = f"{prenom} {nom}"
        self.create_callback(full_name, sujet, nb_joueurs)

    def show_error(self, message):
        self.error_lbl.configure(text=message)
