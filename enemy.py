''' Modulo para generar enemigos en el juego '''

import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, ancho_pantalla, y, sprite, escala):
        super().__init__()
        # Variables
        self.enemigo_frames = []
        self.index = 0
        self.tiempo_inicial = pygame.time.get_ticks()
        self.direccion = random.choice([-1, 1])
        if self.direccion == 1:
            self.giro = False
        else:
            self.giro = True

        # Cargar imagenes
        frames_animacion = 4
        for frame in range(frames_animacion):
            image = sprite.get_image(frame, 32, 32, escala, (0,0,0))
            image = pygame.transform.flip(image, self.giro, False)
            image.set_colorkey((0,0,0))
            self.enemigo_frames.append(image)

        self.image = self.enemigo_frames[self.index]
        self.rect = self.image.get_rect()

        if self.direccion == 1:
            self.rect.right = 0
        else:
            self.rect.left = ancho_pantalla
        self.rect.y = y
    def update(self, scroll, ancho_pantalla):
        # Actualizar animacion
        duracion_animacion = 50
        # Actualizar imagen segun indice
        self.image = self.enemigo_frames[self.index]
        # Actualizar indice segun tiempo
        if pygame.time.get_ticks() - self.tiempo_inicial >= duracion_animacion:
            self.tiempo_inicial = pygame.time.get_ticks()
            self.index += 1
        # Reiniciar
        if self.index >= len(self.enemigo_frames):
            self.index = 0
        # Mover enemigo
        self.rect.x += self.direccion * 2
        self.rect.y += scroll
        # Revisar si supera la pantalla
        if self.rect.right < 0 or self.rect.left > ancho_pantalla:
            self.kill()