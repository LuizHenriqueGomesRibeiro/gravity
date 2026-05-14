import tkinter as tk

from gravity_sim.core.physics import PhysicsEngine
from gravity_sim.core.camera import Camera
from gravity_sim.input.handlers import InputHandler
from gravity_sim.rendering.renderer import Renderer


class GravityGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jogo de Gravidade")

        width = 1000
        height = 800

        self.canvas = tk.Canvas(
            self.root, width=width, height=height, bg="black"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.paused = False
        self.show_trails = True
        self.tracked_body = None

        # Corpos celestes
        self.bodies = []

        # Subsistemas
        self.camera = Camera(width, height)
        self.physics = PhysicsEngine()
        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self)

        self._game_loop()
        self.root.mainloop()

    def _game_loop(self):
        if not self.paused:
            self.physics.step(self.bodies)
        self._update_tracked_camera()
        self.renderer.draw()
        self.root.after(16, self._game_loop)

    def _update_tracked_camera(self):
        if self.tracked_body not in self.bodies:
            self.tracked_body = None
            return
        if self.tracked_body is not None:
            self.camera.x = self.tracked_body.x
            self.camera.y = self.tracked_body.y
