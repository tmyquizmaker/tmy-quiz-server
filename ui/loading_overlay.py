"""
Superposition plein écran Ultra-Pro avec logo tournant, carte moderne
et barre de progression animée pour les opérations réseau (connexion, inscription...).
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
        self._progress_val = 0.0
        self._animating_bar = False

        if os.path.exists(LOGO_PATH):
            try:
                self._logo_original = Image.open(LOGO_PATH).convert("RGBA")
            except Exception:
                self._logo_original = None

        # ===============================================
        # CARTE CENTRALE DESIGN
        # ===============================================
        self.card = ctk.CTkFrame(
            self,
            fg_color="#1E222D",
            corner_radius=24,
            border_width=1,
            border_color="#2B303C"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.45, relheight=0.42)

        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        # 1. Logo animé ou icône fallback
        self.logo_label = ctk.CTkLabel(
            content, text="" if self._logo_original else "🧠", font=("Arial", 50)
        )
        self.logo_label.pack(pady=(10, 15))

        # 2. Message dynamique
        self.message_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Arial", 15, "bold"),
            text_color="#FFFFFF"
        )
        self.message_label.pack(pady=(0, 20))

        # 3. Barre de progression moderne
        self.progress_bar = ctk.CTkProgressBar(
            content,
            width=280,
            height=8,
            corner_radius=4,
            progress_color="#1F6AA5",
            fg_color="#121620"
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(pady=(0, 10))

        # 4. Petit footer discret
        self.footer = ctk.CTkLabel(
            content,
            text="TMY Engine • Sécurisé",
            font=("Arial", 9),
            text_color="#555861"
        )
        self.footer.pack(pady=(5, 0))

    def afficher(self, message=None):
        if message:
            self.message_label.configure(text=message)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        
        # Lancer les animations (Logo + Barre de progression fluide)
        if self._logo_original:
            self._animer_logo()
        
        self._animating_bar = True
        self._animer_barre()

    def masquer(self):
        self._animating_bar = False
        if self._apres_id:
            try:
                self.after_cancel(self._apres_id)
            except Exception:
                pass
            self._apres_id = None
        self.progress_bar.set(0.0)
        self.place_forget()

    def _animer_logo(self):
        if not self.winfo_ismapped():
            return
        self._angle = (self._angle - 6) % 360
        image_tournee = self._logo_original.rotate(self._angle, expand=False)
        ctk_img = ctk.CTkImage(light_image=image_tournee, dark_image=image_tournee, size=(64, 64))
        self.logo_label.configure(image=ctk_img, text="")
        self.logo_label.image = ctk_img  # Évite le garbage-collection

    def _animer_barre(self):
        if not self._animating_bar or not self.winfo_ismapped():
            return
        
        # Fait avancer la barre en boucle de manière fluide et dynamique
        self._progress_val += 0.03
        if self._progress_val > 1.0:
            self._progress_val = 0.0
            
        self.progress_bar.set(self._progress_val)
        self._apres_id = self.after(50, self._animer_barre)