import asyncio
import edge_tts
import pygame
import tempfile
import os
import threading
import time
import json
import re
from pathlib import Path
from num2words import num2words


# ==============================
# Chargement configuration voix
# ==============================

try:

    chemin = Path(__file__).parent / "config" / "speech_config.json"

    with open(

        chemin,

        "r",

        encoding="utf-8"

    ) as fichier:

        CONFIG = json.load(fichier)

    VOICE = CONFIG["voice"]

    RATE = CONFIG["rate"]

    VOLUME = CONFIG["volume"]

    CORRECTIONS = CONFIG["pronunciations"]

    print("Configuration voix chargée.")

except Exception as e:

    print("Erreur chargement speech_config.json :", e)

    VOICE = "fr-FR-VivienneMultilingualNeural"

    RATE = "+0%"

    VOLUME = "+0%"

    CORRECTIONS = {}


# ==============================
# Initialisation audio
# ==============================

pygame.mixer.init()


lecture_en_cours = False

verrou_audio = threading.Lock()


# ==============================
# Préparer le texte avant lecture
# ==============================

def preparer_texte(texte):

    # ==========================
    # Convertir les nombres
    # ==========================

    def remplacer_nombre(match):

        try:
            return num2words(
                int(match.group()),
                lang="fr"
            )

        except:

            return match.group()

    texte = re.sub(
        r"\d+",
        remplacer_nombre,
        texte
    )

    # ==========================
    # Corriger la prononciation
    # ==========================

    for mot, prononciation in CORRECTIONS.items():

        texte = re.sub(

            rf"\b{re.escape(mot)}\b",

            prononciation,

            texte,

            flags=re.IGNORECASE

        )

    return texte


# ==============================
# Création audio Edge TTS
# ==============================

async def creer_audio(texte, fichier):

    texte = preparer_texte(texte)

    communicate = edge_tts.Communicate(
        text=texte,
        voice=VOICE,
        rate=RATE,
        volume=VOLUME
    )

    await communicate.save(fichier)


# ==============================
# Lecture d'un texte unique
# ==============================

def _lecture(texte):

    global lecture_en_cours


    fichier = None


    try:

        with verrou_audio:


            lecture_en_cours = True


            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            ) as f:

                fichier = f.name



            asyncio.run(
                creer_audio(
                    texte,
                    fichier
                )
            )



            pygame.mixer.music.load(
                fichier
            )


            pygame.mixer.music.play()



            while pygame.mixer.music.get_busy():

                if not lecture_en_cours:

                    pygame.mixer.music.stop()

                    break


                time.sleep(0.05)



    except Exception as e:

        print(
            "Erreur voix :",
            e
        )


    finally:


        try:

            pygame.mixer.music.stop()

            pygame.mixer.music.unload()

        except:

            pass



        if fichier:

            try:

                os.remove(fichier)

            except:

                pass



        lecture_en_cours = False





# ==============================
# Lecture simple
# ==============================

def parler(texte, callback=None):


    stop()



    def execution():


        _lecture(
            texte
        )


        if callback:

            callback()



    threading.Thread(

        target=execution,

        daemon=True

    ).start()





# ==============================
# Lecture en plusieurs étapes
# ==============================

def parler_sequence(sequence, callback=None):


    stop()


    def execution():


        try:


            for texte, pause in sequence:


                _lecture(texte)


                time.sleep(pause)



            if callback:

                callback()



        except Exception as e:

            print(
                "Erreur séquence voix :",
                e
            )



    threading.Thread(

        target=execution,

        daemon=True

    ).start()


# ==============================
# Arrêter lecture
# ==============================

def stop():


    global lecture_en_cours


    lecture_en_cours = False



    try:

        if pygame.mixer.music.get_busy():

            pygame.mixer.music.stop()


    except:

        pass