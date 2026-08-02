"""
Page complète (pas un popup) pour réinitialiser son mot de passe :
étape 1 = saisie de l'email, étape 2 = code reçu par email + nouveau mot de passe.
"""
import threading
import customtkinter as ctk
from auth_client import session
from ui.auth_page import PasswordEntry
from ui.loading_overlay import LoadingOverlay

BG_COLOR = "#121620"
CARD_COLOR = "#1B2030"
BTN_NEUTRAL = "#2B2D42"
BTN_NEUTRAL_HOVER = "#3A3D52"
ACCENT_PURPLE = "#8A2BE2"
ACCENT_PURPLE_HOVER = "#6A1B9A"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, master, back_callback, on_success=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.back_callback = back_callback
        self.on_success = on_success
        self.email_envoye = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkButton(
            header, text="← Retour", width=100, fg_color=BTN_NEUTRAL,
            hover_color=BTN_NEUTRAL_HOVER, command=self.back_callback,
        ).pack(side="left")

        ctk.CTkLabel(self, text="Mot de passe oublié", font=("Arial", 22, "bold"), text_color="#FFFFFF").pack(pady=(10, 4))
        self.sous_titre = ctk.CTkLabel(
            self, text="Entrez votre email pour recevoir un code de vérification",
            font=("Arial", 13), text_color="#9AA0B4",
        )
        self.sous_titre.pack(pady=(0, 20))

        self.card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=16, width=420)
        self.card.pack(pady=10, padx=60)

        # Superposition de chargement (logo qui tourne) pendant les appels réseau
        self.overlay = LoadingOverlay(self, message="Veuillez patienter...")

        self._afficher_etape_email()

    # ---------- Étape 1 : demande du code ----------

    def _afficher_etape_email(self):
        for w in self.card.winfo_children():
            w.destroy()
        self.sous_titre.configure(text="Entrez votre email pour recevoir un code de vérification")

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(padx=35, pady=30)

        ctk.CTkLabel(inner, text="Email", font=("Arial", 12)).pack(anchor="w", pady=(0, 4))
        self.email_entry = ctk.CTkEntry(inner, width=320, placeholder_text="votre@email.com")
        self.email_entry.pack(pady=(0, 15))

        self.erreur_lbl = ctk.CTkLabel(inner, text="", text_color=ERROR_COLOR, wraplength=320)
        self.erreur_lbl.pack(pady=5)

        self.envoyer_btn = ctk.CTkButton(
            inner, text="Envoyer le code", font=("Arial", 13, "bold"), width=320, height=42,
            fg_color=ACCENT_PURPLE, hover_color=ACCENT_PURPLE_HOVER, command=self._envoyer_code,
        )
        self.envoyer_btn.pack()

    def _envoyer_code(self):
        email = self.email_entry.get().strip()
        if not email:
            self.erreur_lbl.configure(text="Merci d'entrer votre email.")
            return

        self.envoyer_btn.configure(state="disabled")
        self.erreur_lbl.configure(text="")
        self.overlay.afficher("Envoi du code...")

        def tache():
            succes, message = session.demander_code_reinitialisation(email)
            self.after(0, lambda: self._apres_envoi(succes, message, email))

        threading.Thread(target=tache, daemon=True).start()

    def _apres_envoi(self, succes, message, email):
        if not self.winfo_exists():
            return
        self.overlay.masquer()
        if succes:
            self.email_envoye = email
            self._afficher_etape_code()
        else:
            self.envoyer_btn.configure(state="normal")
            self.erreur_lbl.configure(text=message)

    # ---------- Étape 2 : code + nouveau mot de passe ----------

    def _afficher_etape_code(self):
        self.sous_titre.configure(text=f"Un code a été envoyé à {self.email_envoye}")

        for w in self.card.winfo_children():
            w.destroy()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(padx=35, pady=30)

        ctk.CTkLabel(inner, text="Code reçu par email", font=("Arial", 12)).pack(anchor="w", pady=(0, 4))
        self.code_entry = ctk.CTkEntry(inner, width=320, placeholder_text="123456")
        self.code_entry.pack(pady=(0, 15))

        ctk.CTkLabel(inner, text="Nouveau mot de passe", font=("Arial", 12)).pack(anchor="w", pady=(0, 4))
        self.pwd_entry = PasswordEntry(inner, placeholder="8 caractères min.")
        self.pwd_entry.pack(pady=(0, 15))

        ctk.CTkLabel(inner, text="Confirmer le mot de passe", font=("Arial", 12)).pack(anchor="w", pady=(0, 4))
        self.pwd_confirm_entry = PasswordEntry(inner, placeholder="Retapez le mot de passe")
        self.pwd_confirm_entry.pack(pady=(0, 15))

        self.erreur_lbl = ctk.CTkLabel(inner, text="", text_color=ERROR_COLOR, wraplength=320)
        self.erreur_lbl.pack(pady=5)

        self.valider_btn = ctk.CTkButton(
            inner, text="Réinitialiser le mot de passe", font=("Arial", 13, "bold"), width=320, height=42,
            fg_color=ACCENT_PURPLE, hover_color=ACCENT_PURPLE_HOVER, command=self._valider_reinitialisation,
        )
        self.valider_btn.pack(pady=(0, 10))

        ctk.CTkButton(
            inner, text="Renvoyer un code", fg_color="transparent", text_color="#5dade2",
            hover=False, command=self._afficher_etape_email,
        ).pack()

    def _valider_reinitialisation(self):
        code = self.code_entry.get().strip()
        pwd = self.pwd_entry.get()
        pwd_confirm = self.pwd_confirm_entry.get()

        if not code or not pwd or not pwd_confirm:
            self.erreur_lbl.configure(text="Merci de remplir tous les champs.", text_color=ERROR_COLOR)
            return
        if len(pwd) < 8:
            self.erreur_lbl.configure(text="Le mot de passe doit contenir au moins 8 caractères.", text_color=ERROR_COLOR)
            return
        if pwd != pwd_confirm:
            self.erreur_lbl.configure(text="Les deux mots de passe ne correspondent pas.", text_color=ERROR_COLOR)
            return

        self.valider_btn.configure(state="disabled")
        self.erreur_lbl.configure(text="")
        self.overlay.afficher("Vérification du code...")

        def tache():
            succes, message = session.reinitialiser_mot_de_passe(self.email_envoye, code, pwd)
            self.after(0, lambda: self._apres_reinitialisation(succes, message))

        threading.Thread(target=tache, daemon=True).start()

    def _apres_reinitialisation(self, succes, message):
        if not self.winfo_exists():
            return
        self.overlay.masquer()
        if succes:
            if self.on_success:
                self.on_success()
            else:
                self.back_callback()
        else:
            self.valider_btn.configure(state="normal")
            self.erreur_lbl.configure(text=message, text_color=ERROR_COLOR)
