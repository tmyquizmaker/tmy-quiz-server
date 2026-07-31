"""
Page de connexion / inscription — page complète intégrée à la navigation
de l'app (comme HomePage, JoinRoomPage, etc.), et non une fenêtre popup.
"""
import customtkinter as ctk
from auth_client import session

# Palette reprise du reste de l'app (voir show_level1_choice dans app_controller.py)
BG_COLOR = "#121620"
CARD_COLOR = "#1B2030"
ACCENT_PURPLE = "#8A2BE2"
ACCENT_PURPLE_HOVER = "#6A1B9A"
ACCENT_TEAL = "#008080"
ACCENT_TEAL_HOVER = "#004D4D"
BTN_NEUTRAL = "#2B2D42"
BTN_NEUTRAL_HOVER = "#3A3D52"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class PasswordEntry(ctk.CTkFrame):
    """Champ mot de passe avec un bouton 'œil' pour afficher/masquer la saisie."""

    def __init__(self, master, placeholder="Mot de passe", **kwargs):
        super().__init__(master, fg_color="transparent")
        self._visible = False

        self.entry = ctk.CTkEntry(
            self, placeholder_text=placeholder, show="*", width=248, **kwargs
        )
        self.entry.pack(side="left")

        self.toggle_btn = ctk.CTkButton(
            self, text="👁", width=36, height=28, fg_color=BTN_NEUTRAL,
            hover_color=BTN_NEUTRAL_HOVER, command=self._toggle,
        )
        self.toggle_btn.pack(side="left", padx=(6, 0))

    def _toggle(self):
        self._visible = not self._visible
        self.entry.configure(show="" if self._visible else "*")
        self.toggle_btn.configure(text="🙈" if self._visible else "👁")

    def get(self):
        return self.entry.get()


