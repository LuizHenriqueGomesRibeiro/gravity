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
        self._draw_trails()
        self._draw_center_of_mass()
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
        origin_x = 0
        origin_y = 0
        if self.game.tracked_body == self.game.CENTER_OF_MASS_TARGET:
            center = self.game.physics.compute_center_of_mass(self.game.bodies)
            if center is not None:
                origin_x = center["x"]
                origin_y = center["y"]
        elif self.game.tracked_body is not None:
            origin_x = self.game.tracked_body.x
            origin_y = self.game.tracked_body.y

        x = ((left - origin_x) // step) * step + origin_x
        while x <= right:
            sx, _ = cam.world_to_screen(x, 0)
            canvas.create_line(sx, 0, sx, cam.height, fill="#1a1a2e")
            x += step

        y = ((bottom - origin_y) // step) * step + origin_y
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

    def _draw_center_of_mass(self):
        center = self._get_center_of_mass()
        if center is None:
            return

        cam = self.game.camera
        canvas = self.game.canvas
        sx, sy = cam.world_to_screen(center[0], center[1])
        if sx < -30 or sx > cam.width + 30 or sy < -30 or sy > cam.height + 30:
            return

        r = 3
        color = "#88ccff"
        canvas.create_oval(
            sx - r, sy - r, sx + r, sy + r,
            fill=color, outline=color
        )
        canvas.create_text(
            sx + 7, sy - 7, text="CM", fill=color,
            anchor="w", font=("Consolas", 9)
        )

    def _get_center_of_mass(self):
        center = self.game.physics.compute_center_of_mass(self.game.bodies)
        if center is None:
            return None
        return center["x"], center["y"]

    def _draw_slingshot(self):
        inp = self.game.input_handler
        if not inp.launching:
            return

        cam = self.game.camera
        canvas = self.game.canvas
        physics = self.game.physics

        sx1, sy1 = cam.world_to_screen(inp.launch_start_wx, inp.launch_start_wy)
        sx2, sy2 = cam.world_to_screen(inp.launch_mouse_wx, inp.launch_mouse_wy)

        if inp.binary_mode:
            self._draw_binary_preview(sx1, sy1)
            return

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
        center = physics.compute_center_of_mass(self.game.bodies)
        nearby = None
        nearby_name = None
        nearby_x = None
        nearby_y = None
        orbit_selected = orbit_target is not None

        if orbit_target == inp.CENTER_OF_MASS_TARGET and center is not None:
            nearby_name = "CM"
            nearby_x = center["x"]
            nearby_y = center["y"]
        elif orbit_target == inp.CENTER_OF_MASS_TARGET:
            pass
        elif orbit_target is None:
            nearby, _ = physics.find_dominant_body(
                self.game.bodies, inp.launch_start_wx, inp.launch_start_wy
            )
            if nearby:
                nearby_name = nearby.name
                nearby_x = nearby.x
                nearby_y = nearby.y
        else:
            nearby = orbit_target
            nearby_name = nearby.name
            nearby_x = nearby.x
            nearby_y = nearby.y

        if nearby_name is not None:
            bsx, bsy = cam.world_to_screen(nearby_x, nearby_y)
            canvas.create_line(sx1, sy1, bsx, bsy,
                               fill="#ffff44" if orbit_selected else "#444400",
                               width=1, dash=(2, 4))
            if orbit_selected:
                orb_dist = math.sqrt(
                    (inp.launch_start_wx - nearby_x) ** 2 +
                    (inp.launch_start_wy - nearby_y) ** 2
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
        orbit_info = ""
        if nearby_name:
            orbit_info = f"  [O: orbitar {nearby_name} | C: orbitar CM]"
        elif center is not None:
            orbit_info = "  [C: orbitar CM]"
        info = (f"v={speed:.1f}  m={inp.launch_real_mass:.2e}kg  "
                f"g={g_surface:.1f}m/s\u00b2  d\u2609={dist_au:.2f}AU{orbit_info}")
        canvas.create_text(sx1, sy1 - r - 12, text=info,
                           fill="white", font=("Consolas", 9))

    def _draw_binary_preview(self, sx_cm, sy_cm):
        inp = self.game.input_handler
        cam = self.game.camera
        canvas = self.game.canvas

        separation = max(inp.binary_separation, inp.launch_radius * 8)
        dx = inp.launch_mouse_wx - inp.launch_start_wx
        dy = inp.launch_mouse_wy - inp.launch_start_wy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = dx / dist, dy / dist

        if inp.binary_mode == inp.BINARY_COMPANION:
            mass_1 = inp.launch_mass
            mass_2 = inp.launch_mass * inp.binary_companion_ratio
            real_mass_1 = inp.launch_real_mass
            real_mass_2 = inp.launch_real_mass * inp.binary_companion_ratio
            mode_name = "binario menor"
        else:
            mass_1 = inp.launch_mass
            mass_2 = inp.launch_mass
            real_mass_1 = inp.launch_real_mass
            real_mass_2 = inp.launch_real_mass
            mode_name = "binario igual"

        total_mass = mass_1 + mass_2
        radius_1 = inp.launch_radius
        radius_2 = inp.launch_radius * (mass_2 / mass_1) ** (1 / 3)
        real_radius_1 = inp.launch_real_radius
        real_radius_2 = inp.launch_real_radius * (mass_2 / mass_1) ** (1 / 3)
        separation = max(separation, (radius_1 + radius_2) * 3)
        r1 = separation * mass_2 / total_mass
        r2 = separation * mass_1 / total_mass

        x1 = inp.launch_start_wx - ux * r1
        y1 = inp.launch_start_wy - uy * r1
        x2 = inp.launch_start_wx + ux * r2
        y2 = inp.launch_start_wy + uy * r2
        sx1, sy1 = cam.world_to_screen(x1, y1)
        sx2, sy2 = cam.world_to_screen(x2, y2)

        color_1 = inp.PLANET_COLORS[inp.planet_counter % len(inp.PLANET_COLORS)]
        color_2 = inp.PLANET_COLORS[(inp.planet_counter + 1) % len(inp.PLANET_COLORS)]
        pr1 = max(radius_1 * cam.zoom, 2)
        pr2 = max(radius_2 * cam.zoom, 2)

        canvas.create_line(sx1, sy1, sx2, sy2, fill="#666666", dash=(4, 4))
        canvas.create_oval(sx1 - pr1, sy1 - pr1, sx1 + pr1, sy1 + pr1,
                           fill=color_1, outline=color_1)
        canvas.create_oval(sx2 - pr2, sy2 - pr2, sx2 + pr2, sy2 + pr2,
                           fill=color_2, outline=color_2)

        cm_r = 3
        canvas.create_oval(
            sx_cm - cm_r, sy_cm - cm_r, sx_cm + cm_r, sy_cm + cm_r,
            fill="#88ccff", outline="#88ccff"
        )
        canvas.create_text(
            sx_cm + 7, sy_cm - 7, text="CM", fill="#88ccff",
            anchor="w", font=("Consolas", 9)
        )

        orbit_r1 = r1 * cam.zoom
        orbit_r2 = r2 * cam.zoom
        canvas.create_oval(
            sx_cm - orbit_r1, sy_cm - orbit_r1,
            sx_cm + orbit_r1, sy_cm + orbit_r1,
            outline="#ffff44", width=1, dash=(3, 5)
        )
        canvas.create_oval(
            sx_cm - orbit_r2, sy_cm - orbit_r2,
            sx_cm + orbit_r2, sy_cm + orbit_r2,
            outline="#ffff44", width=1, dash=(3, 5)
        )

        omega = math.sqrt(self.game.physics.G_world * total_mass / (separation ** 3))
        G = 6.674e-11
        g_surface_1 = G * real_mass_1 / (real_radius_1 ** 2)
        g_surface_2 = G * real_mass_2 / (real_radius_2 ** 2)
        info = (
            f"{mode_name}  sep={separation:.1f}  "
            f"m1={mass_1:.1f}  m2={mass_2:.1f}  w={omega:.3f}  "
            "[Enter: criar | B/Shift+B: modo | Z/X: separacao]"
        )
        gravity_info = f"g1={g_surface_1:.1f}m/s\u00b2  g2={g_surface_2:.1f}m/s\u00b2"
        text_y = sy_cm - max(orbit_r1, orbit_r2, 16) - 16
        canvas.create_text(
            sx_cm, text_y,
            text=info, fill="white", font=("Consolas", 9)
        )
        canvas.create_text(
            sx_cm, text_y + 14,
            text=gravity_info, fill="white", font=("Consolas", 9)
        )

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
        if self.game.tracked_body == self.game.CENTER_OF_MASS_TARGET:
            lines.append("Tracking: CM")
        elif self.game.tracked_body:
            lines.append(f"Tracking: {self.game.tracked_body.name}")

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

        controls = "Scroll: Zoom | Mid Mouse: Pan | LClick: Lançar | B: Binário | Shift+B: Menor | Z/X: Separação | 2x LClick: Tracking | [/]: Alvo orbital | O/C: Orbitar | P: Pausar"
        canvas.create_text(
            10, cam.height - 10, text=controls, fill="#666666",
            anchor="sw", font=("Consolas", 9), tags="hud",
        )
