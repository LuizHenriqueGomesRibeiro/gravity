import tkinter as tk

from gravity_sim.models.body import CelestialBody
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

        # Corpos celestes
        self.bodies = []

        # Subsistemas
        self.camera = Camera(width, height)
        self.physics = PhysicsEngine()
        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self)

        self._create_sun()
        self._game_loop()
        self.root.mainloop()

    def _create_sun(self):
        sun = CelestialBody(
            name="Sol",
            x=0, y=0,
            mass=8e5,
            radius=80,
            color="#FFD700",
            glow_color="#FFA500",
            fixed=True,
            real_mass=1.989e30,
            real_radius=6.963e8,
        )
        self.bodies.append(sun)

    def _game_loop(self):
        if not self.paused:
            self.physics.step(self.bodies)
        self.renderer.draw()
        self.root.after(16, self._game_loop)
