''' Modulo para extraer las imagenes de un plantilla '''

import pygame

class SpriteSheet():
    def __init__(self, image):
        self.plantilla = image

    def get_image(self, frame, ancho, alto, escala, color):
        image = pygame.Surface((ancho,alto)).convert_alpha() # Generar cuadro
        image.blit(self.plantilla, (0,0), ((frame * ancho), 0, ancho, alto)) # Colocar recorte en el cuadro
        image = pygame.transform.scale(image, (ancho * escala, alto * escala)) # Escalar
        image.set_colorkey(color)

        return image