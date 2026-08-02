"""
Page de saisie du code de vérification envoyé par email après l'inscription
(ou depuis l'écran de connexion si le compte n'est pas encore vérifié).
"""
import threading
import customtkinter as ctk
from auth_client import session
from ui.loading_overlay import LoadingOverlay

BG_COLOR = "#121620"
CARD_COLOR = "#1B2030"
BTN_NEUTRAL = "#2B2D42"
BTN_NEUTRAL_HOVER = "#3A3D52"
ACCENT_PURPLE = "#8A2BE2"
ACCENT_PURPLE_HOVER = "#6A1B9A"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"


class VerifyEmailPage(ctk.CTkFrame):
    """
    email : adresse à vérifier (déjà connue, ex: juste après l'inscription)
    on_success : callback appelé une fois l'email vérifié (généralement retour à la connexion)
    back_callback : callback du bouton retour
    """

    def __init__(self, master, email, on_success=None, back_callback=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.email = email
        self.on_success = on_success
        self.back_callback = back_callback

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        if self.back_callback:
            ctk.CTkButton(
                header, text="← Retour", width=100, fg_color=BTN_NEUTRAL,
                hover_color=BTN_NEUTRAL_HOVER, command=self.back_callback,
            ).pack(side="left")

        ctk.CTkLabel(self, text="Vérifiez votre email", font=("Arial", 22, "bold"), text_color="#FFFFFF").pack(pady=(10, 4))
        ctk.CTkLabel(
            self, text=f"Entrez le code à 6 chiffres envoyé à {self.email}",
            font=("Arial", 13), text_color="#9AA0B4", wraplength=380,
        ).pack(pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=16, width=380)
        card.pack(pady=10, padx=60)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=35, pady=30)

        ctk.CTkLabel(inner, text="Code reçu par email", font=("Arial", 12)).pack(anchor="w", pady=(0, 4))
        self.code_entry = ctk.CTkEntry(inner, width=300, placeholder_text="123456", justify="center", font=("Arial", 16))
        self.code_entry.pack(pady=(0, 15))

        self.erreur_lbl = ctk.CTkLabel(inner, text="", text_color=ERROR_COLOR, wraplength=300)
        self.erreur_lbl.pack(pady=5)

        self.valider_btn = ctk.CTkButton(
            inner, text="Vérifier mon compte", font=("Arial", 13, "bold"), width=300, height=42,
            fg_color=ACCENT_PURPLE, hover_color=ACCENT_PURPLE_HOVER, command=self._verifier,
        )
        self.valider_btn.pack(pady=(0, 10))

        ctk.CTkButton(
            inner, text="Renvoyer le code", fg_color="transparent", text_color="#5dade2",
            hover=False, command=self._renvoyer,
        ).pack()

        # Superposition de chargement (logo qui tourne) pendant les appels réseau
        self.overlay = LoadingOverlay(self, message="Vérification en cours...")

    def _verifier(self):
        code = self.code_entry.get().strip()
        if not code:
            self.erreur_lbl.configure(text="Merci d'entrer le code reçu par email.", text_color=ERROR_COLOR)
            return

        self.valider_btn.configure(state="disabled")
        self.erreur_lbl.configure(text="")
        self.overlay.afficher("Vérification en cours...")

        def tache():
            succes, message = session.verifier_email(self.email, code)
            self.after(0, lambda: self._apres_verification(succes, message))

        threading.Thread(target=tache, daemon=True).start()

    def _apres_verification(self, succes, message):
        if not self.winfo_exists():
            return
        self.overlay.masquer()
        self.valider_btn.configure(state="normal")

        if succes:
            if self.on_success:
                self.on_success()
            elif self.back_callback:
                self.back_callback()
        else:
            self.erreur_lbl.configure(text=message, text_color=ERROR_COLOR)

    def _renvoyer(self):
        self.overlay.afficher("Envoi du nouveau code...")
        self.erreur_lbl.configure(text="")

        def tache():
            succes, message = session.renvoyer_code_verification(self.email)
            self.after(0, lambda: self._apres_renvoi(succes, message))

        threading.Thread(target=tache, daemon=True).start()

    def _apres_renvoi(self, succes, message):
        if not self.winfo_exists():
            return
        self.overlay.masquer()
        self.erreur_lbl.configure(
            text=message, text_color=SUCCESS_COLOR if succes else ERROR_COLOR,
        )
