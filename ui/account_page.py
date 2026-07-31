import os
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from auth_client import session

BG = "#121620"
CARD = "#1E222D"
BORDER = "#2B303C"
NEUTRAL = "#2B2D42"
NEUTRAL_HOVER = "#3A3D52"
DANGER = "#E53935"
DANGER_HOVER = "#B71C1C"


class AccountPage(ctk.CTkFrame):
    def __init__(self, master, back_callback, on_logout):
        super().__init__(master, fg_color=BG)
        self.back_callback = back_callback
        self.on_logout = on_logout

        # --- En-tête ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))
        ctk.CTkButton(
            header, text="← Retour", width=100, fg_color=NEUTRAL,
            hover_color=NEUTRAL_HOVER, command=self.back_callback,
        ).pack(side="left")

        ctk.CTkLabel(
            self, text="Mon compte", font=("Arial", 22, "bold"), text_color="#FFFFFF"
        ).pack(pady=(10, 20))

        # --- Carte centrale ---
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=16, border_width=1, border_color=BORDER)
        card.pack(pady=10, padx=60)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=50, pady=35)

        self.avatar_label = ctk.CTkLabel(inner, text="", width=120, height=120)
        self.avatar_label.pack(pady=(0, 12))
        self._charger_avatar()

        ctk.CTkButton(
            inner, text="📷  Changer ma photo", font=("Arial", 11, "bold"),
            fg_color=NEUTRAL, hover_color=NEUTRAL_HOVER, height=32, width=180,
            corner_radius=16, command=self._changer_photo,
        ).pack(pady=(0, 22))

        user = session.user or {}
        ctk.CTkLabel(
            inner, text=f"@{user.get('username', '')}", font=("Arial", 17, "bold"), text_color="#FFFFFF"
        ).pack()
        ctk.CTkLabel(
            inner, text=user.get("email", ""), font=("Arial", 12), text_color="#AAAAAA"
        ).pack(pady=(2, 4))
        ctk.CTkLabel(
            inner, text=f"🏆 Niveau {user.get('niveau', 1)}  •  {user.get('xp', 0)} XP",
            font=("Arial", 12, "bold"), text_color="#FFD700",
        ).pack(pady=(2, 4))

        self.photo_erreur = ctk.CTkLabel(inner, text="", font=("Arial", 10), text_color="#FF5252", wraplength=260)
        self.photo_erreur.pack()

        ctk.CTkFrame(inner, fg_color=BORDER, height=1, width=280).pack(pady=(20, 20))

        ctk.CTkButton(
            inner, text="Se déconnecter", font=("Arial", 13, "bold"),
            fg_color=DANGER, hover_color=DANGER_HOVER, height=42, width=280,
            corner_radius=10, command=self._demander_deconnexion,
        ).pack()

    # ---------- Avatar ----------

    def _charger_avatar(self):
        image = session.avatar_image()
        if image:
            ctk_img = ctk.CTkImage(light_image=image, dark_image=image, size=(120, 120))
            self.avatar_label.configure(image=ctk_img, text="", fg_color="transparent")
            self.avatar_label.image = ctk_img  # évite le garbage-collect de l'image
        else:
            self.avatar_label.configure(
                text="👤", font=("Arial", 55), image="", fg_color=BG, corner_radius=60,
            )

    def _changer_photo(self):
        chemin = filedialog.askopenfilename(
            title="Choisir une photo de profil",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")],
        )
        if not chemin:
            return

        succes, message = session.changer_avatar(chemin)
        if succes:
            self.photo_erreur.configure(text="")
            self._charger_avatar()
        else:
            self.photo_erreur.configure(text=message)

    # ---------- Déconnexion ----------

    def _demander_deconnexion(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmation")
        dialog.geometry("340x170")
        dialog.configure(fg_color=CARD)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Voulez-vous vraiment vous déconnecter ?",
            font=("Arial", 13, "bold"), text_color="#FFFFFF", wraplength=280,
        ).pack(pady=(28, 22), padx=20)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        def confirmer():
            dialog.destroy()
            session.deconnecter()
            if self.on_logout:
                self.on_logout()

        ctk.CTkButton(
            btn_row, text="Annuler", fg_color=NEUTRAL, hover_color=NEUTRAL_HOVER,
            width=120, command=dialog.destroy,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_row, text="Se déconnecter", fg_color=DANGER, hover_color=DANGER_HOVER,
            width=140, command=confirmer,
        ).pack(side="left", padx=8)
