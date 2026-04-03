import math
import random
from gravity_sim.models.body import CelestialBody


class PhysicsEngine:
    """Motor de física gravitacional com fragmentação."""

    MAX_BODIES = 500          # limite de corpos para performance
    FRAGMENT_COUNT = 6        # fragmentos por colisão/quebra
    SHATTER_THRESHOLD = 3.0   # razão de energia cinética / binding energy para estilhaçar
    DEBRIS_FRACTION = 0.15    # fração de massa ejetada em colisão moderada
    ROCHE_FACTOR = 2.5        # fator de Roche: d < ROCHE * R_big * (M_big/M_small)^(1/3)

    def __init__(self):
        self.G_world = 1.0
        self.dt = 0.016
        self.sub_steps = 8
        self.time_scale = 1.0
        self.AU = 200.0

    def step(self, bodies):
        sub_dt = (self.dt * self.time_scale) / self.sub_steps

        # Separar: corpos principais (gravitam tudo) vs fragmentos (só sentem principais)
        main_bodies = [b for b in bodies if not b.is_fragment]
        fragments = [b for b in bodies if b.is_fragment and not b.fixed]

        for _ in range(self.sub_steps):
            # Corpos principais: interação N²  entre si (poucos)
            for body in main_bodies:
                if body.fixed:
                    continue
                ax, ay = 0.0, 0.0
                for other in main_bodies:
                    if other is body:
                        continue
                    dx = other.x - body.x
                    dy = other.y - body.y
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq)
                    if dist < other.radius:
                        dist = other.radius
                        dist_sq = dist * dist
                    force = self.G_world * other.mass / dist_sq
                    ax += force * dx / dist
                    ay += force * dy / dist
                body.vx += ax * sub_dt
                body.vy += ay * sub_dt
                body.x += body.vx * sub_dt
                body.y += body.vy * sub_dt

            # Fragmentos: só sentem gravidade dos corpos principais (N_frag * N_main)
            for frag in fragments:
                ax, ay = 0.0, 0.0
                for other in main_bodies:
                    dx = other.x - frag.x
                    dy = other.y - frag.y
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq)
                    if dist < other.radius:
                        dist = other.radius
                        dist_sq = dist * dist
                    force = self.G_world * other.mass / dist_sq
                    ax += force * dx / dist
                    ay += force * dy / dist
                frag.vx += ax * sub_dt
                frag.vy += ay * sub_dt
                frag.x += frag.vx * sub_dt
                frag.y += frag.vy * sub_dt

        self._check_collisions(bodies)
        self._check_roche_breakup(bodies)

        for body in bodies:
            if body.fixed:
                continue
            body.trail.append((body.x, body.y))

        return bodies

    def _check_collisions(self, bodies):
        to_remove = set()
        new_bodies = []
        for i, a in enumerate(bodies):
            if i in to_remove:
                continue
            for j, b in enumerate(bodies):
                if j <= i or j in to_remove:
                    continue
                dx = a.x - b.x
                dy = a.y - b.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < a.radius + b.radius:
                    if a.mass >= b.mass:
                        big, small = a, b
                        remove_idx = j
                    else:
                        big, small = b, a
                        remove_idx = i

                    # Energia cinética relativa no referencial do CM
                    rel_vx = a.vx - b.vx
                    rel_vy = a.vy - b.vy
                    rel_speed_sq = rel_vx * rel_vx + rel_vy * rel_vy
                    mu = (a.mass * b.mass) / (a.mass + b.mass)
                    kinetic_energy = 0.5 * mu * rel_speed_sq

                    # Energia de ligação gravitacional (binding)
                    binding_energy = self.G_world * a.mass * b.mass / (a.radius + b.radius)

                    ratio = kinetic_energy / max(binding_energy, 1e-10)

                    if ratio > self.SHATTER_THRESHOLD and not big.fixed:
                        # Colisão destrutiva: merge normal (sem fragmentos)
                        to_remove.add(i)
                        to_remove.add(j)
                        total_mass = a.mass + b.mass
                        cm_x = (a.mass * a.x + b.mass * b.x) / total_mass
                        cm_y = (a.mass * a.y + b.mass * b.y) / total_mass
                        cm_vx = (a.mass * a.vx + b.mass * b.vx) / total_mass
                        cm_vy = (a.mass * a.vy + b.mass * b.vy) / total_mass
                        rem = CelestialBody(
                            name="Remanescente",
                            x=cm_x, y=cm_y,
                            mass=total_mass,
                            radius=(a.radius**3 + b.radius**3) ** (1/3),
                            color=big.color,
                            vx=cm_vx, vy=cm_vy,
                            is_fragment=False,
                        )
                        new_bodies.append(rem)
                        if i in to_remove:
                            break
                    elif ratio > 0.3 and not big.fixed:
                        # Colisão moderada: merge + ejetar detritos
                        to_remove.add(remove_idx)
                        debris_mass = small.mass * self.DEBRIS_FRACTION
                        merge_mass = small.mass - debris_mass

                        total_mass = big.mass + merge_mass
                        if not big.fixed:
                            big.vx = (big.mass * big.vx + merge_mass * small.vx) / total_mass
                            big.vy = (big.mass * big.vy + merge_mass * small.vy) / total_mass
                            big.x = (big.mass * big.x + merge_mass * small.x) / total_mass
                            big.y = (big.mass * big.y + merge_mass * small.y) / total_mass

                        big.mass = total_mass
                        big.radius = (big.radius**3 + (small.radius * (1 - self.DEBRIS_FRACTION)**(1/3))**3) ** (1/3)
                        self._merge_real_props(big, small, 1 - self.DEBRIS_FRACTION)

                        # Ejetar fragmentos
                        if debris_mass > 0.1:
                            impact_speed = math.sqrt(rel_speed_sq)
                            frags = self._create_fragments(
                                small.x, small.y, small.vx, small.vy,
                                debris_mass, small.radius * 0.3, small.color,
                                self.FRAGMENT_COUNT,
                                impact_speed * 0.3
                            )
                            new_bodies.extend(frags)

                        if i in to_remove:
                            break
                    else:
                        # Colisão suave: merge limpo
                        to_remove.add(remove_idx)
                        total_mass = big.mass + small.mass
                        if not big.fixed:
                            big.vx = (big.mass * big.vx + small.mass * small.vx) / total_mass
                            big.vy = (big.mass * big.vy + small.mass * small.vy) / total_mass
                            big.x = (big.mass * big.x + small.mass * small.x) / total_mass
                            big.y = (big.mass * big.y + small.mass * small.y) / total_mass

                        big.mass = total_mass
                        big.radius = (big.radius**3 + small.radius**3) ** (1/3)
                        self._merge_real_props(big, small, 1.0)
                        big.trail.extend(small.trail)

                        if i in to_remove:
                            break

        if to_remove:
            bodies[:] = [b for i, b in enumerate(bodies) if i not in to_remove]

        # Adicionar novos fragmentos (respeitando limite)
        space = self.MAX_BODIES - len(bodies)
        if space > 0 and new_bodies:
            bodies.extend(new_bodies[:space])

    def _merge_real_props(self, big, small, fraction):
        if big.real_mass and small.real_mass:
            big.real_mass += small.real_mass * fraction
        if big.real_radius and small.real_radius:
            big.real_radius = (big.real_radius**3 + (small.real_radius * fraction**(1/3))**3) ** (1/3)

    def _create_fragments(self, cx, cy, cvx, cvy, total_mass, parent_radius,
                          color, count, eject_speed):
        # Fragmentação desabilitada
        return []

    def _check_roche_breakup(self, bodies):
        # Desabilitado: não há mais espedaçamento por gravidade
        pass

    def find_nearest_body(self, bodies, wx, wy):
        best = None
        best_dist = float('inf')
        for body in bodies:
            dx = wx - body.x
            dy = wy - body.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < best_dist and dist > body.radius:
                best_dist = dist
                best = body
        return best, best_dist

    def find_dominant_body(self, bodies, wx, wy):
        """Encontra o corpo com maior influência gravitacional (M/r²) em (wx, wy)."""
        best = None
        best_influence = 0.0
        best_dist = float('inf')
        for body in bodies:
            if body.is_fragment:
                continue
            dx = wx - body.x
            dy = wy - body.y
            dist_sq = dx * dx + dy * dy
            dist = math.sqrt(dist_sq)
            if dist <= body.radius:
                continue
            influence = body.mass / dist_sq
            if influence > best_influence:
                best_influence = influence
                best = body
                best_dist = dist
        return best, best_dist

    def compute_orbit_velocity(self, target, launch_x, launch_y):
        dx = launch_x - target.x
        dy = launch_y - target.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1e-6:
            return 0.0, 0.0

        orbital_speed = math.sqrt(self.G_world * target.mass / dist)
        nx = -dy / dist
        ny = dx / dist

        vx = orbital_speed * nx + target.vx
        vy = orbital_speed * ny + target.vy
        return vx, vy

    def simulate_trajectory(self, bodies, start_x, start_y, vx, vy,
                            launch_radius, max_steps=20000):
        px, py = start_x, start_y
        pvx, pvy = vx, vy
        sim_dt = self.dt * 4
        points = [(px, py)]
        min_dist_check = 50

        sim_bodies = []
        for b in bodies:
            sim_bodies.append({
                'x': b.x, 'y': b.y,
                'vx': b.vx, 'vy': b.vy,
                'mass': b.mass, 'radius': b.radius,
                'fixed': b.fixed,
            })

        departed = False
        for _ in range(max_steps):
            for sb in sim_bodies:
                if sb['fixed']:
                    continue
                sax, say = 0.0, 0.0
                for ob in sim_bodies:
                    if ob is sb:
                        continue
                    dx = ob['x'] - sb['x']
                    dy = ob['y'] - sb['y']
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq)
                    if dist < ob['radius']:
                        dist = ob['radius']
                        dist_sq = dist * dist
                    force = self.G_world * ob['mass'] / dist_sq
                    sax += force * dx / dist
                    say += force * dy / dist
                sb['vx'] += sax * sim_dt
                sb['vy'] += say * sim_dt
            for sb in sim_bodies:
                if sb['fixed']:
                    continue
                sb['x'] += sb['vx'] * sim_dt
                sb['y'] += sb['vy'] * sim_dt

            ax, ay = 0.0, 0.0
            collided = False
            for sb in sim_bodies:
                dx = sb['x'] - px
                dy = sb['y'] - py
                dist_sq = dx * dx + dy * dy
                dist = math.sqrt(dist_sq)
                if dist < sb['radius'] + launch_radius:
                    collided = True
                    break
                if dist < sb['radius']:
                    dist = sb['radius']
                    dist_sq = dist * dist
                force = self.G_world * sb['mass'] / dist_sq
                ax += force * dx / dist
                ay += force * dy / dist
            if collided:
                break
            pvx += ax * sim_dt
            pvy += ay * sim_dt
            px += pvx * sim_dt
            py += pvy * sim_dt
            points.append((px, py))

            dx_start = px - start_x
            dy_start = py - start_y
            dist_start = math.sqrt(dx_start * dx_start + dy_start * dy_start)
            if not departed and dist_start > min_dist_check:
                departed = True
            if departed and dist_start < min_dist_check * 0.5:
                break

        return points
