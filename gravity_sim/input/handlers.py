import math
from gravity_sim.models.body import CelestialBody



class InputHandler:
    """Gerencia entrada do usuário: mouse e teclado."""

    def simulate_all_trajectories(self):
        """Simula e armazena trajetórias para todos os corpos não fixos e não fragmentos."""
        physics = self.game.physics
        bodies = self.game.bodies
        for body in bodies:
            if body.fixed or body.is_fragment:
                body.simulated_traj = []
                continue
            # Simula trajetória considerando todos os corpos atuais
            body.simulated_traj = physics.simulate_trajectory(
                bodies,
                body.x, body.y,
                body.vx, body.vy,
                body.radius,
                max_steps=2000
            )

    PLANET_COLORS = [
        "#4488ff", "#ff6644", "#44ff88", "#ff44ff",
        "#44ffff", "#ffaa22", "#aa44ff", "#ff4488",
    ]
    CENTER_OF_MASS_TARGET = "center_of_mass"

    def __init__(self, game):
        self.game = game
        self.canvas = game.canvas

        # Drag state (middle mouse pan)
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Slingshot state (left mouse)
        self.launching = False
        self.launch_start_wx = 0.0
        self.launch_start_wy = 0.0
        self.launch_mouse_wx = 0.0
        self.launch_mouse_wy = 0.0
        self.launch_vx = 0.0
        self.launch_vy = 0.0
        self.launch_wasd_active = False
        self.launch_orbit_target = None
        self.velocity_scale = 1.5
        self.planet_counter = 0
        self.launch_mass = 195.0
        self.launch_real_mass = 5.972e24
        self.launch_radius = 5
        self.launch_real_radius = 6.371e6

        # WASD
        self.wasd_speed_step = 5.0
        self.wasd_angle_step = 5.0

        # Mouse world position
        self.mouse_world_x = 0.0
        self.mouse_world_y = 0.0
        self.hovered_body = None

        self._bind_events()

    def _bind_events(self):
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", self._on_scroll)
        self.canvas.bind("<Button-5>", self._on_scroll)
        self.canvas.bind("<ButtonPress-2>", self._on_mid_down)
        self.canvas.bind("<B2-Motion>", self._on_mid_drag)
        self.canvas.bind("<ButtonPress-1>", self._on_left_down)
        self.canvas.bind("<Double-Button-1>", self._on_left_double_click)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_up)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Configure>", self._on_resize)
        self.game.root.bind("<Key>", self._on_key)
        self.canvas.focus_set()

    def _on_scroll(self, event):
        delta = getattr(event, "delta", 0)
        zoom_in = delta > 0 or getattr(event, "num", 0) == 4
        self.game.camera.apply_scroll(event.x, event.y, zoom_in)

    def _on_mid_down(self, event):
        self.game.tracked_body = None
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_mid_drag(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.game.camera.apply_pan(dx, dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_left_down(self, event):
        cam = self.game.camera
        wx, wy = cam.screen_to_world(event.x, event.y)
        self.launching = True
        self.launch_start_wx = wx
        self.launch_start_wy = wy
        self.launch_mouse_wx = wx
        self.launch_mouse_wy = wy
        self.launch_vx = 0.0
        self.launch_vy = 0.0
        self.launch_wasd_active = False
        self.launch_orbit_target = None
        self.canvas.focus_set()

    def _on_left_double_click(self, event):
        cam = self.game.camera
        wx, wy = cam.screen_to_world(event.x, event.y)
        center = self._center_of_mass_at_world(wx, wy)
        if center is not None:
            self.game.tracked_body = self.CENTER_OF_MASS_TARGET
            self.launching = False
            cam.x = center["x"]
            cam.y = center["y"]
            self.canvas.focus_set()
            return

        body = self._body_at_world(wx, wy)
        if body is None:
            return
        self.game.tracked_body = body
        self.launching = False
        cam.x = body.x
        cam.y = body.y
        self.canvas.focus_set()

    def _on_left_drag(self, event):
        if self.launching:
            cam = self.game.camera
            self.launch_mouse_wx, self.launch_mouse_wy = cam.screen_to_world(
                event.x, event.y
            )
            if not self.launch_wasd_active:
                self.launch_vx = (self.launch_start_wx - self.launch_mouse_wx) * self.velocity_scale
                self.launch_vy = (self.launch_start_wy - self.launch_mouse_wy) * self.velocity_scale

    def _on_left_up(self, event):
        # Agora, apenas libera o modo de arrasto, mas mantém self.launching True
        if not self.launching:
            return
        # O usuário pode soltar o mouse, mas a criação só ocorre com Enter
        pass

    def _on_mouse_move(self, event):
        cam = self.game.camera
        self.mouse_world_x, self.mouse_world_y = cam.screen_to_world(
            event.x, event.y
        )
        self._update_hover()

    def _on_key(self, event):
        key = event.keysym.lower()

        if key == 'p':
            self.game.paused = not self.game.paused
            return
        if key == 'h':
            self.game.show_trails = not self.game.show_trails
            return

        if key == 'comma' or key == 'less':
            self.game.physics.time_scale = max(0.1, self.game.physics.time_scale / 2)
            return
        if key == 'period' or key == 'greater':
            self.game.physics.time_scale = min(64.0, self.game.physics.time_scale * 2)
            return

        if not self.launching:
            return

        # Enter cria o planeta
        if key == 'return':
            color = self.PLANET_COLORS[self.planet_counter % len(self.PLANET_COLORS)]
            self.planet_counter += 1
            planet = CelestialBody(
                name=f"Planeta {self.planet_counter}",
                x=self.launch_start_wx,
                y=self.launch_start_wy,
                mass=self.launch_mass,
                radius=self.launch_radius,
                color=color,
                vx=self.launch_vx,
                vy=self.launch_vy,
                real_mass=self.launch_real_mass,
                real_radius=self.launch_real_radius,
            )
            self.game.bodies.append(planet)
            # Simula trajetórias de todos os corpos após adicionar novo planeta
            self.simulate_all_trajectories()
            self.launching = False
            return

        # Del cancela a criação
        if key == 'delete':
            self.launching = False
            return

        # Seleção de planeta para orbitar
        if key in ['bracketleft', 'bracketright']:
            targets = self._get_orbit_targets()
            if not targets:
                return
            # Se não há alvo, começa do mais próximo
            if self.launch_orbit_target is None:
                # Seleciona o corpo mais próximo do ponto de lançamento
                physics = self.game.physics
                target, _ = physics.find_dominant_body(
                    self.game.bodies, self.launch_start_wx, self.launch_start_wy
                )
                if target is not None and target in targets:
                    idx = targets.index(target)
                else:
                    idx = 0
            elif self.launch_orbit_target in targets:
                idx = targets.index(self.launch_orbit_target)
            else:
                idx = 0
            if key == 'bracketright':
                idx = (idx + 1) % len(targets)
            else:
                idx = (idx - 1) % len(targets)
            self._apply_orbit_target_velocity(targets[idx])
            return

        if key == 'o':
            self._apply_orbit_velocity()
            return
        if key == 'c':
            self._apply_center_of_mass_orbit_velocity()
            return
        if key == 'q':
            self.launch_mass = max(1.0, self.launch_mass / 1.5)
            self.launch_real_mass /= 1.5
            self.launch_radius = max(1, self.launch_radius / 1.5 ** (1/3))
            self.launch_real_radius /= 1.5 ** (1/3)
            return
        if key == 'e':
            self.launch_mass *= 1.5
            self.launch_real_mass *= 1.5
            self.launch_radius *= 1.5 ** (1/3)
            self.launch_real_radius *= 1.5 ** (1/3)
            return

        speed = math.sqrt(self.launch_vx**2 + self.launch_vy**2)
        if speed < 0.01:
            angle = 0.0
        else:
            angle = math.atan2(self.launch_vy, self.launch_vx)

        if key == 'w':
            speed += self.wasd_speed_step
        elif key == 's':
            speed = max(0, speed - self.wasd_speed_step)
        elif key == 'a':
            angle += math.radians(self.wasd_angle_step)
        elif key == 'd':
            angle -= math.radians(self.wasd_angle_step)
        else:
            return

        self.launch_wasd_active = True
        self.launch_vx = speed * math.cos(angle)
        self.launch_vy = speed * math.sin(angle)

    def _apply_orbit_velocity(self):
        if self.launch_orbit_target == self.CENTER_OF_MASS_TARGET:
            self._apply_center_of_mass_orbit_velocity()
            return

        physics = self.game.physics
        target, dist = physics.find_dominant_body(
            self.game.bodies, self.launch_start_wx, self.launch_start_wy
        )
        if target is None or dist < 1e-6:
            return
        self.launch_orbit_target = target
        vx, vy = physics.compute_orbit_velocity(
            target, self.launch_start_wx, self.launch_start_wy
        )
        self.launch_vx = vx
        self.launch_vy = vy
        self.launch_wasd_active = True

    def _apply_center_of_mass_orbit_velocity(self):
        self._apply_orbit_target_velocity(self.CENTER_OF_MASS_TARGET)

    def _get_orbit_targets(self):
        targets = [b for b in self.game.bodies if b is not None]
        if self.game.physics.compute_center_of_mass(self.game.bodies) is not None:
            targets.append(self.CENTER_OF_MASS_TARGET)
        return targets

    def _apply_orbit_target_velocity(self, target):
        if target == self.CENTER_OF_MASS_TARGET:
            self._apply_center_of_mass_target_velocity()
            return

        vx, vy = self.game.physics.compute_orbit_velocity(
            target, self.launch_start_wx, self.launch_start_wy
        )
        self.launch_orbit_target = target
        self.launch_vx = vx
        self.launch_vy = vy
        self.launch_wasd_active = True

    def _apply_center_of_mass_target_velocity(self):
        physics = self.game.physics
        center = physics.compute_center_of_mass(self.game.bodies)
        if center is None:
            return
        vx, vy = physics.compute_orbit_velocity_around_point(
            center["x"], center["y"], center["vx"], center["vy"],
            center["mass"], self.launch_start_wx, self.launch_start_wy
        )
        if vx == 0.0 and vy == 0.0:
            return
        self.launch_orbit_target = self.CENTER_OF_MASS_TARGET
        self.launch_vx = vx
        self.launch_vy = vy
        self.launch_wasd_active = True

    def _update_hover(self):
        self.hovered_body = self._body_at_world(
            self.mouse_world_x, self.mouse_world_y
        )

    def _body_at_world(self, wx, wy):
        min_click_radius = 6 / max(self.game.camera.zoom, 0.001)
        for body in reversed(self.game.bodies):
            dx = wx - body.x
            dy = wy - body.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= max(body.radius, min_click_radius):
                return body
        return None

    def _center_of_mass_at_world(self, wx, wy):
        center = self.game.physics.compute_center_of_mass(self.game.bodies)
        if center is None:
            return None

        min_click_radius = 8 / max(self.game.camera.zoom, 0.001)
        dx = wx - center["x"]
        dy = wy - center["y"]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= min_click_radius:
            return center
        return None

    def _on_resize(self, event):
        self.game.camera.resize(event.width, event.height)