class AuthPage(ctk.CTkFrame):
    """
    on_success : callback appelé une fois connecté (reprend l'action d'origine,
                 ex : ouvrir le générateur IA, le multijoueur, etc.)
    back_callback : callback pour le bouton retour (généralement show_home)
    """

    def __init__(self, master, on_success=None, back_callback=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.on_success = on_success
        self.back_callback = back_callback

        # --- En-tête ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))

        if self.back_callback:
            ctk.CTkButton(
                header, text="← Retour", width=100, fg_color=BTN_NEUTRAL,
                hover_color=BTN_NEUTRAL_HOVER, command=self.back_callback,
            ).pack(side="left")

        ctk.CTkLabel(
            self, text="Connexion requise", font=("Arial", 22, "bold"), text_color="#FFFFFF"
        ).pack(pady=(5, 2))
        ctk.CTkLabel(
            self, text="Connectez-vous ou créez un compte pour continuer",
            font=("Arial", 13), text_color="#9AA0B4",
        ).pack(pady=(0, 20))

        # --- Carte centrale ---
        card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=16, width=420)
        card.pack(pady=10)

        self.tabview = ctk.CTkTabview(
            card, width=380, height=440,
            segmented_button_selected_color=ACCENT_PURPLE,
            segmented_button_selected_hover_color=ACCENT_PURPLE_HOVER,
        )
        self.tabview.pack(padx=20, pady=20)
        self.tabview.add("Connexion")
        self.tabview.add("Créer un compte")

        self._construire_onglet_connexion(self.tabview.tab("Connexion"))
        self._construire_onglet_inscription(self.tabview.tab("Créer un compte"))

    # ---------- Onglet Connexion ----------

    def _construire_onglet_connexion(self, tab):
        ctk.CTkLabel(tab, text="Nom d'utilisateur ou email", font=("Arial", 12)).pack(pady=(20, 4), anchor="w", padx=10)
        self.login_identifiant = ctk.CTkEntry(tab, width=300, placeholder_text="ex : marcelus.money")
        self.login_identifiant.pack(pady=2, padx=10)

        ctk.CTkLabel(tab, text="Mot de passe", font=("Arial", 12)).pack(pady=(14, 4), anchor="w", padx=10)
        self.login_password = PasswordEntry(tab, placeholder="Votre mot de passe")
        self.login_password.pack(pady=2, padx=10)

        self.login_erreur = ctk.CTkLabel(tab, text="", text_color=ERROR_COLOR, wraplength=320)
        self.login_erreur.pack(pady=8)

        ctk.CTkButton(
            tab, text="SE CONNECTER", font=("Arial", 13, "bold"), width=300, height=42,
            fg_color=ACCENT_PURPLE, hover_color=ACCENT_PURPLE_HOVER, command=self._soumettre_connexion,
        ).pack(pady=6)

        ctk.CTkButton(
            tab, text="Mot de passe oublié ?", fg_color="transparent",
            text_color="#5dade2", hover=False, command=self._mot_de_passe_oublie,
        ).pack()

    def _soumettre_connexion(self):
        identifiant = self.login_identifiant.get().strip()
        password = self.login_password.get()

        if not identifiant or not password:
            self.login_erreur.configure(text="Merci de remplir tous les champs.")
            return

        succes, message = session.connecter(identifiant, password)
        if not succes:
            self.login_erreur.configure(text=message)
            return

        if self.on_success:
            self.on_success()
        elif self.back_callback:
            self.back_callback()

    def _mot_de_passe_oublie(self):
        self.login_erreur.configure(
            text="Un email de réinitialisation vous sera envoyé si le compte existe.",
            text_color="#5dade2",
        )

    # ---------- Onglet Inscription ----------

    def _construire_onglet_inscription(self, tab):
        self.reg_champs = {}
        champs_simples = [
            ("nom", "Nom"),
            ("prenom", "Prénom"),
            ("username", "Nom d'utilisateur"),
            ("date_naissance", "Date de naissance (AAAA-MM-JJ)"),
            ("email", "Email"),
        ]

        scroll = ctk.CTkScrollableFrame(tab, width=330, height=320, fg_color="transparent")
        scroll.pack(pady=(15, 5), padx=5, fill="both", expand=True)

        for cle, label in champs_simples:
            ctk.CTkLabel(scroll, text=label, font=("Arial", 12)).pack(pady=(8, 2), anchor="w")
            entree = ctk.CTkEntry(scroll, width=300)
            entree.pack(pady=2)
            self.reg_champs[cle] = entree

        ctk.CTkLabel(scroll, text="Mot de passe (8 caractères min.)", font=("Arial", 12)).pack(pady=(8, 2), anchor="w")
        self.reg_password = PasswordEntry(scroll, placeholder="Choisissez un mot de passe")
        self.reg_password.pack(pady=2)

        ctk.CTkLabel(scroll, text="Confirmer le mot de passe", font=("Arial", 12)).pack(pady=(8, 2), anchor="w")
        self.reg_password_confirm = PasswordEntry(scroll, placeholder="Retapez le mot de passe")
        self.reg_password_confirm.pack(pady=2)

        self.reg_erreur = ctk.CTkLabel(tab, text="", text_color=ERROR_COLOR, wraplength=320)
        self.reg_erreur.pack(pady=6)

        ctk.CTkButton(
            tab, text="CRÉER MON COMPTE", font=("Arial", 13, "bold"), width=300, height=42,
            fg_color=ACCENT_TEAL, hover_color=ACCENT_TEAL_HOVER, command=self._soumettre_inscription,
        ).pack(pady=(0, 10))

    def _soumettre_inscription(self):
        valeurs = {cle: entree.get().strip() for cle, entree in self.reg_champs.items()}
        password = self.reg_password.get()
        password_confirm = self.reg_password_confirm.get()

        if not all(valeurs.values()) or not password or not password_confirm:
            self.reg_erreur.configure(text="Merci de remplir tous les champs.", text_color=ERROR_COLOR)
            return

        if len(password) < 8:
            self.reg_erreur.configure(text="Le mot de passe doit contenir au moins 8 caractères.", text_color=ERROR_COLOR)
            return

        if password != password_confirm:
            self.reg_erreur.configure(text="Les deux mots de passe ne correspondent pas.", text_color=ERROR_COLOR)
            return

        succes, message = session.inscrire(
            nom=valeurs["nom"], prenom=valeurs["prenom"], username=valeurs["username"],
            date_naissance=valeurs["date_naissance"], email=valeurs["email"], password=password,
        )

        if not succes:
            self.reg_erreur.configure(text=message, text_color=ERROR_COLOR)
            return

        self.reg_erreur.configure(
            text="Compte créé ! Vérifiez votre boîte mail avant de vous connecter.",
            text_color=SUCCESS_COLOR,
        )
