import pygame
import os

class SoundManager:
    """Manages all sound effects and music for the game"""
    
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.muted = False
        self.volume = 0.7  # Default volume level
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sound effects"""
        sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
        
        # Create the sounds directory if it doesn't exist
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
        
        # Define sound paths
        sound_files = {
            'click': 'click.wav',
            'move': 'move.wav',
            'place_obstacle': 'place_obstacle.wav',
            'game_start': 'game_start.wav',
            'game_win': 'game_win.wav',
            'game_lose': 'game_lose.wav',
            'menu_hover': 'menu_hover.wav',
            'menu_select': 'menu_select.wav',
            'error': 'error.wav'
        }
        
        # Load each sound if it exists
        for sound_name, file_name in sound_files.items():
            file_path = os.path.join(sound_dir, file_name)
            try:
                if os.path.exists(file_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(self.volume)
                else:
                    print(f"Sound file not found: {file_path}")
            except pygame.error as e:
                print(f"Could not load sound {file_name}: {e}")
    
    def play(self, sound_name):
        """Play a sound effect if not muted"""
        if not self.muted and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.muted = not self.muted
        return self.muted
    
    def set_volume(self, volume):
        """Set volume level for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def increase_volume(self):
        """Increase volume by 10%"""
        self.set_volume(self.volume + 0.1)
        return self.volume
    
    def decrease_volume(self):
        """Decrease volume by 10%"""
        self.set_volume(self.volume - 0.1)
        return self.volume
    
    def get_volume(self):
        """Get current volume level"""
        return self.volume
    
    def is_muted(self):
        """Check if sound is muted"""
        return self.muted 