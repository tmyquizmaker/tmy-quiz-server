import json
from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_naissance = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # --- XP & progression : accumulé à chaque quiz joué (voir scores.py) ---
    xp = db.Column(db.Integer, default=0, nullable=False)

    # --- Photo de profil, stockée en base (PNG encodé en base64, ~200x200) ---
    # Choix volontaire plutôt qu'un fichier sur disque : sur Render, le disque
    # n'est pas persistant entre les redéploiements, alors que la base l'est.
    avatar_base64 = db.Column(db.Text, nullable=True)

    # --- Connexion unique : identifiant de la session active la plus récente.
    # Chaque login en génère un nouveau et écrase l'ancien, ce qui invalide
    # automatiquement le token de tout appareil précédemment connecté.
    current_session_id = db.Column(db.String(64), nullable=True)

    # --- Statistiques simples (mises à jour à chaque partie créditée en XP) ---
    total_parties = db.Column(db.Integer, default=0, nullable=False)
    meilleur_score = db.Column(db.Integer, default=0, nullable=False)

    scores = db.relationship("GameHistory", backref="user", lazy=True)

    def to_public_dict(self):
        """Représentation sûre à renvoyer au client (jamais le hash du mot de passe)."""
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "username": self.username,
            "email": self.email,
            "email_verified": self.email_verified,
            "xp": self.xp,
            "niveau": 1 + (self.xp // 1000),  # 1000 XP par niveau — ajustez ici si besoin
            "avatar_base64": self.avatar_base64,
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    questions = db.relationship("Question", backref="quiz", lazy=True,
                                 cascade="all, delete-orphan", order_by="Question.ordre")
    parties = db.relationship("GameHistory", backref="quiz", lazy=True)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    texte = db.Column(db.Text, nullable=False)
    ordre = db.Column(db.Integer, default=0, nullable=False)

    reponses = db.relationship("Answer", backref="question", lazy=True,
                                cascade="all, delete-orphan")


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    texte = db.Column(db.String(500), nullable=False)
    est_correcte = db.Column(db.Boolean, default=False, nullable=False)


class GameHistory(db.Model):
    """Historique des parties jouées. Le leaderboard est une simple requête
    (MAX(score) ou SUM(score)) sur cette table, groupée par utilisateur et/ou quiz —
    pas besoin d'une table 'Leaderboard' séparée à maintenir en double."""
    __tablename__ = "game_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    duree_secondes = db.Column(db.Integer)
    joue_le = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class VerificationCode(db.Model):
    """Code à 6 chiffres envoyé par email, pour la vérification d'inscription
    OU la réinitialisation de mot de passe — le champ 'purpose' distingue les deux
    ('verify_email' ou 'reset_password'). Valable 15 minutes par défaut."""
    __tablename__ = "verification_codes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User")


class SavedQuiz(db.Model):
    """Bibliothèque de quiz créés par l'utilisateur ('Mes Créations'), stockée
    sur le compte — plus jamais perdue au rebuild de l'app desktop, et visible
    depuis n'importe quel appareil connecté à ce compte."""
    __tablename__ = "saved_quizzes"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    teacher_name = db.Column(db.String(120))
    questions_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    owner = db.relationship("User", backref="quiz_crees")

    def to_dict(self):
        questions = json.loads(self.questions_json) if self.questions_json else []
        return {
            "id": self.id,
            "title": self.title,
            "teacher_name": self.teacher_name,
            "questions": questions,
            "total_questions": len(questions),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class GameSession(db.Model):
    """Historique des parties jouées, stocké sur le compte — même principe
    que SavedQuiz, pour l'onglet 'Historique des Parties'."""
    __tablename__ = "game_sessions"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_code = db.Column(db.String(60), nullable=False)
    quiz_title = db.Column(db.String(200))
    niveau = db.Column(db.String(50))
    mode = db.Column(db.String(30))
    played_at = db.Column(db.String(30))
    score = db.Column(db.String(20))
    percentage = db.Column(db.Integer)
    xp = db.Column(db.Integer)
    details_json = db.Column(db.Text)

    owner = db.relationship("User", backref="parties_jouees")

    def to_dict(self):
        return {
            "session_id": self.session_code,
            "quiz_title": self.quiz_title,
            "niveau": self.niveau,
            "mode": self.mode,
            "played_at": self.played_at,
            "score": self.score,
            "percentage": self.percentage,
            "xp": self.xp,
            "details": json.loads(self.details_json) if self.details_json else {},
        }
