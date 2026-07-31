"""
Gère la session utilisateur côté client desktop : appels aux endpoints
/auth/register, /auth/login, /auth/refresh, /auth/me, et persistance légère du refresh_token
pour éviter de redemander le mot de passe à chaque lancement de l'app.
"""
import base64
import io
import json
import os
import requests
from PIL import Image, ImageDraw, ImageOps

# URL par défaut pour vos tests locaux.
# Peut aussi être surchargée via la variable d'environnement API_BASE_URL
API_BASE_URL = os.environ.get("API_BASE_URL", "https://tmy-quiz-server.onrender.com")

# Fichier local où l'on garde le refresh_token entre deux lancements de l'app.
_SESSION_FILE = os.path.join(os.path.expanduser("~"), ".tmy_quiz_maker_session.json")


class AuthSession:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.user = None
        self._charger_session_locale()

    # ---------- État ----------

    def est_connecte(self):
        return self.access_token is not None and self.user is not None

    def _headers_auth(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    # ---------- Persistance locale ----------

    def _charger_session_locale(self):
        if not os.path.exists(_SESSION_FILE):
            return
        try:
            with open(_SESSION_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self.refresh_token = data.get("refresh_token")
            if self.refresh_token:
                self._rafraichir_token()
        except Exception:
            pass  # session locale corrompue ou absente : on repart à zéro

    def _sauvegarder_session_locale(self):
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"refresh_token": self.refresh_token}, f)

    def _effacer_session_locale(self):
        if os.path.exists(_SESSION_FILE):
            try:
                os.remove(_SESSION_FILE)
            except OSError:
                pass

    # ---------- Actions ----------

    def inscrire(self, nom, prenom, username, date_naissance, email, password):
        """date_naissance au format 'AAAA-MM-JJ'. Retourne (succes: bool, message: str)."""
        try:
            r = requests.post(f"{API_BASE_URL}/auth/register", json={
                "nom": nom, "prenom": prenom, "username": username,
                "date_naissance": date_naissance, "email": email, "password": password,
            }, timeout=10)
            data = r.json()
        except requests.RequestException:
            return False, "Impossible de contacter le serveur. Vérifiez votre connexion."
        except json.JSONDecodeError:
            return False, f"Réponse invalide du serveur ({r.status_code})."

        if r.status_code == 201:
            return True, data.get("message", "Compte créé.")
        return False, data.get("error", "Erreur lors de l'inscription.")

    def connecter(self, identifiant, password):
        """identifiant = username OU email. Retourne (succes: bool, message: str)."""
        try:
            r = requests.post(f"{API_BASE_URL}/auth/login", json={
                "identifiant": identifiant, "password": password,
            }, timeout=10)
            data = r.json()
        except requests.RequestException:
            return False, "Impossible de contacter le serveur. Vérifiez votre connexion."
        except json.JSONDecodeError:
            return False, f"Réponse invalide du serveur ({r.status_code})."

        if r.status_code != 200:
            return False, data.get("error", "Identifiant ou mot de passe incorrect.")

        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        self.user = data.get("user")
        self._sauvegarder_session_locale()
        return True, "Connexion réussie."

    def _rafraichir_token(self):
        """Utilise le refresh_token stocké pour obtenir un nouvel access_token,
        sans redemander le mot de passe. Appelé automatiquement au démarrage."""
        if not self.refresh_token:
            return False
        try:
            r = requests.post(
                f"{API_BASE_URL}/auth/refresh",
                headers={"Authorization": f"Bearer {self.refresh_token}"},
                timeout=10,
            )
            if r.status_code != 200:
                self.deconnecter()
                return False

            data = r.json()
            self.access_token = data.get("access_token")
            return self._charger_profil()
        except Exception:
            return False

    def _charger_profil(self):
        try:
            r = requests.get(f"{API_BASE_URL}/auth/me", headers=self._headers_auth(), timeout=10)
            if r.status_code != 200:
                return False
            self.user = r.json()
            return True
        except Exception:
            return False

    def recuperer_stats(self):
        """Retourne (succes: bool, stats_ou_message). stats = {'total_parties':.., 'meilleur_score':..}"""
        if not self.est_connecte():
            return False, "Non connecté."
        try:
            r = requests.get(f"{API_BASE_URL}/me/stats", headers=self._headers_auth(), timeout=10)
            if r.status_code != 200:
                return False, "Impossible de récupérer les statistiques."
            return True, r.json()
        except Exception:
            return False, "Impossible de contacter le serveur."

    # ---------- Photo de profil (stockée sur le compte, côté serveur) ----------

    def avatar_image(self):
        """Retourne la photo de profil (PIL.Image) décodée depuis le compte, ou None."""
        if not self.user or not self.user.get("avatar_base64"):
            return None
        try:
            donnees = base64.b64decode(self.user["avatar_base64"])
            return Image.open(io.BytesIO(donnees))
        except Exception:
            return None

    def changer_avatar(self, chemin_source):
        """Recadre l'image choisie en cercle et l'envoie au serveur : elle est alors
        liée au compte et visible sur tous les appareils / par les autres joueurs."""
        if not self.est_connecte():
            return False, "Vous devez être connecté."

        try:
            image = Image.open(chemin_source).convert("RGBA")
            taille = min(image.size)
            image = ImageOps.fit(image, (taille, taille), centering=(0.5, 0.5))
            image = image.resize((200, 200))

            masque = Image.new("L", (200, 200), 0)
            ImageDraw.Draw(masque).ellipse((0, 0, 200, 200), fill=255)
            resultat = Image.new("RGBA", (200, 200))
            resultat.paste(image, (0, 0), mask=masque)

            buffer = io.BytesIO()
            resultat.save(buffer, format="PNG")
            avatar_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as exc:
            return False, f"Impossible d'utiliser cette image : {exc}"

        try:
            r = requests.post(
                f"{API_BASE_URL}/auth/avatar",
                json={"avatar_base64": avatar_b64},
                headers=self._headers_auth(),
                timeout=15,
            )
            data = r.json()
        except requests.RequestException:
            return False, "Impossible de contacter le serveur."
        except json.JSONDecodeError:
            return False, f"Réponse invalide du serveur ({r.status_code})."

        if r.status_code != 200:
            return False, data.get("error", "Erreur lors de l'envoi de la photo.")

        self.user = data.get("user", self.user)
        return True, data.get("message", "Photo de profil mise à jour.")

    # ---------- Scores & XP ----------

    def enregistrer_score(self, quiz_id, score, duree_secondes=None):
        """Envoie le score d'une partie ; le serveur crédite l'XP correspondante
        et renvoie le profil à jour (utilisé pour rafraîchir le badge NIVEAU/XP)."""
        if not self.est_connecte():
            return False, "Vous devez être connecté."

        try:
            r = requests.post(
                f"{API_BASE_URL}/quiz/{quiz_id}/score",
                json={"score": score, "duree_secondes": duree_secondes},
                headers=self._headers_auth(),
                timeout=10,
            )
            data = r.json()
        except requests.RequestException:
            return False, "Impossible de contacter le serveur."
        except json.JSONDecodeError:
            return False, f"Réponse invalide du serveur ({r.status_code})."

        if r.status_code != 201:
            return False, data.get("error", "Erreur lors de l'enregistrement du score.")

        if "user" in data:
            self.user = data["user"]
        return True, data.get("message", "Score enregistré.")

    def deconnecter(self):
        self.access_token = None
        self.refresh_token = None
        self.user = None
        self._effacer_session_locale()


# Instance unique partagée par toute l'application
session = AuthSession()
