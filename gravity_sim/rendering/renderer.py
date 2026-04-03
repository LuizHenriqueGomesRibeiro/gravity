import tkinter as tk
import math


class Renderer:
    """Renderiza todos os elementos visuais no canvas."""

    def __init__(self, game):
        self.game = game
        self.grid_size = 50

    def draw(self):
        canvas = self.game.canvas
        canvas.delete("all")
        self._draw_grid()
        self._draw_axes()
        self._draw_trails()
        self._draw_bodies()
        self._draw_slingshot()
        self._draw_hud()

    def _draw_grid(self):
        cam = self.game.camera
        canvas = self.game.canvas
        step = self.grid_size
        while step * cam.zoom < 20:
            step *= 5
        while step * cam.zoom > 200 and step > 1:
            step /= 5

        left, top = cam.screen_to_world(0, 0)
        right, bottom = cam.screen_to_world(cam.width, cam.height)

        x = (left // step) * step
        while x <= right:
            sx, _ = cam.world_to_screen(x, 0)
            canvas.create_line(sx, 0, sx, cam.height, fill="#1a1a2e")
            x += step

        y = (bottom // step) * step
        while y <= top:
            _, sy = cam.world_to_screen(0, y)
            canvas.create_line(0, sy, cam.width, sy, fill="#1a1a2e")
            y += step

    def _draw_axes(self):
        cam = self.game.camera
        canvas = self.game.canvas
        _, sy = cam.world_to_screen(0, 0)
        if 0 <= sy <= cam.height:
            canvas.create_line(0, sy, cam.width, sy, fill="#ff4444", width=1)
        sx, _ = cam.world_to_screen(0, 0)
        if 0 <= sx <= cam.width:
            canvas.create_line(sx, 0, sx, cam.height, fill="#44ff44", width=1)
        if 0 <= sx <= cam.width and 0 <= sy <= cam.height:
            r = 4
            canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                               fill="white", outline="white")

    def _draw_trails(self):
        if not self.game.show_trails:
            return
        cam = self.game.camera
        canvas = self.game.canvas
        for body in self.game.bodies:
            # Trajetória simulada (se existir)
            if hasattr(body, 'simulated_traj') and body.simulated_traj:
                traj = body.simulated_traj
                if len(traj) >= 2:
                    points = []
                    for wx, wy in traj:
                        sx, sy = cam.world_to_screen(wx, wy)
                        points.extend([sx, sy])
                    if len(points) >= 4:
                        canvas.create_line(*points, fill="#aaaaaa", width=1, dash=(2, 6))
            # Traço real
            if body.fixed or body.is_fragment or len(body.trail) < 2:
                continue
            trail = body.trail
            step = max(1, len(trail) // 1000)
            points = []
            for i in range(0, len(trail), step):
                sx, sy = cam.world_to_screen(trail[i][0], trail[i][1])
                points.extend([sx, sy])
            sx, sy = cam.world_to_screen(trail[-1][0], trail[-1][1])
            points.extend([sx, sy])
            if len(points) >= 4:
                canvas.create_line(*points, fill=body.color, width=2)

    def _draw_bodies(self):
        cam = self.game.camera
        canvas = self.game.canvas
        for body in self.game.bodies:
            sx, sy = cam.world_to_screen(body.x, body.y)
            r = max(body.radius * cam.zoom, 1)
            if (sx + r < -50 or sx - r > cam.width + 50 or
                    sy + r < -50 or sy - r > cam.height + 50):
                continue
            canvas.create_oval(sx - r, sy - r, sx + r, sy + r,
                               fill=body.color, outline=body.color)

    def _draw_slingshot(self):
        inp = self.game.input_handler
        if not inp.launching:
            return

        cam = self.game.camera
        canvas = self.game.canvas
        physics = self.game.physics

        sx1, sy1 = cam.world_to_screen(inp.launch_start_wx, inp.launch_start_wy)
        sx2, sy2 = cam.world_to_screen(inp.launch_mouse_wx, inp.launch_mouse_wy)

        vx = inp.launch_vx
        vy = inp.launch_vy

        # Trajetória simulada
        traj = physics.simulate_trajectory(
            self.game.bodies,
            inp.launch_start_wx, inp.launch_start_wy,
            vx, vy, inp.launch_radius
        )
        if len(traj) >= 2:
            screen_pts = []
            for wx, wy in traj:
                sx, sy = cam.world_to_screen(wx, wy)
                screen_pts.extend([sx, sy])
            canvas.create_line(*screen_pts, fill="#ffffff",
                               width=1, dash=(3, 5), smooth=True)

        # Linha do arrasto
        canvas.create_line(sx1, sy1, sx2, sy2, fill="#666666",
                           width=1, dash=(4, 4))

        # Seta de velocidade
        arrow_ex = inp.launch_start_wx + vx * 0.3
        arrow_ey = inp.launch_start_wy + vy * 0.3
        asx, asy = cam.world_to_screen(arrow_ex, arrow_ey)
        canvas.create_line(sx1, sy1, asx, asy, fill="#44ff44",
                           width=2, arrow=tk.LAST)

        # Círculo preview
        r = max(inp.launch_radius * cam.zoom, 2)
        color = inp.PLANET_COLORS[inp.planet_counter % len(inp.PLANET_COLORS)]
        canvas.create_oval(sx1 - r, sy1 - r, sx1 + r, sy1 + r,
                           fill=color, outline=color)

        # Corpo alvo de órbita
        orbit_target = inp.launch_orbit_target
        if orbit_target is None:
            nearby, _ = physics.find_dominant_body(
                self.game.bodies, inp.launch_start_wx, inp.launch_start_wy
            )
        else:
            nearby = orbit_target
        if nearby:
            bsx, bsy = cam.world_to_screen(nearby.x, nearby.y)
            canvas.create_line(sx1, sy1, bsx, bsy,
                               fill="#ffff44" if orbit_target else "#444400",
                               width=1, dash=(2, 4))
            if orbit_target:
                orb_dist = math.sqrt(
                    (inp.launch_start_wx - orbit_target.x) ** 2 +
                    (inp.launch_start_wy - orbit_target.y) ** 2
                )
                orb_r = orb_dist * cam.zoom
                canvas.create_oval(
                    bsx - orb_r, bsy - orb_r, bsx + orb_r, bsy + orb_r,
                    outline="#ffff44", width=1, dash=(3, 5)
                )

        # Info
        speed = math.sqrt(vx * vx + vy * vy)
        G = 6.674e-11
        g_surface = G * inp.launch_real_mass / (inp.launch_real_radius ** 2)
        dist_sol = math.sqrt(inp.launch_start_wx**2 + inp.launch_start_wy**2)
        dist_au = dist_sol / physics.AU
        orbit_info = f"  [O: orbitar {nearby.name}]" if nearby else ""
        info = (f"v={speed:.1f}  m={inp.launch_real_mass:.2e}kg  "
                f"g={g_surface:.1f}m/s\u00b2  d\u2609={dist_au:.2f}AU{orbit_info}")
        canvas.create_text(sx1, sy1 - r - 12, text=info,
                           fill="white", font=("Consolas", 9))

    def _draw_hud(self):
        cam = self.game.camera
        canvas = self.game.canvas
        physics = self.game.physics
        canvas.delete("hud")
        zoom_pct = int(cam.zoom * 100)
        G = 6.674e-11
        inp = self.game.input_handler

        n_bodies = len(self.game.bodies)
        n_frags = sum(1 for b in self.game.bodies if b.is_fragment)
        lines = [
            f"Câmera: ({cam.x:.1f}, {cam.y:.1f})  "
            f"Mouse: ({inp.mouse_world_x:.1f}, {inp.mouse_world_y:.1f})  "
            f"Zoom: {zoom_pct}%",
            f"Tempo: {physics.time_scale:.1f}x  "
            f"Corpos: {n_bodies}" + (f" ({n_frags} frag)" if n_frags else "")
            + ("  [PAUSADO]" if self.game.paused else "")
        ]

        if inp.hovered_body:
            b = inp.hovered_body
            lines.append("")
            lines.append(f"[ {b.name} ]")
            if b.real_mass and b.real_radius:
                g_surface = G * b.real_mass / (b.real_radius ** 2)
                lines.append(f"  Massa: {b.real_mass:.3e} kg")
                lines.append(f"  Raio: {b.real_radius:.3e} m")
                lines.append(f"  Gravidade: {g_surface:.1f} m/s²")
            else:
                lines.append(f"  Massa: {b.mass:.3e} (jogo)")
            speed = math.sqrt(b.vx * b.vx + b.vy * b.vy)
            lines.append(f"  Velocidade: {speed:.1f} u/s")

        y_offset = 10
        for line in lines:
            canvas.create_text(
                10, y_offset, text=line, fill="white", anchor="nw",
                font=("Consolas", 11), tags="hud",
            )
            y_offset += 18

        controls = "Scroll: Zoom | Mid Mouse: Pan | LClick: Lançar | P: Pausar | </>: Tempo | O: Orbitar | H: Trilhas"
        canvas.create_text(
            10, cam.height - 10, text=controls, fill="#666666",
            anchor="sw", font=("Consolas", 9), tags="hud",
        )
