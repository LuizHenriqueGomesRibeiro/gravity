from collections import deque


class CelestialBody:
    """Corpo celeste com propriedades físicas reais."""

    def __init__(self, name, x, y, mass, radius, color, glow_color=None,
                 vx=0.0, vy=0.0, fixed=False,
                 real_mass=None, real_radius=None, is_fragment=False):
        self.name = name
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.color = color
        self.glow_color = glow_color or color
        self.fixed = fixed
        self.trail = deque(maxlen=3000 if not is_fragment else 300)
        self.real_mass = real_mass      # kg
        self.real_radius = real_radius  # metros
        self.is_fragment = is_fragment  # fragmento de colisão/maré
