import os
import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False

        self.current_music = None
        self.sounds = {}
        self.music_tracks = {}
        self.muted = False
        self.master_volume = 0.4
        self._single_shot_sounds = {"half_time", "low_time"}
        self._single_shot_channels = {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        if self.enabled:
            self._register_music_tracks()
            self._load_sounds()

    def _register_music_tracks(self):
        self.music_tracks = {
            "menu": os.path.join(self.assets_dir, "music", "menu.mp3"),
            "investigation_detective": os.path.join(self.assets_dir, "music", "investigation-detective.mp3"),
            "investigation_bully": os.path.join(self.assets_dir, "music", "investigation-bully.mp3"),
            "result_winner": os.path.join(self.assets_dir, "music", "result-winner.mp3"),
            "result_gameover": os.path.join(self.assets_dir, "music", "result-gameover.mp3"),
        }

    def _load_sounds(self):
        sound_files = {
            "button_click": os.path.join("sounds", "buttons", "ui-button-click-1.mp3"),
            "success": os.path.join("sounds", "hint", "notification-1.mp3"),
            "error": os.path.join("sounds", "hint", "notification-2.mp3"),
            "sabotage": os.path.join("sounds", "hint", "hacker-interference.mp3"),
            "half_time": os.path.join("sounds", "timer-alarm", "half-time.mp3"),
            "low_time": os.path.join("sounds", "timer-alarm", "low-time.mp3"),
        }

        for name, rel_path in sound_files.items():
            full_path = os.path.join(self.assets_dir, rel_path)
            if os.path.exists(full_path):
                try:
                    sound = pygame.mixer.Sound(full_path)
                    sound.set_volume(0.6)
                    self.sounds[name] = sound
                except Exception:
                    self.sounds[name] = self._load_fallback(name)
            else:
                self.sounds[name] = self._load_fallback(name)

    def _load_fallback(self, sound_name):
        if sound_name == "success":
            return self._generate_beep(880, 0.15, 0.15)
        if sound_name == "error":
            return self._generate_beep(440, 0.3, 0.12)
        if sound_name == "sabotage":
            return self._generate_beep(220, 0.4, 0.15)
        if sound_name == "button_click":
            return self._generate_beep(1000, 0.08, 0.12)
        if sound_name == "half_time":
            return self._generate_beep(660, 0.18, 0.16)
        if sound_name == "low_time":
            return self._generate_beep(320, 0.25, 0.18)
        return self._generate_beep(440, 0.2, 0.1)

    def _generate_beep(self, frequency, duration, volume=0.1):
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_amplitude = 32767 * volume

        for s in range(n_samples):
            t = float(s) / sample_rate
            val = int(round(max_amplitude * np.sin(2 * np.pi * frequency * t)))
            buf[s][0] = val
            buf[s][1] = val

        return pygame.sndarray.make_sound(buf)

    def play(self, sound_name):
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(sound_name)
        if not sound:
            return

        try:
            if sound_name in self._single_shot_sounds:
                channel = self._single_shot_channels.get(sound_name)
                if channel is not None and channel.get_busy():
                    return
                self._single_shot_channels[sound_name] = sound.play()
                return

            sound.play()
        except Exception:
            pass

    def play_music(self, track_name, loops=-1, volume=0.4):
        if not self.enabled:
            return

        track_path = self.music_tracks.get(track_name)
        if not track_path or not os.path.exists(track_path):
            return

        if track_name == self.current_music:
            if self.muted:
                return
            try:
                if pygame.mixer.music.get_busy():
                    return
            except Exception:
                pass

        self.current_music = track_name
        if self.muted:
            return

        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except Exception:
            self.current_music = None

    def toggle_mute(self):
        if not self.enabled:
            return
        self.muted = not self.muted
        try:
            if self.muted:
                pygame.mixer.music.set_volume(0)
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.set_volume(self.master_volume)
                pygame.mixer.music.unpause()
        except Exception:
            pass

    def stop_music(self, fade_ms=500):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception:
            pass
        self.current_music = None
