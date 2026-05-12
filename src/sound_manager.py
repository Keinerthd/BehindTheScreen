import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
        except:
            self.enabled = False
            
        self.sounds = {}
        if self.enabled:
            self.sounds["success"] = self._generate_beep(800, 0.2)
            self.sounds["error"] = self._generate_beep(300, 0.4)
            self.sounds["sabotage"] = self._generate_beep(150, 0.5)

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
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
