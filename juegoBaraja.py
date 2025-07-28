import pygame
import os
import random

pygame.init()  # Inicializa todos los módulos de Pygame

# CONFIGURACIÓN DE LA VENTANA  
WIDTH, HEIGHT = 1200, 800  # Dimensiones de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana principal
pygame.display.set_caption("Juego de Cartas")  # Título de la ventana

# DEFINICIÓN DE COLORES Y DIMENSIONES GLOBALES            

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
LIGHT_GRAY = (200, 200, 200)

CARD_WIDTH, CARD_HEIGHT = 100, 150  # Tamaño de las cartas
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 40  # Tamaño de los botones

CARD_OFFSET_H = 20  # Desplazamiento horizontal para el efecto "escalerita" de cartas
CARD_OFFSET_V = 2   # Desplazamiento vertical para el mazo

# Coordenadas de las 13 pilas en la mesa 
posiciones = [
    (WIDTH // 2 - 350, 80),    # Pila 1
    (WIDTH // 2 - 150, 80),    # Pila 2
    (WIDTH // 2 + 50, 80),     # Pila 3
    (WIDTH // 2 + 250, 80),    # Pila 4
    (WIDTH // 2 + 250, 240),   # Pila 5
    (WIDTH // 2 + 250, 400),   # Pila 6
    (WIDTH // 2 + 250, 560),   # Pila 7
    (WIDTH // 2 + 50, 560),    # Pila 8
    (WIDTH // 2 - 150, 560),   # Pila 9
    (WIDTH // 2 - 350, 560),   # Pila 10
    (WIDTH // 2 - 350, 400),   # Pila 11
    (WIDTH // 2 - 350, 240),   # Pila 12
    (WIDTH // 2 - 40, 325),    # Pila 13 (centro)
]


# CLASE Carta: Representa una carta individual             
class Carta:
    def __init__(self, imagen_frontal, imagen_reverso, nombre_archivo):
        self.imagen_frontal = imagen_frontal
        self.imagen_reverso = imagen_reverso
        self.nombre_archivo = nombre_archivo
        self.rect = imagen_frontal.get_rect()
        
    def obtener_valor(self):
        """
        Devuelve el valor numérico de la carta según su nombre de archivo.
        A=1, J=11, Q=12, K=13, números según corresponda.
        """
        # Obtener el valor del inicio del nombre del archivo
        nombre = self.nombre_archivo.lower()  # Convertir a minúsculas para manejar mejor
        
        # Manejar casos especiales primero
        if nombre.startswith('a'):
            return 1
        elif nombre.startswith('j'):
            return 11
        elif nombre.startswith('q'):
            return 12
        elif nombre.startswith('k'):
            return 13
        else:
            # Para números del 2-10, tomar los dígitos del inicio
            valor = ''
            for char in nombre:
                if char.isdigit():
                    valor += char
                else:
                    break
            return int(valor) if valor else 0

    def obtener_siguiente_posicion(self, carta):
        """
        Dado un objeto carta, devuelve el índice de la pila destino según el valor.
        """
        # Usar el nombre del archivo para determinar el valor
        valor = carta.obtener_valor()
        if valor == 13:  # K
            return 12  # índice 12 corresponde a posición 13 (centro)
        return valor - 1  # índice 0-11 corresponde a posiciones 1-12
        


# CLASE Button: Botón gráfico con texto y color            
class Button:
    def __init__(self, x, y, width, height, text, color=(0, 200, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.activo = True
        self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 28) if os.path.exists(os.path.join("recursos", "JandaEverydayCasual.ttf")) else pygame.font.Font(None, 28)
        self.text_surface = self.font.render(text, True, (0, 0, 0))

    def draw(self, surface):
        """
        Dibuja el botón en la superficie indicada.
        """
        color = self.color if self.activo else (128, 128, 128)
        pygame.draw.rect(surface, color, self.rect, border_radius=20)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=20)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)

    def is_clicked(self, pos):
        """
        Devuelve True si el punto (pos) está dentro del botón.
        """
        return self.rect.collidepoint(pos)


###########################################################
# CLASE Juego: Lógica principal del juego de cartas        #
###########################################################
class Juego:
    ESTADO_INICIO = 0
    ESTADO_INSTRUCCIONES = 1
    ESTADO_JUEGO = 2
    ESTADO_AUTO = 3

    def __init__(self):
        """
        Inicializa todos los atributos y estados del juego.
        """
        # Atributos para la animación
        self.animando_mezcla = False
        self.tiempo_animacion = 0
        self.duracion_animacion = 120  # Tiempo de animación de la MEZCLA (milisegundos por paso)
        self.cartas_mezcladas = []
        self.grupos_mezcla = []
        self.carta_actual = None
        self.pos_central = (WIDTH // 2 - 100, HEIGHT // 2 - 100)  # Más arriba y a la izquierda
        self.pos_inicial_izq = (WIDTH // 2 - 250, HEIGHT // 2 - 100)  # Más separado a la izquierda
        self.pos_inicial_der = (WIDTH // 2 + 50, HEIGHT // 2 - 100)   # Más separado a la derecha
        self.estado_animacion = 'inicio'

        # Variables para automatización del modo automático
        self._auto_fase = None
        self._auto_last_action_time = 0
        self._auto_action_interval = 1000  # milisegundos (1 segundo)

        self.tiempo_reparto = 0
        # Asegurarnos de que no haya cartas fantasma
        self.animando_reparto = False
        self.carta_actual_reparto = None
        self.cartas_por_repartir = []
        self.cartas_a_repartir = []
        self.posicion_destino = None
        self.duracion_reparto_carta = 35  # Tiempo de animación de REPARTO de cada carta (milisegundos)

        # Estado de la pantalla
        self.estado = Juego.ESTADO_INICIO
        self.modo_automatico = False

        # Botones de inicio 
        botones_y = HEIGHT//2 + 40  # Un poco más abajo del centro
        espacio_entre = 40
        ancho_auto = 240
        ancho_manual = 200
        alto = 60
        total_ancho = ancho_auto + ancho_manual + espacio_entre
        inicio_x = WIDTH//2 - total_ancho//2
        self.boton_auto = Button(inicio_x, botones_y, ancho_auto, alto, "Modo Automático", color=(0, 200, 0))
        self.boton_manual = Button(inicio_x + ancho_auto + espacio_entre, botones_y, ancho_manual, alto, "Modo Manual", color=(0, 200, 0))
        self.boton_instrucciones = Button(WIDTH//2 - 100, botones_y + alto + 40, 200, 50, "Instrucciones", color=(0, 150, 200))

        # Botones de juego
        self.boton_mezclar = Button(WIDTH-150, 100, BUTTON_WIDTH, BUTTON_HEIGHT, "Mezclar", color=(200, 200, 0))
        self.boton_repartir = Button(WIDTH-150, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Repartir", color=(0, 150, 200))
        self.boton_jugar = Button(WIDTH-150, 300, BUTTON_WIDTH, BUTTON_HEIGHT, "Jugar", color=(0, 200, 0))
        self.boton_reiniciar = Button(WIDTH-150, 400, BUTTON_WIDTH, BUTTON_HEIGHT, "Reiniciar", color=(200, 0, 0))

        # Fuente grande para títulos
        self.font_titulo = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 48) if os.path.exists(os.path.join("recursos", "JandaEverydayCasual.ttf")) else pygame.font.Font(None, 48)
        self.font_btn = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 28) if os.path.exists(os.path.join("recursos", "JandaEverydayCasual.ttf")) else pygame.font.Font(None, 28)

        # Texto de instrucciones
        self.texto_instrucciones = [
            "REGLAS DEL JUEGO DEL CARTAS:",
            "- El objetivo es colocar todas las cartas en las pilas correctas.",
            "- En modo manual, arrastra la carta a la pila correspondiente.",
            "- En modo automático, el juego se juega solo.",
            "- Ganas si logras colocar todas las cartas sin errores.",
            "- Pulsa ESC para volver al menú principal."
        ]

        # Cargar imágenes
        self.fondo = self.cargar_imagen(os.path.join("recursos", "fondo.png"), (WIDTH, HEIGHT))
        self.reverso_base = self.cargar_imagen(os.path.join("recursos", "reversoo.png"), (CARD_WIDTH, CARD_HEIGHT))
         
        # Cargar mazo
        self.mazo = self.cargar_cartas()
        self.mazo_pos = (50, HEIGHT//2 - CARD_HEIGHT//2)
        self.cartas_por_posicion = {pos: [] for pos in posiciones}
        
        # Inicializar sistema de audio con manejo de errores
        #try:
        #    pygame.mixer.init()
            # Cargar efectos de sonido y música
        #    self.sonido_click = pygame.mixer.Sound(os.path.join("recursos", "click.mp3"))
        #    
            # Configurar y reproducir música de fondo
        #    pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
        #    pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
        #    pygame.mixer.music.play(-1)  # -1 significa loop infinito
            
        #    self.audio_disponible = True
        #except:
        #    print("No se pudo inicializar el sistema de audio")
        #    self.audio_disponible = False
        

        # Crear botones con imágenes
        
        # Estado inicial de los botones
        self.boton_jugar.activo = False
        self.boton_reiniciar.activo = False
        
        # Estado del juego
        self.cartas_mesa = []

        # Ajustar los offsets para los efectos escalerita
        self.CARD_OFFSET_H = 20  # Para los bloques horizontales
        self.CARD_OFFSET_V = 0.5  # Para el mazo vertical (mucho más sutil)

        # Variables para el juego del Reloj
        self.jugando = False
        self.carta_actual_juego = None
        self.cartas_volteadas = set()
        self.pila_actual = 12  # Empezamos en la pila central
        self.total_cartas = 52
        
        # Variables para arrastrar cartas
        self.arrastrando = False
        self.carta_arrastrada = None
        self.pos_arrastre = None
        self.pos_origen = None
        self.pos_origen_index = None

        # Cargar imágenes de respuesta
        self.img_si = self.cargar_imagen(os.path.join("recursos", "respSI.png"), (480, 300))
        self.img_no = self.cargar_imagen(os.path.join("recursos", "respNO.png"), (480, 300))
        
        # Variables para el cuadro de texto
        self.pregunta = ""
        self.mostrando_input = False
        self.font = pygame.font.Font(None, 32)
        self.input_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 20, 400, 40)
        self.color_input_activo = pygame.Color('lightskyblue3')
        self.color_input_inactivo = pygame.Color('gray15')
        self.color_input = self.color_input_inactivo
        
        # Variable para mostrar respuesta
        self.mostrando_respuesta = False
        self.respuesta_img = None
        self.tiempo_respuesta = 0

        # Cargar imagen de pregunta
        self.img_pregunta = self.cargar_imagen(os.path.join("recursos", "pregunta.png"), (600, 200))
        
        # Cargar la fuente personalizada
        try:
            self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18)
        except Exception:
            print("No se pudo cargar la fuente personalizada, usando fuente por defecto")
            self.font = pygame.font.Font(None, 20)  # Fuente por defecto si falla la carga
        

        # Variables para el cuadro de texto
        self.pregunta = ""
        self.mostrando_input = False
        self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18)
        
        # Definir el área de texto dentro de la imagen
        self.area_texto = {
            'ancho': 300,      # Ajusta según necesites
            'alto': 110,        # Ajusta según necesites
            'offset_x': 250,   # Ajusta según necesites
            'offset_y': 60     # Ajusta según necesites
        }
        self.margen_texto = 10
        self.font = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 18) 

        # Cargar imagen meditando
        self.img_mascota = self.cargar_imagen(os.path.join("recursos", "mascota.png"), (150, 150))  # Ajusta el tamaño según necesites
        self.mostrar_mascota = True  # Variable para controlar cuando se muestra la imagen

        # Inicializar sistema de audio con manejo de errores
        try:
            pygame.mixer.init()
            # Cargar efectos de sonido y música
            self.sonido_click = pygame.mixer.Sound(os.path.join("recursos", "click.mp3"))
            
            # Configurar y reproducir música de fondo
            pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
            pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
            pygame.mixer.music.play(-1)  # -1 significa loop infinito
            
            self.sonido_error = pygame.mixer.Sound(os.path.join("recursos", "error.mp3"))
            self.sonido_tomar = pygame.mixer.Sound(os.path.join("recursos", "cartaTomada.mp3"))
            self.sonido_soltar = pygame.mixer.Sound(os.path.join("recursos", "cartaSoltada.mp3"))
            self.sonido_barajar = pygame.mixer.Sound(os.path.join("recursos", "barajada.mp3"))
            self.sonido_barajar.set_volume(0.5)
            self.sonido_error.set_volume(0.5)
            
            self.audio_disponible = True
            self.barajando_sonando = False
        except Exception:
            print("No se pudo inicializar el sistema de audio")
            self.audio_disponible = False
        
        self.duracion_reparto_carta = 100  # Originalmente era más alto, ajusta este valor según necesites

    def render_texto_multilinea(self, texto, ancho_disponible):
        """
        Divide un texto largo en varias líneas para que quepa en un ancho dado.
        """
        lineas = []
        palabras = texto.split()
        linea_actual = []
        
        for palabra in palabras:
            # Añadir palabra de prueba
            linea_prueba = linea_actual + [palabra]
            # Obtener el ancho de la línea con la nueva palabra
            texto_prueba = ' '.join(linea_prueba)
            ancho_texto = self.font.render(texto_prueba, True, (0, 0, 0)).get_width()
            
            if ancho_texto <= ancho_disponible:
                # La palabra cabe en la línea actual
                linea_actual = linea_prueba
            else:
                # La palabra no cabe, guardar línea actual y empezar nueva línea
                if linea_actual:  # Si hay texto en la línea actual
                    lineas.append(' '.join(linea_actual))
                    linea_actual = [palabra]
                else:  # Si la palabra es más larga que el ancho disponible
                    # Dividir la palabra
                    lineas.append(palabra[:len(palabra)//2] + '-')
                    linea_actual = [palabra[len(palabra)//2:]]
        
        # Añadir la última línea si existe
        if linea_actual:
            lineas.append(' '.join(linea_actual))
            
        return lineas
    
    def __del__(self):
        """
        Detiene la música al destruir el objeto Juego.
        """
        try:
            if hasattr(self, 'audio_disponible') and self.audio_disponible:
                pygame.mixer.music.stop()
        except Exception:
            pass
    
    def reiniciar_juego(self):
        """
        Restaura todos los estados y variables para comenzar una nueva partida.
        """
        self.detener_todos_sonidos()

        # Reiniciar variables del juego
        self.jugando = False
        self.mazo = self.cargar_cartas()
        self.cartas_por_posicion = {pos: [] for pos in posiciones}
        self.cartas_volteadas = set()
        self.carta_arrastrada = None
        self.arrastrando = False
        self.mostrando_respuesta = False
        self.respuesta_img = None
        self.pregunta = ""
        self.mostrando_input = False
        self._auto_fase = None
        if hasattr(self, '_mezcla_realizada'):
            del self._mezcla_realizada
        if hasattr(self, '_mazo_barajado'):
            del self._mazo_barajado
        self.modo_automatico = False
        # Reiniciar estado de los botones
        self.boton_mezclar.activo = True
        self.boton_repartir.activo = True  # Ahora también activamos el botón de repartir
        self.boton_jugar.activo = False
        self.boton_reiniciar.activo = False
        # Reiniciar música
        pygame.mixer.music.load(os.path.join("recursos", "jazz.mp3"))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        self.mostrar_mascota = True  # Mostrar mascota al reiniciar
        # Asegurarse de que todos los sonidos se detengan
        if self.audio_disponible:
            if self.barajando_sonando:
                self.sonido_barajar.stop()
                self.barajando_sonando = False
            self.sonido_tomar.stop()
            self.sonido_soltar.stop()
        
    def iniciar_juego(self):
        """
        Inicia la partida (modo manual), habilitando el juego.
        """
        if not self.boton_jugar.activo:
            return
            
        self.detener_todos_sonidos()
        self.jugando = True
        self.boton_jugar.activo = False
        self.pila_actual = 12  # Empezamos en la pila central
        # No volteamos automáticamente, esperamos el click del usuario
        
    def voltear_carta_en_posicion(self, pos_index):
        """
        Voltea la carta superior de la pila indicada si es la pila actual.
        """
        if not self.jugando or pos_index != self.pila_actual:
            return  # Solo permitir voltear en la pila actual
            
        pila = self.cartas_por_posicion[posiciones[pos_index]]
        if not pila:  # Si la pila está vacía
            self.terminar_juego(False)  # Perdiste
            return
            
        carta = pila[-1]  # Tomar la carta superior
        if carta in self.cartas_volteadas:
            self.terminar_juego(False)  # Perdiste - la carta ya estaba volteada
            return
            
        # Voltear la carta
        self.carta_actual_juego = carta
        self.cartas_volteadas.add(carta)
        
        # Determinar la siguiente posición basada en el valor de la carta
        valor = (carta.valor % 13) + 1  # Convertir valor 0-51 a 1-13
        if valor == 13:  # K
            self.pila_actual = 12  # Centro
        else:
            self.pila_actual = valor - 1  # Posiciones 0-11 para valores 1-12
        
        # Verificar victoria
        if len(self.cartas_volteadas) == self.total_cartas:
            self.terminar_juego(True)
        
    def obtener_siguiente_posicion(self, carta):
        """
        Devuelve el índice de la pila destino para la carta dada.
        """
        # Usar el nombre del archivo para determinar el valor
        valor = carta.obtener_valor()
        if valor == 13:  # K
            return 12  # índice 12 corresponde a posición 13 (centro)
        return valor - 1  # índice 0-11 corresponde a posiciones 1-12

    def terminar_juego(self, victoria):
        """
        Finaliza la partida mostrando el resultado y habilita el botón de reinicio.
        """
        self.detener_todos_sonidos()
        self.jugando = False
        mensaje = "¡Ganaste!" if victoria else "Perdiste"
        print(mensaje)
        
        # Mostrar imagen de respuesta
        self.mostrando_respuesta = True
        self.respuesta_img = self.img_si if victoria else self.img_no
        
        # Ocultar imagen meditando cuando se muestra la respuesta
        self.mostrar_mascota = False
        
        # Activar botón de reiniciar
        self.boton_reiniciar.activo = True
        
        pygame.mixer.music.stop()
        
    def obtener_pila_clickeada(self, pos_mouse):
        """
        Devuelve el índice de la pila sobre la que se hizo click, o None.
        """
        # Verificar en qué pila se hizo click
        for i, pos in enumerate(posiciones):
            # Crear un rectángulo para la pila
            rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
            if rect.collidepoint(pos_mouse):
                return i
        return None
        
    def cargar_imagen(self, ruta, size=None):
        """
        Carga una imagen desde disco y la escala si se indica.
        """
        imagen = pygame.image.load(ruta).convert_alpha()
        if size:
            imagen = pygame.transform.scale(imagen, size)
        return imagen
        
    def cargar_cartas(self):
        """
        Carga todas las cartas desde la carpeta 'img' y las devuelve como objetos Carta.
        """
        mazo = []
        for carta in os.listdir("img"):
            if carta.endswith(".png"):
                ruta_carta = os.path.join("img", carta)
                imagen_frontal = self.cargar_imagen(ruta_carta, (CARD_WIDTH, CARD_HEIGHT))
                # Crear una copia del reverso para cada carta
                imagen_reverso = self.reverso_base.copy()
                mazo.append(Carta(imagen_frontal, imagen_reverso, carta))
        return mazo
        
    def mezclar_hojeo(self):
        """
        Realiza la animación y lógica de mezcla del mazo (mezcla tipo riffle).
        """
        if self.animando_mezcla or not self.boton_mezclar.activo:
            return

        # Mezcla real del mazo antes de la animación (solo una vez)
        # Solo barajar si no hay cartas_mezcladas de una mezcla previa
        if not hasattr(self, '_mazo_barajado') or not self._mazo_barajado:
            random.shuffle(self.mazo)
            self._mazo_barajado = True

        self.animando_mezcla = True
        self.cartas_mezcladas = []
        self.estado_animacion = 'inicio'
        self.tiempo_animacion = 0

        # Desactivar botón de repartir mientras se mezcla
        self.boton_repartir.activo = False
        mazo_temp = self.mazo.copy()

        # Dividir el mazo en dos mitades
        mitad = len(mazo_temp) // 2
        mazo_izquierdo = mazo_temp[:mitad]
        mazo_derecho = mazo_temp[mitad:]

        # Crear grupos de cartas para la mezcla
        self.grupos_mezcla = []
        while mazo_izquierdo or mazo_derecho:
            if mazo_izquierdo:
                cant = random.randint(1, min(3, len(mazo_izquierdo)))
                cartas = mazo_izquierdo[:cant]
                del mazo_izquierdo[:cant]
                for carta in cartas:
                    self.grupos_mezcla.append({
                        'carta': carta,
                        'lado': 'izquierda',
                        'pos_actual': self.pos_inicial_izq,
                        'progreso': 0
                    })
            if mazo_derecho:
                cant = random.randint(1, min(3, len(mazo_derecho)))
                cartas = mazo_derecho[:cant]
                del mazo_derecho[:cant]
                for carta in cartas:
                    self.grupos_mezcla.append({
                        'carta': carta,
                        'lado': 'derecha',
                        'pos_actual': self.pos_inicial_der,
                        'progreso': 0
                    })
    
    def detener_todos_sonidos(self):
        """
        Detiene todos los efectos de sonido activos.
        """
        #detiene los efectos de sonido
        if self.audio_disponible:
            self.sonido_tomar.stop()
            self.sonido_soltar.stop()
            self.sonido_barajar.stop()
            self.barajando_sonando = False

    def reproducir_sonido(self, sonido):
        """
        Detiene los sonidos actuales y reproduce el sonido indicado.
        """
        #reproduce un sonido despues de detener los otros
        if self.audio_disponible:
            self.detener_todos_sonidos()
            sonido.play()

    def actualizar_animacion(self, dt):
        """
        Actualiza el estado de la animación de mezcla de cartas.
        """
        if not self.animando_mezcla:
            return

        self.tiempo_animacion += dt

        if self.estado_animacion == 'inicio':
            # Mover el mazo al centro
            # Aquí se usa un tiempo fijo de 500ms para la animación inicial de la mezcla
            progreso = min(1, self.tiempo_animacion / 500)  # 500ms para el movimiento inicial
            if progreso >= 1:
                self.estado_animacion = 'dividiendo'
                self.tiempo_animacion = 0

        elif self.estado_animacion == 'dividiendo':
            # Aquí también se usa 500ms para la animación de dividir el mazo
            progreso = min(1, self.tiempo_animacion / 500)
            if progreso >= 1:
                self.estado_animacion = 'mezclando'
                self.tiempo_animacion = 0
                if self.audio_disponible and not self.barajando_sonando:
                    self.detener_todos_sonidos()
                    self.sonido_barajar.play(-1)
                    self.barajando_sonando = True

        elif self.estado_animacion == 'mezclando':
            # Mover cartas una por una
            # Aquí se usa 100ms por carta para la animación de mezcla (ajustable)
            if self.carta_actual is None and self.grupos_mezcla:
                self.carta_actual = self.grupos_mezcla.pop(0)
                self.carta_actual['progreso'] = 0

            if self.carta_actual:
                self.carta_actual['progreso'] += dt / 100  # 100ms por carta mezclada

                if self.carta_actual['progreso'] >= 1:
                    self.cartas_mezcladas.append(self.carta_actual['carta'])
                    self.carta_actual = None
                else:
                    # Interpolar posición
                    prog = self.carta_actual['progreso']
                    pos_inicial = self.pos_inicial_izq if self.carta_actual['lado'] == 'izquierda' else self.pos_inicial_der
                    self.carta_actual['pos_actual'] = (
                        pos_inicial[0] + (self.pos_central[0] - pos_inicial[0]) * prog,
                        pos_inicial[1] + (self.pos_central[1] - pos_inicial[1]) * prog
                    )

        # Terminar animación
        if not self.carta_actual and not self.grupos_mezcla:
            self.animando_mezcla = False
            # NO volver a barajar aquí, solo usar el orden de cartas_mezcladas
            self.mazo = self.cartas_mezcladas.copy()
            self.detener_todos_sonidos()
            self.boton_repartir.activo = True


    def repartir(self):
        """
        Realiza la animación y lógica de reparto de cartas a las pilas.
        """
        if self.animando_reparto:
            return

        self.animando_reparto = True
        self.tiempo_reparto = 0
        self.cartas_mesa = []
        self.cartas_por_posicion = {pos: [] for pos in posiciones}
        self.cartas_volteadas = set()  # Limpiar cartas volteadas antes de repartir

        # Desactivar botón de mezclar y repartir
        self.boton_mezclar.activo = False
        self.boton_repartir.activo = False

        # Usar el mazo ya barajado (NO volver a barajar ni cambiar el orden)
        self.cartas_por_repartir = self.mazo.copy()
        self.cartas_a_repartir = []

        for _ in range(4):
            for pos_index in range(13):
                if self.cartas_por_repartir:
                    carta = self.cartas_por_repartir.pop(0)
                    self.cartas_a_repartir.append({
                        'carta': carta,
                        'pos_destino': posiciones[pos_index],
                        'progreso': 0
                    })

        # Activar input de pregunta al terminar el reparto (por si el estado previo lo dejó desactivado)
        self.mostrando_input = False  # Se activará al terminar el reparto


    def actualizar_reparto(self, dt):
        """
        Actualiza la animación de reparto de cartas.
        """
        if not self.animando_reparto:
            return
            
        self.tiempo_reparto += dt
        
        if self.carta_actual_reparto is None and self.cartas_a_repartir:
            self.carta_actual_reparto = self.cartas_a_repartir.pop(0)
            self.carta_actual_reparto['progreso'] = 0
            # Remover la carta del mazo cuando comienza a moverse
            if len(self.mazo) > 0:
                self.mazo.pop()
                
        if self.carta_actual_reparto:
            # Aquí se usa self.duracion_reparto_carta para controlar la velocidad de reparto de cada carta
            self.carta_actual_reparto['progreso'] += dt / self.duracion_reparto_carta
            
            if self.carta_actual_reparto['progreso'] >= 1:
                # La carta llegó a su destino
                carta = self.carta_actual_reparto['carta']
                pos_destino = self.carta_actual_reparto['pos_destino']
                self.cartas_por_posicion[pos_destino].append(carta)
                
                # Reproducir sonido cuando la carta llega a su posición
                if self.audio_disponible:
                    self.reproducir_sonido(self.sonido_tomar)
                
                self.carta_actual_reparto = None
            
        #if not self.carta_actual_reparto and not self.cartas_a_repartir:
        #    self.animando_reparto = False
        #    self.boton_jugar.activo = True
        
        if not self.carta_actual_reparto and not self.cartas_a_repartir:
            self.animando_reparto = False
            if self.estado != Juego.ESTADO_AUTO:
                self.mostrando_input = True
                self.mostrar_mascota = False
                # Limpiar la pregunta anterior para evitar residuos
                self.pregunta = ""
    
    def obtener_ultima_carta_no_volteada(self, pila):
        """
        Devuelve la última carta no volteada de una pila, o None si todas están volteadas.
        """
        # Recorrer la pila desde arriba hacia abajo
        for carta in reversed(pila):
            if carta not in self.cartas_volteadas:
                return carta
        return None
        
    def manejar_evento(self, event):
        """
        Maneja todos los eventos de teclado y ratón del juego.
        """
        # Manejar entrada de texto primero, sin importar el estado
        if self.mostrando_input:
            KEYDOWN = getattr(pygame, 'KEYDOWN', 768)
            K_RETURN = getattr(pygame, 'K_RETURN', 13)
            K_BACKSPACE = getattr(pygame, 'K_BACKSPACE', 8)
            if event.type == KEYDOWN:
                # Solo aceptar caracteres imprimibles y teclas relevantes
                if event.key == K_RETURN and self.pregunta:
                    print(f"Pregunta realizada: {self.pregunta}")
                    self.mostrando_input = False
                    self.boton_jugar.activo = True
                    self.mostrar_mascota = True
                    # En modo automático, avanzar a la fase de mezclar tras la pregunta
                    if self.estado == Juego.ESTADO_AUTO:
                        self._auto_fase = 'mezclar'
                elif event.key == K_BACKSPACE:
                    self.pregunta = self.pregunta[:-1]
                elif hasattr(event, 'unicode') and event.unicode and event.unicode.isprintable():
                    self.pregunta += event.unicode
                return
        # --- PANTALLA DE INICIO ---
        if self.estado == Juego.ESTADO_INICIO:
            MOUSEBUTTONDOWN = getattr(pygame, 'MOUSEBUTTONDOWN', 1025)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.boton_auto.rect.collidepoint(event.pos):
                    self.modo_automatico = True
                    self.estado = Juego.ESTADO_AUTO
                    self.reiniciar_juego()
                    self.boton_jugar.activo = False
                    self.boton_repartir.activo = True
                    # Mostrar input de pregunta y esperar ENTER
                    self.mostrando_input = True
                    self.pregunta = ""
                    self._auto_fase = 'pregunta'
                    self._auto_last_action_time = pygame.time.get_ticks()
                elif self.boton_manual.rect.collidepoint(event.pos):
                    self.modo_automatico = False
                    self.estado = Juego.ESTADO_JUEGO
                    self.reiniciar_juego()
                    self.boton_jugar.activo = False
                    self.boton_repartir.activo = True
                elif self.boton_instrucciones.rect.collidepoint(event.pos):
                    self.estado = Juego.ESTADO_INSTRUCCIONES
            return
        # --- INSTRUCCIONES ---
        if self.estado == Juego.ESTADO_INSTRUCCIONES:
            KEYDOWN = getattr(pygame, 'KEYDOWN', 768)
            K_ESCAPE = getattr(pygame, 'K_ESCAPE', 27)
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.estado = Juego.ESTADO_INICIO
            return
        # --- JUEGO NORMAL O AUTO ---
        if self.estado == Juego.ESTADO_AUTO:
            # Solo permitir interacción de teclado para la pregunta y ESC
            KEYDOWN = getattr(pygame, 'KEYDOWN', 768)
            K_ESCAPE = getattr(pygame, 'K_ESCAPE', 27)
            # Solo procesar eventos de teclado
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.estado = Juego.ESTADO_INICIO
                for attr in ['_auto_fase', '_auto_jugada_timer', '_reparto_pendiente', '_pregunta_mostrada']:
                    if hasattr(self, attr):
                        delattr(self, attr)
                return
            # Permitir solo la pregunta (input) en modo automático
            if self.mostrando_input:
                K_RETURN = getattr(pygame, 'K_RETURN', 13)
                K_BACKSPACE = getattr(pygame, 'K_BACKSPACE', 8)
                if event.type == KEYDOWN:
                    if event.key == K_RETURN and self.pregunta:
                        print(f"Pregunta realizada: {self.pregunta}")
                        self.mostrando_input = False
                        self.boton_jugar.activo = True
                        self.mostrar_mascota = True
                        # En modo automático, avanzar a la fase de mezclar (no a jugar)
                        if self.estado == Juego.ESTADO_AUTO:
                            self._auto_fase = 'mezclar'
                    elif event.key == K_BACKSPACE:
                        self.pregunta = self.pregunta[:-1]
                    elif hasattr(event, 'unicode') and event.unicode and event.unicode.isprintable():
                        self.pregunta += event.unicode
                return
            # No procesar eventos de mouse en modo automático
            return
        if self.estado == Juego.ESTADO_JUEGO:
            KEYDOWN = getattr(pygame, 'KEYDOWN', 768)
            K_ESCAPE = getattr(pygame, 'K_ESCAPE', 27)
            # Permitir volver al menú with ESC
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.estado = Juego.ESTADO_INICIO
                return
            # ...sigue el código original...

        MOUSEBUTTONDOWN = getattr(pygame, 'MOUSEBUTTONDOWN', 1025)
        MOUSEBUTTONUP = getattr(pygame, 'MOUSEBUTTONUP', 1026)
        MOUSEMOTION = getattr(pygame, 'MOUSEMOTION', 1024)
        if event.type == MOUSEBUTTONDOWN and event.button == 1:  # Click izquierdo
            mouse_pos = event.pos
            # Permitir reiniciar desde la pantalla de resultado
            if self.mostrando_respuesta and self.boton_reiniciar.rect.collidepoint(mouse_pos) and self.boton_reiniciar.activo:
                if self.audio_disponible:
                    self.sonido_click.play()
                self.reiniciar_juego()
                # Siempre volver al menú principal y limpiar variables automáticas
                self.estado = Juego.ESTADO_INICIO
                self.modo_automatico = False
                # Limpiar todas las variables automáticas posibles
                for attr in ['_auto_fase', '_auto_jugada_timer', '_reparto_pendiente', '_pregunta_mostrada', '_mezcla_realizada', '_mazo_barajado', '_auto_anim_carta']:
                    if hasattr(self, attr):
                        delattr(self, attr)
                return
            if not self.jugando:
                # Manejar clicks en botones cuando no estamos jugando
                if self.boton_mezclar.rect.collidepoint(mouse_pos) and self.boton_mezclar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.mezclar_hojeo()
                elif self.boton_repartir.rect.collidepoint(mouse_pos) and self.boton_repartir.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.repartir()
                elif self.boton_jugar.rect.collidepoint(mouse_pos) and self.boton_jugar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.detener_todos_sonidos()  # Asegurarse de que no haya sonidos activos
                    self.iniciar_juego()
                elif self.boton_reiniciar.rect.collidepoint(mouse_pos) and self.boton_reiniciar.activo:
                    if self.audio_disponible:
                        self.sonido_click.play()
                    self.reiniciar_juego()
                    self.estado = Juego.ESTADO_INICIO
            else:
                # Intentar agarrar una carta de la pila actual
                if not self.arrastrando:  # Solo si no estamos arrastrando ya
                    pila_clickeada = self.obtener_pila_clickeada(event.pos)
                    if pila_clickeada == self.pila_actual:
                        pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
                        carta = self.obtener_ultima_carta_no_volteada(pila)
                        if carta:
                            self.reproducir_sonido(self.sonido_tomar)
                            self.arrastrando = True
                            self.carta_arrastrada = carta
                            self.pos_arrastre = event.pos
                            self.pos_origen = posiciones[self.pila_actual]
                            self.pos_origen_index = self.pila_actual

        elif event.type == MOUSEBUTTONUP and event.button == 1:  # Soltar click izquierdo
            if self.arrastrando:
                pila_destino = self.obtener_pila_clickeada(event.pos)
                siguiente_pos = self.obtener_siguiente_posicion(self.carta_arrastrada)
                
                if pila_destino is not None and pila_destino == siguiente_pos:
                    self.reproducir_sonido(self.sonido_soltar)
                    
                    pila_origen = self.cartas_por_posicion[posiciones[self.pos_origen_index]]
                    if self.carta_arrastrada in pila_origen:
                        pila_origen.remove(self.carta_arrastrada)
                    
                    pila_destino_cartas = self.cartas_por_posicion[posiciones[siguiente_pos]]
                    pila_destino_cartas.append(self.carta_arrastrada)
                    self.cartas_volteadas.add(self.carta_arrastrada)
                    self.pila_actual = siguiente_pos
                    
                    # Verificar victoria/derrota
                    if len(self.cartas_volteadas) == self.total_cartas:
                        self.terminar_juego(True)
                    else:
                        nueva_pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
                        if not self.obtener_ultima_carta_no_volteada(nueva_pila):
                            self.terminar_juego(False)
                else:
                    if self.audio_disponible:
                        self.reproducir_sonido(self.sonido_error)
                
                # Limpiar estado de arrastre
                self.arrastrando = False
                self.carta_arrastrada = None
                self.pos_arrastre = None
                
        elif event.type == MOUSEMOTION:
            # Actualizar posición de la carta siendo arrastrada
            if self.arrastrando:
                self.pos_arrastre = event.pos

    def draw(self, surface):
        """
        Dibuja la pantalla principal según el estado actual del juego.
        """
        # --- PANTALLA DE INICIO ---
        if self.estado == Juego.ESTADO_INICIO:
            screen.fill((20, 60, 20))
            # Logo/mascota
            if hasattr(self, 'img_mascota'):
                screen.blit(self.img_mascota, (WIDTH//2 - 75, 80))
            # Título
            titulo = self.font_titulo.render("JUEGO CARTAS", True, (255, 215, 0))
            screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 250))
            # Texto de instrucción para usabilidad
            font_instr = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 28) if os.path.exists(os.path.join("recursos", "JandaEverydayCasual.ttf")) else pygame.font.Font(None, 28)
            texto_instr = font_instr.render("Seleccione el modo de juego:", True, (255,255,255))
            screen.blit(texto_instr, (WIDTH//2 - texto_instr.get_width()//2, 320))
            # Botones
            self.boton_auto.draw(screen)
            self.boton_manual.draw(screen)
            self.boton_instrucciones.draw(screen)
            return
        # --- INSTRUCCIONES ---
        if self.estado == Juego.ESTADO_INSTRUCCIONES:
            screen.fill((30, 30, 60))
            y = 120
            for linea in self.texto_instrucciones:
                txt = self.font_btn.render(linea, True, (255,255,255))
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
                y += 50
            txt_esc = self.font_btn.render("Pulsa ESC para volver", True, (255,255,0))
            screen.blit(txt_esc, (WIDTH//2 - txt_esc.get_width()//2, y+30))
            return
        # --- MODO AUTOMÁTICO ---
        if self.estado == Juego.ESTADO_AUTO:
            # Fondo tipo casino
            surface.fill((10, 40, 10))
            # Llamar al draw normal para mostrar el juego
            self.draw_juego(surface)
            txt = self.font_btn.render("Modo Automático (ESC para menú)", True, (255,255,255))
            surface.blit(txt, (20, 20))
            return
        # --- MODO MANUAL ---
        if self.estado == Juego.ESTADO_JUEGO:
            surface.fill((10, 40, 10))
            self.draw_juego(surface)
            txt = self.font_btn.render("Modo Manual (ESC para menú)", True, (255,255,255))
            surface.blit(txt, (20, 20))
            return

    def draw_juego(self, surface):
        """
        Dibuja la mesa de juego, cartas, animaciones y controles.
        """
        surface.blit(self.fondo, (0, 0))

        # Dibujar imagen meditando solo si corresponde y no hay imagen de respuesta
        if self.mostrar_mascota and not self.mostrando_input and not self.mostrando_respuesta:
            surface.blit(self.img_mascota, (20, 20))

        if self.animando_mezcla:
            if self.estado_animacion == 'inicio':
                # Dibujar mazo moviéndose al centro
                progreso = min(1, self.tiempo_animacion / 500)
                pos_x = self.mazo_pos[0] + (self.pos_central[0] - self.mazo_pos[0]) * progreso
                pos_y = self.mazo_pos[1] + (self.pos_central[1] - self.mazo_pos[1]) * progreso
                surface.blit(self.reverso_base, (pos_x, pos_y))
            elif self.estado_animacion == 'dividiendo':
                progreso = min(1, self.tiempo_animacion / 500)
                pos_izq_x = self.pos_central[0] + (self.pos_inicial_izq[0] - self.pos_central[0]) * progreso
                pos_der_x = self.pos_central[0] + (self.pos_inicial_der[0] - self.pos_central[0]) * progreso
                surface.blit(self.reverso_base, (pos_izq_x, self.pos_central[1]))
                surface.blit(self.reverso_base, (pos_der_x, self.pos_central[1]))
            elif self.estado_animacion == 'mezclando':
                for grupo in self.grupos_mezcla:
                    pos = self.pos_inicial_izq if grupo['lado'] == 'izquierda' else self.pos_inicial_der
                    surface.blit(self.reverso_base, pos)
                if self.carta_actual:
                    surface.blit(self.reverso_base, self.carta_actual['pos_actual'])
                for i, carta in enumerate(self.cartas_mezcladas):
                    surface.blit(self.reverso_base, (self.pos_central[0], self.pos_central[1] - i * 2))
        else:
            if len(self.mazo) > 0:
                for i in range(len(self.mazo)-1, -1, -1):
                    surface.blit(self.mazo[i].imagen_reverso, 
                            (self.mazo_pos[0] + i * self.CARD_OFFSET_V, 
                            self.mazo_pos[1]))

        if self.animando_reparto and self.carta_actual_reparto:
            progreso = self.carta_actual_reparto['progreso']
            pos_inicial = self.mazo_pos
            pos_final = self.carta_actual_reparto['pos_destino']
            pos_actual = (
                pos_inicial[0] + (pos_final[0] - pos_inicial[0]) * progreso,
                pos_inicial[1] + (pos_final[1] - pos_inicial[1]) * progreso
            )
            surface.blit(self.carta_actual_reparto['carta'].imagen_reverso, pos_actual)

        # Dibujar cartas en la mesa
        for _, pos in enumerate(posiciones):
            cartas = self.cartas_por_posicion[pos]
            for i, carta in enumerate(cartas):
                if carta == self.carta_arrastrada:
                    continue  # No dibujar la carta que se está arrastrando
                if carta in self.cartas_volteadas:
                    screen.blit(carta.imagen_frontal, 
                            (pos[0] + i * self.CARD_OFFSET_H, 
                            pos[1]))
                else:
                    screen.blit(carta.imagen_reverso, 
                            (pos[0] + i * self.CARD_OFFSET_H, 
                            pos[1]))

        # Si estamos jugando, resaltar la pila actual y la pila destino válida
        if self.jugando:
            pos_actual = posiciones[self.pila_actual]
            pygame.draw.rect(surface, (255, 255, 0), 
                           (pos_actual[0], pos_actual[1], CARD_WIDTH, CARD_HEIGHT), 2)
            if self.arrastrando:
                siguiente_pos = self.obtener_siguiente_posicion(self.carta_arrastrada)
                pos_destino = posiciones[siguiente_pos]
                pygame.draw.rect(surface, (0, 255, 0), 
                               (pos_destino[0], pos_destino[1], CARD_WIDTH, CARD_HEIGHT), 2)

        if self.arrastrando and self.carta_arrastrada:
            surface.blit(self.carta_arrastrada.imagen_frontal, 
                       (self.pos_arrastre[0] - CARD_WIDTH//2, 
                        self.pos_arrastre[1] - CARD_HEIGHT//2))

        if self.mostrando_respuesta and self.respuesta_img:
            pos_x = WIDTH//2 - self.respuesta_img.get_width()//2
            pos_y = HEIGHT//2 - self.respuesta_img.get_height()//2
            surface.blit(self.respuesta_img, (pos_x, pos_y))

        self.boton_mezclar.draw(surface)
        self.boton_repartir.draw(surface)
        self.boton_jugar.draw(surface)

        if self.mostrando_respuesta and self.respuesta_img:
            pos_x = WIDTH//2 - self.respuesta_img.get_width()//2
            pos_y = HEIGHT//2 - self.respuesta_img.get_height()//2
            surface.blit(self.respuesta_img, (pos_x, pos_y))
            self.boton_reiniciar.rect.centerx = WIDTH//2
            self.boton_reiniciar.rect.top = pos_y + self.respuesta_img.get_height() + 20
            self.boton_reiniciar.draw(surface)

        if self.mostrando_input:
            # Centrar la imagen de pregunta
            pos_x = WIDTH//2 - self.img_pregunta.get_width()//2
            pos_y = HEIGHT//2 - self.img_pregunta.get_height()//2
            surface.blit(self.img_pregunta, (pos_x, pos_y))

            # Definir el área de input centrada dentro de la imagen
            marco_ancho = 320
            marco_alto = 40
            marco_x = pos_x + (self.img_pregunta.get_width() - marco_ancho)//2
            marco_y = pos_y + self.img_pregunta.get_height()//2 + 10
            pygame.draw.rect(surface, (255, 255, 255), (
                marco_x,
                marco_y,
                marco_ancho,
                marco_alto
            ), 2, border_radius=12)

            # Renderizar el texto centrado vertical y horizontalmente
            font_input = pygame.font.Font(os.path.join("recursos", "JandaEverydayCasual.ttf"), 22) if os.path.exists(os.path.join("recursos", "JandaEverydayCasual.ttf")) else pygame.font.Font(None, 22)
            texto_mostrado = self.pregunta[:60]
            text_surface = font_input.render(texto_mostrado, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.centery = marco_y + marco_alto//2
            text_rect.x = marco_x + 12
            # Si el texto es muy largo, recortar para que no se salga
            if text_rect.width > marco_ancho - 24:
                # Recortar el texto para que quepa
                while text_rect.width > marco_ancho - 24 and len(texto_mostrado) > 0:
                    texto_mostrado = texto_mostrado[1:]
                    text_surface = font_input.render(texto_mostrado, True, (0, 0, 0))
                    text_rect = text_surface.get_rect()
                    text_rect.centery = marco_y + marco_alto//2
                    text_rect.x = marco_x + 12
            surface.blit(text_surface, text_rect)

            # Cursor parpadeante al final del texto
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = text_rect.x + text_rect.width + 2
                cursor_y = text_rect.y
                cursor_h = text_rect.height
                if cursor_x < marco_x + marco_ancho - 8:
                    pygame.draw.line(surface, (0, 0, 0),
                                   (cursor_x, cursor_y),
                                   (cursor_x, cursor_y + cursor_h), 2)
    def jugada_automatica(self):
        """
        Realiza una jugada automática (modo automático): mueve la carta a la pila destino.
        """
        # 100% automático: mueve la carta de la pila actual a la pila destino sin interacción de mouse
        if not self.jugando:
            return
        pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
        carta = self.obtener_ultima_carta_no_volteada(pila)
        if carta:
            siguiente_pos = self.obtener_siguiente_posicion(carta)
            pila_origen = self.cartas_por_posicion[posiciones[self.pila_actual]]
            pila_destino = self.cartas_por_posicion[posiciones[siguiente_pos]]
            if carta in pila_origen:
                pila_origen.remove(carta)
            pila_destino.append(carta)
            self.cartas_volteadas.add(carta)
            self.pila_actual = siguiente_pos
            # Verificar victoria/derrota
            if len(self.cartas_volteadas) == self.total_cartas:
                self.terminar_juego(True)
            else:
                nueva_pila = self.cartas_por_posicion[posiciones[self.pila_actual]]
                if not self.obtener_ultima_carta_no_volteada(nueva_pila):
                    self.terminar_juego(False)

###########################################################
# FUNCIÓN PRINCIPAL: Bucle de juego y automatización       #
###########################################################
def main():

    juego = Juego()  # Instancia principal del juego
    running = True
    clock = pygame.time.Clock()
    QUIT = getattr(pygame, 'QUIT', 256)

    # Variables de automatización como atributos del juego
    juego._auto_last_action_time = 0
    juego._auto_action_interval = 2500  # milisegundos (2.5 segundos)

    # Bucle principal del juego
    while running:
        dt = clock.tick(100)  # Controla los FPS
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            # Delegar el manejo de eventos a la clase Juego
            juego.manejar_evento(event)
        # Actualizar animaciones
        juego.actualizar_animacion(dt)
        juego.actualizar_reparto(dt)

        # --- Automatización del modo automático ---
        if getattr(juego, 'estado', None) == Juego.ESTADO_AUTO:
            # Fase: mezclar
            if getattr(juego, '_auto_fase', None) == 'mezclar':
                # Solo iniciar la mezcla si no está animando
                if not juego.animando_mezcla:
                    if not hasattr(juego, '_mezcla_realizada') or not juego._mezcla_realizada:
                        juego.mezclar_hojeo()
                        juego._mezcla_realizada = True
                    else:
                        # Si la animación ya terminó y la mezcla ya se hizo, pasar a repartir
                        juego._auto_fase = 'repartir'
                        juego._auto_last_action_time = current_time
            # Fase: repartir
            elif getattr(juego, '_auto_fase', None) == 'repartir':
                # Solo iniciar el reparto si la mezcla terminó y el botón repartir está activo
                if not juego.animando_reparto and juego.boton_repartir.activo:
                    juego.repartir()
                    juego._auto_fase = 'esperando_reparto'
                    juego._auto_last_action_time = current_time
            # Nueva fase: esperar a que termine el reparto antes de jugar
            elif getattr(juego, '_auto_fase', None) == 'esperando_reparto':
                if not juego.animando_reparto:
                    juego.jugando = True
                    juego._auto_fase = 'jugar'
                    juego._auto_last_action_time = current_time
            # Fase: pregunta (esperar input del usuario)
            elif getattr(juego, '_auto_fase', None) == 'pregunta':
                # Esperar a que el usuario escriba la pregunta y presione ENTER
                pass
            # Fase: jugar (jugadas automáticas)
            elif getattr(juego, '_auto_fase', None) == 'jugar' and juego.jugando:
                if current_time - juego._auto_last_action_time > juego._auto_action_interval:
                    juego.jugada_automatica()
                    juego._auto_last_action_time = current_time

        # Dibuja la pantalla actual
        juego.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    # Al salir del bucle, cerrar Pygame
    if hasattr(pygame, 'quit'):
        pygame.quit()


# Punto de entrada del programa
if __name__ == "__main__":
    main()