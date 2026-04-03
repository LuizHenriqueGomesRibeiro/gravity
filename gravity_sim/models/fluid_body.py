import taichi as ti
import numpy as np

@ti.data_oriented
class FluidBody:
    def __init__(self, center, radius, particle_count, mass, color=(0.5, 0.5, 1.0)):
        self.center = np.array(center, dtype=np.float32)
        self.radius = radius
        self.particle_count = particle_count
        self.mass = mass
        self.color = color
        self.dim = 2
        self.positions = ti.Vector.field(self.dim, dtype=ti.f32, shape=particle_count)
        self.velocities = ti.Vector.field(self.dim, dtype=ti.f32, shape=particle_count)
        self.forces = ti.Vector.field(self.dim, dtype=ti.f32, shape=particle_count)
        self.particle_mass = mass / particle_count
        self._init_particles()

    def _init_particles(self):
        # Distribui partículas em um círculo
        for i in range(self.particle_count):
            angle = 2 * np.pi * (i / self.particle_count)
            r = self.radius * np.sqrt(np.random.rand())
            x = self.center[0] + r * np.cos(angle)
            y = self.center[1] + r * np.sin(angle)
            self.positions[i] = [x, y]
            self.velocities[i] = [0.0, 0.0]

    @ti.kernel
    def apply_gravity(self, g: ti.f32):
        for i in range(self.particle_count):
            self.forces[i] = ti.Vector([0.0, -g * self.particle_mass])

    @ti.kernel
    def step(self, dt: ti.f32):
        for i in range(self.particle_count):
            self.velocities[i] += dt * self.forces[i] / self.particle_mass
            self.positions[i] += dt * self.velocities[i]

    def update(self, dt, g=9.8):
        self.apply_gravity(g)
        self.step(dt)

    def get_positions(self):
        return self.positions.to_numpy()
