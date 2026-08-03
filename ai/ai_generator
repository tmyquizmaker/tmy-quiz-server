"""
===========================================
TMY Quiz Maker
Version 4.0

ai_generator.py

Moteur IA TMY

Fonctions :
- Génération quiz Gemini
- Anti-répétition IA
- Temps intelligent
- Difficulté adaptative
- Sauvegarde historique
===========================================
"""

from google import genai
import json
import os
import time
import platform
from data.history_manager import HistoryManager


# ==========================================
# Configuration intégrée (sans config.py)
# ==========================================
API_KEY = os.environ.get("GEMINI_API_KEY")

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest"
]


# ==========================================
# Connexion Gemini
# ==========================================
client = genai.Client(
    api_key=API_KEY
)


# Fichier où sont mémorisées TOUTES les questions déjà générées (jouées ou non),
# pour empêcher les répétitions même quand on régénère sans terminer le quiz précédent.
GENERATED_CACHE_FILE = os.path.join("data", "generated_questions_cache.json")


class AIGenerator:

    def __init__(self):
        self.history_manager = HistoryManager()
        # Détection automatique de l'appareil
        self.device_profile = self.detect_device_profile()

    # ======================================
    # Cache anti-répétition (toutes questions générées, jouées ou non)
    # ======================================

    def _load_generated_cache(self):
        if not os.path.exists(GENERATED_CACHE_FILE):
            return []
        try:
            with open(GENERATED_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _add_to_generated_cache(self, questions):
        cache = self._load_generated_cache()
        nouveaux = [q.get("question", "") for q in questions if q.get("question")]
        cache.extend(nouveaux)

        # Garde uniquement les 300 dernières pour ne pas alourdir le prompt indéfiniment
        cache = cache[-300:]

        os.makedirs("data", exist_ok=True)
        try:
            with open(GENERATED_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Impossible d'enregistrer le cache anti-répétition : {e}")

    # ======================================
    # Détection automatique appareil
    # ======================================

    def detect_device_profile(self):
        system = platform.system().lower()

        if "android" in system:
            return "mobile"

        if system in [
            "windows",
            "linux",
            "darwin"
        ]:
            return "desktop"

        return "mobile"

    # ======================================
    # Contraintes d'affichage
    # ======================================

    def get_display_limits(self):
        if self.device_profile == "mobile":
            return {
                "question_min": 60,
                "question_max": 100,
                "answer_min": 5,
                "answer_max": 35,
                "question_lines": 3,
                "answer_lines": 2
            }

        return {
            "question_min": 80,
            "question_max": 150,
            "answer_min": 5,
            "answer_max": 50,
            "question_lines": 4,
            "answer_lines": 2
        }

    # ======================================
    # Génération quiz principale
    # ======================================

    def generate_quiz(
            self,
            sujet,
            nombre_questions,
            niveau,
            regeneration=False,
            sauvegarder=True
    ):

        anciennes_questions = (
            self.history_manager.get_used_questions()
        )
        # Fusion avec le cache de TOUTES les questions déjà générées (jouées ou non) :
        # sans ça, régénérer avant d'avoir terminé un quiz montrait les mêmes questions.
        anciennes_questions = list(anciennes_questions) + self._load_generated_cache()

        prompt = self.create_prompt(
            sujet,
            nombre_questions,
            niveau,
            anciennes_questions,
            regeneration
        )

        response = None
        last_error = None
        for model in MODELS:
            print(f"🔄 Essai avec {model}")
            for tentative in range(3):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    print(f"✅ {model} fonctionne")
                    break
                except Exception as e:
                    last_error = e
                    print(
                        f"❌ {model} | "
                        f"Tentative {tentative+1}/3"
                    )
                    if tentative < 2:
                        attente = 3 + tentative * 2
                        print(
                            f"⏳ Nouvelle tentative dans {attente}s..."
                        )
                        time.sleep(attente)
            if response:
                break

        if response is None:
            raise Exception(last_error)

        texte = response.text.strip()

        questions = self.clean_json(texte)
        if not isinstance(questions, list):
            raise Exception(
                "Gemini n'a pas retourné une liste de questions."
            )

        if len(questions) == 0:
            raise Exception(
                "Aucune question générée."
            )

        questions = self.prepare_questions(
            questions
        )
        # Alimente le cache anti-répétition immédiatement, même si l'utilisateur
        # ne termine pas ce quiz — sinon régénérer tout de suite après reverrait les mêmes questions.
        self._add_to_generated_cache(questions)

        if questions and sauvegarder:
            self.save_quiz(questions)

        return questions

    # ======================================
    # Génération d'UNE SEULE question
    # (mode multijoueur "Questions entre amis" : difficulté
    # adaptée en direct, une question à la fois, par sujet)
    # ======================================

    def generate_single_question(self, sujet, niveau="easy"):
        """Génère une seule question sur un sujet donné, au niveau de
        difficulté donné. Utilisé par le serveur du mode party pour
        générer les questions une par une, en ajustant la difficulté
        selon le taux de réussite de la question précédente."""

        questions = self.generate_quiz(
            sujet=sujet,
            nombre_questions=1,
            niveau=niveau,
            regeneration=False,
            sauvegarder=False,
        )

        if not questions:
            raise Exception(f"Aucune question générée pour le sujet '{sujet}'.")

        return questions[0]

    # ======================================
    # Création du prompt Gemini
    # ======================================

    def create_prompt(
            self,
            sujet,
            nombre_questions,
            niveau,
            anciennes_questions,
            regeneration
    ):
        limits = self.get_display_limits()
        anti_repeat = ""

        if anciennes_questions:
            liste = "\n".join(
                anciennes_questions[-100:]
            )

            anti_repeat = f"""
QUESTIONS DEJA UTILISEES :
{liste}

IMPORTANT :
- Ne crée aucune question identique.
- Change aussi la formulation.
- Utilise de nouveaux exemples.
"""

        regeneration_text = ""

        if regeneration:
            regeneration_text = """
Ceci est une régénération.
Le précédent quiz existe déjà.
Crée un quiz totalement différent.
"""

        prompt = f"""
Tu es TMY, une intelligence artificielle spécialisée
dans la création de quiz éducatifs professionnels.

Crée exactement {nombre_questions} questions.

Sujet :
{sujet}

Niveau :
{niveau}

{regeneration_text}

{anti_repeat}

REGLES IMPORTANTES :

1) Retourne uniquement un JSON valide.
2) Aucun texte avant ou après.
3) Chaque question possède exactement :
- une question
- quatre réponses A,B,C,D
- une seule bonne réponse
4) Ajoute une estimation du temps nécessaire.

Le temps doit dépendre :
- longueur de la question
- longueur des réponses
- difficulté

Temps conseillé :
Question courte :
10-15 secondes

Question moyenne :
15-25 secondes

Question longue :
25-40 secondes

IMPORTANT POUR L'AFFICHAGE
Le quiz sera affiché sur :
{self.device_profile}
Respecte impérativement ces limites.

Question :
- entre {limits["question_min"]} et {limits["question_max"]} caractères
- maximum {limits["question_lines"]} lignes
- une seule idée par question

Réponses :
- entre {limits["answer_min"]} et {limits["answer_max"]} caractères
- maximum {limits["answer_lines"]} lignes
- réponses courtes

Ne dépasse jamais ces limites.

FORMAT OBLIGATOIRE :
[
{{
"question":"",
"A":"",
"B":"",
"C":"",
"D":"",
"correct":"A",
"difficulty":"medium",
"time":20
}}
]

Le champ "correct" doit être uniquement :
A ou B ou C ou D.

Le champ "time" doit être un nombre entier
en secondes.

Le champ "difficulty" doit être :
easy
medium
hard
"""

        return prompt

    # ======================================
    # Nettoyage réponse Gemini
    # ======================================

    def clean_json(
            self,
            texte
    ):
        if "```json" in texte:
            texte = texte.replace(
                "```json",
                ""
            )
            texte = texte.replace(
                "```",
                ""
            )

        texte = texte.strip()

        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            raise Exception(
                "Réponse JSON invalide."
            )

    # ======================================
    # Préparation des questions
    # ======================================

    def prepare_questions(
            self,
            questions
    ):
        result = []
        for q in questions:
            question = {
                "question": q.get(
                    "question",
                    ""
                ),
                "A": q.get(
                    "A",
                    ""
                ),
                "B": q.get(
                    "B",
                    ""
                ),
                "C": q.get(
                    "C",
                    ""
                ),
                "D": q.get(
                    "D",
                    ""
                ),
                "correct": q.get(
                    "correct",
                    "A"
                ),
                "difficulty": q.get(
                    "difficulty",
                    "medium"
                ),
                "time": self.validate_time(
                    q.get(
                        "time",
                        20
                    )
                )
            }
            result.append(
                question
            )

        return result

    # ======================================
    # Validation du temps
    # ======================================

    def validate_time(
            self,
            value
    ):
        try:
            value = int(value)
        except:
            value = 20

        # limite sécurité
        if value < 10:
            value = 10

        if value > 60:
            value = 60

        return value

    # ======================================
    # Sauvegarde locale quiz
    # ======================================

    def save_quiz(
            self,
            questions
    ):
        dossier = "data"
        os.makedirs(
            dossier,
            exist_ok=True
        )
        fichier = os.path.join(
            dossier,
            "quizzes.json"
        )
        anciens = []

        if os.path.exists(
            fichier
        ):
            try:
                with open(
                    fichier,
                    "r",
                    encoding="utf-8"
                ) as f:
                    anciens = json.load(f)
            except:
                anciens = []

        anciens.append(
            questions
        )

        with open(
            fichier,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                anciens,
                f,
                indent=4,
                ensure_ascii=False
            )
