import sys
import os
import threading
import time
import pygame

pygame.mixer.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

MUSIC = resource_path("assets/music/menu.mp3")


def start_music():
    try:
        pygame.mixer.music.load(MUSIC)
        pygame.mixer.music.set_volume(0.03)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Erreur musique :", e)


def stop_music():
    try:
        pygame.mixer.music.stop()
    except:
        pass


def resume_music():
    def _play():
        try:
            time.sleep(0.9)
            pygame.mixer.quit()
            pygame.mixer.init()

            pygame.mixer.music.load(MUSIC)
            pygame.mixer.music.set_volume(0.03)
            pygame.mixer.music.play(-1)
            print("🎵 Musique de résultat lancée avec succès !")
        except Exception as e:
            print("Erreur relance musique :", e)

    threading.Thread(target=_play, daemon=True).start()