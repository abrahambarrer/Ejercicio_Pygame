# Libreria
import pygame
import random
import os
from spritesheet import SpriteSheet # Importar clase para las imagenes
from enemy import Enemy # Importar clase para los enemigos
# Iniciar
pygame.init()

# Dimensiones de pantalla
ancho_pantalla = 400
alto_pantalla = 600

# Ajuste de velocidad
FPS = 60
reloj = pygame.time.Clock()

# Variables de juego
GRAVEDAD = 1
MAX_PLATAFORMAS = 5
SCROLL_LIMITE = 200
scroll = 0
game_over = False
score = 0
fade_contador = 0
duracion_animacion = 75

# Revision de high score
if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

# Pantalla de juego
pantalla = pygame.display.set_mode((ancho_pantalla,alto_pantalla))
pygame.display.set_caption('Jumpy Monster')

# Colores
BLANCO = (255,255,255)
NEGRO = (0,0,0)
PANEL = (153, 217, 234)

# Definir fuentes
fuente_chica = pygame.font.SysFont('Lucida Sans', 20)
fuente_grande = pygame.font.SysFont('Lucida Sans', 24)

# Cargar imagenes
monster_plantilla = pygame.image.load('recursos/monster_sheet.png').convert_alpha()
monster = SpriteSheet(monster_plantilla)
plataforma_imagen = pygame.image.load('recursos/Rocks.png').convert_alpha()
background = pygame.image.load('recursos/sky_bg.png').convert_alpha()
enemigo_plantilla = pygame.image.load('recursos/bat_flying.png').convert_alpha()
enemigo_image = SpriteSheet(enemigo_plantilla)

# Cargar animacion
frames_animacion = 7
monster_frames = []
for frame in range(frames_animacion):
    monster_frames.append(monster.get_image(frame, 32, 32, 2, NEGRO).convert_alpha())

# Icono
pygame.display.set_icon(plataforma_imagen)

# Funcion para dar salida al texto
def dibujar_texto(texto, fuente, color_texto, x, y):
    imagen = fuente.render(texto, True, color_texto)
    pantalla.blit(imagen, (x,y))

# Funcion para dibujar el panel
def dibujar_panel():
    pygame.draw.rect(pantalla, PANEL, (0,0, ancho_pantalla,30))
    pygame.draw.line(pantalla, BLANCO, (0,30),(ancho_pantalla, 30),2)
    dibujar_texto('SCORE: ' + str(score), fuente_chica, BLANCO, 0,0)

# Funcion dibujar background
def dibujar_bg(background):
    pantalla.blit(background, (0,0))

# Clase de jugador
class Player():
    def __init__(self, x, y):
        self.image = monster_frames[0]
        self.ancho = 35
        self.alto = 55
        self.rect = pygame.Rect(0,0, self.ancho, self.alto)
        self.rect.center = (x,y)
        self.giro = False
        self.vel_y = 0
        self.tiempo_inicial = pygame.time.get_ticks()
        self.index = 0
    def move(self):
        # Variables de cambio
        scroll = 0
        dx = 0
        dy = 0

        # Presionar controles
        tecla = pygame.key.get_pressed()
        if tecla[pygame.K_a]:
            dx = -7
            self.giro = True
        elif tecla[pygame.K_d]:
            dx = 7
            self.giro = False

        # Gravedad
        self.vel_y += GRAVEDAD
        dy += self.vel_y

        # Revisar movimiento fuera de la pantalla
        if self.rect.right < 0:
            self.rect.left = ancho_pantalla
        if self.rect.left > ancho_pantalla:
            self.rect.right = 0

        # Revisar colision con plataforma
        for plataforma in grupo_plataforma:
            # Colision en la coordenada y
            if plataforma.rect.colliderect(self.rect.x, self.rect.y + dy, self.ancho, self.alto):
                # Comprobar que este sobre la plataforma
                if self.rect.bottom < plataforma.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = plataforma.rect.top
                        dy = 0
                        self.vel_y = -20
                        self.index = 0 # Reiniciar animacion

        # Comprobar si el jugador supera el limite de scroll
        if self.rect.top <= SCROLL_LIMITE:
            # Solo si esta saltando
            if self.vel_y < 0:
                scroll = -dy
        # Actualizar posicion
        self.rect.x += dx
        self.rect.y += dy + scroll

        # Actualizar mascara
        self.mascara = pygame.mask.from_surface(self.image)

        return scroll
    # Metodo dibujar
    def draw(self):
        # Animacion
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_inicial >= duracion_animacion:
            if self.index < 6:
                self.index += 1
                self.image = monster_frames[self.index]
            self.tiempo_inicial = tiempo_actual
        # Colocar imagen
        pantalla.blit(pygame.transform.flip(self.image, self.giro, False),(self.rect.x - 15, self.rect.y - 10))

