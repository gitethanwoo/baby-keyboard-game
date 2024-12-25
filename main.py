import pygame
import random
import numpy as np
import sys
from pygame import mixer
from math import sin

# Initialize Pygame
pygame.init()
mixer.init(44100, -16, 2, 2048)

# Set up the display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

# Colors - Bright, baby-friendly colors
COLORS = [
    (255, 105, 180),  # Hot Pink
    (0, 191, 255),    # Deep Sky Blue
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Lime Green
    (178, 102, 255),  # Medium Purple
    (255, 165, 0),    # Orange
]

# Sound generation
def generate_tone(frequency, duration=0.5, volume=0.3, tone_type='normal'):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    if tone_type == 'bell':
        # Bell-like sound with more harmonics
        tone = np.sin(2 * np.pi * frequency * t)
        tone += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        tone += 0.2 * np.sin(2 * np.pi * frequency * 3 * t)
        tone += 0.1 * np.sin(2 * np.pi * frequency * 5 * t)
        envelope = np.exp(-4 * t)
    
    elif tone_type == 'soft':
        # Soft, gentle sound
        tone = np.sin(2 * np.pi * frequency * t)
        tone += 0.1 * np.sin(2 * np.pi * frequency * 2 * t)
        envelope = np.exp(-2 * t)
    
    elif tone_type == 'bouncy':
        # Playful, bouncy sound
        tone = np.sin(2 * np.pi * frequency * t)
        tone += 0.2 * np.sin(2 * np.pi * frequency * 1.5 * t)
        envelope = np.exp(-1 * t) * (1 + np.sin(2 * np.pi * 8 * t))
    
    else:  # normal
        # Standard pleasant tone
        tone = np.sin(2 * np.pi * frequency * t)
        tone += 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        tone += 0.2 * np.sin(2 * np.pi * frequency * 3 * t)
        envelope = np.exp(-3 * t)
    
    # Apply envelope
    tone = tone * envelope
    
    # Normalize and convert to 16-bit integer
    tone = np.int16(tone * volume * 32767)
    return pygame.sndarray.make_sound(np.column_stack((tone, tone)))

# Generate a wider range of musical notes (C major scale across two octaves)
frequencies = [
    262,  # C4
    294,  # D4
    330,  # E4
    349,  # F4
    392,  # G4
    440,  # A4
    494,  # B4
    523,  # C5
    587,  # D5
    659,  # E5
    698,  # F5
    784,  # G5
]

# Create different types of sounds for variety
sounds = []
for f in frequencies:
    sounds.extend([
        generate_tone(f, duration=0.4, volume=0.2, tone_type='bell'),
        generate_tone(f, duration=0.5, volume=0.2, tone_type='soft'),
        generate_tone(f, duration=0.3, volume=0.2, tone_type='bouncy'),
        generate_tone(f, duration=0.4, volume=0.2, tone_type='normal')
    ])

# Background music generation
def generate_background_music():
    duration = 4.0
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    music = np.zeros_like(t)
    
    # Create a more interesting ambient sound
    frequencies = [65.4, 98.1, 130.8, 164.8]  # C2, G2, C3, E3
    for i, freq in enumerate(frequencies):
        music += 0.1 * np.sin(2 * np.pi * freq * t) * np.exp(-0.5 * t)
        # Add gentle pulse to background
        music += 0.05 * np.sin(2 * np.pi * freq * t) * (1 + np.sin(2 * np.pi * 0.5 * t))
    
    music = np.int16(music * 0.1 * 32767)
    return pygame.sndarray.make_sound(np.column_stack((music, music)))

background_music = generate_background_music()
background_music.play(-1)  # Loop forever

class Shape:
    def __init__(self, x, y, color, shape_type, size):
        self.x = x
        self.y = y
        self.color = list(color)
        self.shape_type = shape_type
        self.size = size
        self.alpha = 255
        self.fade_speed = 0.5

    def draw(self, surface):
        alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        
        if self.shape_type == 0:  # Circle
            pygame.draw.circle(alpha_surface, color_with_alpha, (self.x, self.y), self.size)
        elif self.shape_type == 1:  # Square
            pygame.draw.rect(alpha_surface, color_with_alpha, 
                           (self.x-self.size//2, self.y-self.size//2, self.size, self.size))
        else:  # Triangle
            points = [
                (self.x, self.y - self.size//2),
                (self.x - self.size//2, self.y + self.size//2),
                (self.x + self.size//2, self.y + self.size//2)
            ]
            pygame.draw.polygon(alpha_surface, color_with_alpha, points)
        
        surface.blit(alpha_surface, (0, 0))
        
    def update(self):
        self.alpha = max(0, self.alpha - self.fade_speed)
        return self.alpha > 0

def create_random_shape():
    return Shape(
        x=random.randint(0, width),
        y=random.randint(0, height),
        color=random.choice(COLORS),
        shape_type=random.randint(0, 2),
        size=random.randint(50, 150)
    )

def main():
    clock = pygame.time.Clock()
    shapes = []
    background_color = (255, 255, 255)  # White background
    
    # Set window title
    pygame.display.set_caption("Baby's Keyboard Fun!")
    
    escape_message_timer = 0
    show_escape_message = False
    font = pygame.font.Font(None, 36)
    escape_text = font.render("Hold ESC to exit", True, (0, 0, 0))
    escape_text_rect = escape_text.get_rect(topleft=(10, 10))

    escape_held_timer = 0
    
    while True:
        screen.fill(background_color)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Emergency exit for parent
                    escape_message_timer = 180 # 3 seconds at 60 fps
                    show_escape_message = True
                    escape_held_timer = 1 # Start the timer
                
                # Play random sound
                random.choice(sounds).play()
                
                # Create new shape
                shapes.append(create_random_shape())
                
                # Limit maximum shapes for performance
                if len(shapes) > 50:
                    shapes.pop(0)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    show_escape_message = False
                    escape_message_timer = 0
                    escape_held_timer = 0
        
        if show_escape_message:
            screen.blit(escape_text, escape_text_rect)
            escape_message_timer -= 1
            if escape_message_timer <= 0:
                show_escape_message = False
        
        # Check if escape is held down
        if show_escape_message and pygame.key.get_pressed()[pygame.K_ESCAPE]:
            escape_held_timer += 1
            if escape_held_timer > 180: # 3 seconds at 60 fps
                pygame.quit()
                sys.exit()
        elif show_escape_message:
            escape_held_timer = 1 # Reset if escape is released
        
        # Update and draw shapes
        shapes = [shape for shape in shapes if shape.update()]
        for shape in shapes:
            shape.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        


if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
