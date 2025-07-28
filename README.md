# Juego de Cartas (Modo Automático y Manual)

Este proyecto es un juego de cartas interactivo desarrollado en Python usando la librería Pygame. Permite jugar en modo manual o completamente automático, simulando la experiencia de un casino, con animaciones de mezcla y reparto, botones gráficos y sonidos.
<img width="1505" height="1017" alt="image" src="https://github.com/user-attachments/assets/ba87d5f3-b036-4962-b940-a2d2c161f6e2" />


## Características principales

- **Modo Automático**: El juego se desarrolla solo tras ingresar una pregunta, mostrando animaciones de mezcla, reparto y jugadas automáticas.
- **Modo Manual**: El usuario puede arrastrar cartas y controlar el flujo del juego.
- **Animaciones profesionales**: Mezcla tipo riffle, reparto carta por carta, movimiento animado de cartas.
- **Interfaz gráfica amigable**: Botones grandes, colores claros, instrucciones visibles.
- **Sonidos y música**: Efectos de barajar, repartir, tomar y soltar cartas, música de fondo.
- **Preguntas personalizadas**: El usuario puede ingresar una pregunta antes de iniciar el modo automático.
- **Reinicio y control total**: Botón de reinicio que regresa siempre al menú principal y limpia el estado.

## Estructura del proyecto

```
JuegoBaraja/
├── baraja.py           # Lógica principal del juego (puede llamarse juegoBaraja.py)
├── botones.py          # Demo de interfaz de botones con Pygame
├── img/                # Imágenes de cartas (frontal y reverso)
├── recursos/           # Recursos gráficos y de audio (botones, sonidos, fuentes, fondo)
└── README.md           # Este archivo
```

## Requisitos

- Python 3.8 o superior
- pygame >= 2.0

Instala las dependencias con:

```bash
pip install pygame
```

## Cómo ejecutar el juego

1. Clona el repositorio o descarga el código.
2. Asegúrate de tener la carpeta `img/` con todas las imágenes de cartas y la carpeta `recursos/` con los recursos necesarios.
3. Ejecuta el archivo principal:

```bash
python juegoBaraja.py
```

4. Para probar solo la interfaz de botones:

```bash
python botones.py
```

## Controles y modos de juego

- **Modo Automático**: Pulsa el botón "Modo Automático", ingresa una pregunta y presiona ENTER. El juego se desarrolla solo.
- **Modo Manual**: Pulsa el botón "Modo Manual" y juega arrastrando cartas.
- **Botón Reiniciar**: Siempre regresa al menú principal y limpia el estado.
- **Botón Instrucciones**: Muestra las reglas básicas en pantalla.

## Recursos incluidos

- Imágenes de cartas (PNG)
- Imágenes de botones y fondo
- Fuentes personalizadas (JandaEverydayCasual.ttf)
- Sonidos y música de fondo (MP3)

## Créditos y licencias

- Fuente: [Janda Everyday Casual](https://www.dafont.com/janda-everyday-casual.font)
- Código: Desarrollado por Andersson Ambuludi.

## Autor

- Andersson Ambuludi