# Clase de plataformas
class Plataformas(pygame.sprite.Sprite):
    def __init__(self, x, y, ancho, movimiento):
        super().__init__()
        self.image = pygame.transform.scale(plataforma_imagen, (ancho, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movimiento = movimiento
        self.contador_movimiento = random.randint(0,50)
        self.direccion = random.choice([-1,1])
        self.velocidad = random.randint(2,3)
    def update(self, scroll, score):
        # Movimiento de las plataformas
        if self.movimiento == True:
            self.contador_movimiento += 1
            self.rect.x +=  self.direccion * self.velocidad
        # Cambiar direccion
        if self.contador_movimiento >= 100 or self.rect.right > ancho_pantalla or self.rect.left < 0:
            self.direccion *= -1
            self.contador_movimiento = 0
        # Actualizar posicion vertical
        if score > 3000: # Mayor dificultad
            self.rect.y += score // 1500
        self.rect.y += scroll
        # Eliminar plataformas fuera de pantalla
        if self.rect.top > alto_pantalla:
            self.kill()

# Instancia de jugador
player = Player(ancho_pantalla // 2, alto_pantalla // 2)

# Crear grupo de sprites
grupo_plataforma = pygame.sprite.Group()
grupo_enemigos = pygame.sprite.Group()

# Plataforma inicial
plataforma = Plataformas(ancho_pantalla // 2 - 50, alto_pantalla - 50, 100, False)
grupo_plataforma.add(plataforma)

# Bucle de ejecucion
run = True
while run:
    # Manejo de FPS
    reloj.tick(FPS)
    if game_over == False:
        # Movimiento de personaje
        scroll = player.move()

        # Añadir fondo
        dibujar_bg(background)

        # Generar plataformas
        if len(grupo_plataforma) < MAX_PLATAFORMAS:
            plataforma_ancho = random.randint(60, 80)
            plataforma_x = random.randint(0, ancho_pantalla - plataforma_ancho)
            plataforma_y = plataforma.rect.y - random.randint(140, 160)
            plataforma_tipo = random.randint(1, 2)
            if plataforma_tipo == 1 and score > 500:
                plataforma_tipo = True
            else:
                plataforma_tipo = False
            plataforma = Plataformas(plataforma_x, plataforma_y, plataforma_ancho, plataforma_tipo)
            grupo_plataforma.add(plataforma)

        # Actualizar plataformas
        grupo_plataforma.update(scroll, score)

        # Generar enemigos
        if len(grupo_enemigos) == 0 and score > 2000:
            enemigo = Enemy(ancho_pantalla, 100, enemigo_image, 3)
            grupo_enemigos.add(enemigo)

        # Actualizar enemigos
        grupo_enemigos.update(scroll, ancho_pantalla)

        # Actualizar score
        if scroll > 0:
            score += scroll
        pygame.draw.line(pantalla, NEGRO, (0, score - high_score + SCROLL_LIMITE), (ancho_pantalla, score - high_score + SCROLL_LIMITE), 3)
        dibujar_texto('HIGH SCORE: ', fuente_chica, NEGRO, ancho_pantalla // 2, score - high_score + SCROLL_LIMITE)

        # Dibujar sprites
        grupo_plataforma.draw(pantalla)
        grupo_enemigos.draw(pantalla)

        # Animacion
        player.draw()

        # Dibujar panel
        dibujar_panel()

        # Revisar Game Over
        if player.rect.top > alto_pantalla:
            game_over = True
        # Revisar colision con enemigos
        if pygame.sprite.spritecollide(player, grupo_enemigos, False):
            if pygame.sprite.spritecollide(player, grupo_enemigos, False, pygame.sprite.collide_mask):
                game_over = True

    else:
        if fade_contador < ancho_pantalla:
            fade_contador += 5
            for y in range(0,6,2):
                pygame.draw.rect(pantalla, NEGRO, (0, y * 100, fade_contador, 100))
                pygame.draw.rect(pantalla, NEGRO, (ancho_pantalla - fade_contador, (y + 1) * 100, ancho_pantalla, 100))
        else:
            dibujar_texto('FIN DEL JUEGO', fuente_grande, BLANCO, 115, 200)
            dibujar_texto('PUNTUACION: ' + str(score), fuente_grande, BLANCO, 110, 250)
            dibujar_texto('PRESIONA ESPACIO', fuente_grande, BLANCO, 90, 300)

            # Actualizar high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))

            # Control
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:
                # Reiniciar variables
                fade_contador = 0
                game_over = False
                score = 0
                scroll = 0
                # Reposicionar jugador
                player.rect.center = (ancho_pantalla // 2, alto_pantalla // 2)
                # Reiniciar enemigos
                grupo_enemigos.empty()
                # Reiniciar plataformas
                grupo_plataforma.empty()
                # Plataforma inicial
                plataforma = Plataformas(ancho_pantalla // 2 - 50, alto_pantalla - 50, 100, False)
                grupo_plataforma.add(plataforma)
    # Handle_event
    for event in pygame.event.get():
        # Salida
        if event.type == pygame.QUIT:
            # Actualizar high score al cerrar ventana
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False

    # Actualizar pantalla
    pygame.display.update()
pygame.quit()