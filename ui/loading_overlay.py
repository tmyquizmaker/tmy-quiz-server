"""
Superposition plein écran avec logo qui tourne + message, affichée pendant
une opération réseau (connexion, inscription, envoi de code...) pour éviter
que l'utilisateur ne pense que l'application a gelé. Réutilisable partout :
placez une instance dans n'importe quelle page CTkFrame, appelez .afficher()
avant la requête réseau (idéalement lancée dans un thread) et .masquer() une
fois la réponse reçue.
"""
import os
import customtkinter as ctk
from PIL import Image

LOGO_PATH = os.path.join("assets", "logo.png")


class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, parent, message="Veuillez patienter..."):
        super().__init__(parent, fg_color="#0B0E14")
        self._angle = 0
        self._apres_id = None
        self._logo_original = None

        if os.path.exists(LOGO_PATH):
            try:
                self._logo_original = Image.open(LOGO_PATH).convert("RGBA")
            except Exception:
                self._logo_original = None

        centre = ctk.CTkFrame(self, fg_color="transparent")
        centre.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_label = ctk.CTkLabel(
            centre, text="" if self._logo_original else "⏳", font=("Arial", 40)
        )
        self.logo_label.pack(pady=(0, 16))

        self.message_label = ctk.CTkLabel(
            centre, text=message, font=("Arial", 14, "bold"), text_color="#E5E7EB",
        )
        self.message_label.pack()

    def afficher(self, message=None):
        if message:
            self.message_label.configure(text=message)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        if self._logo_original:
            self._animer()

    def masquer(self):
        if self._apres_id:
            try:
                self.after_cancel(self._apres_id)
            except Exception:
                pass
            self._apres_id = None
        self.place_forget()

    def _animer(self):
        if not self.winfo_ismapped():
            return
        self._angle = (self._angle - 6) % 360
        image_tournee = self._logo_original.rotate(self._angle, expand=False)
        ctk_img = ctk.CTkImage(light_image=image_tournee, dark_image=image_tournee, size=(64, 64))
        self.logo_label.configure(image=ctk_img, text="")
        self.logo_label.image = ctk_img  # évite le garbage-collect
        self._apres_id = self.after(40, self._animer)
