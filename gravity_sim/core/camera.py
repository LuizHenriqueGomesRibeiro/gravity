class Camera:
    """Câmera 2D com pan e zoom."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

    def world_to_screen(self, wx, wy):
        sx = self.width / 2 + (wx - self.x) * self.zoom
        sy = self.height / 2 - (wy - self.y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = self.x + (sx - self.width / 2) / self.zoom
        wy = self.y - (sy - self.height / 2) / self.zoom
        return wx, wy

    def apply_scroll(self, event_x, event_y, zoom_in):
        mx, my = self.screen_to_world(event_x, event_y)
        factor = 1.15
        if zoom_in:
            self.zoom *= factor
        else:
            self.zoom /= factor
        self.zoom = max(0.001, min(100.0, self.zoom))
        self.x = mx - (event_x - self.width / 2) / self.zoom
        self.y = my + (event_y - self.height / 2) / self.zoom

    def apply_pan(self, dx_screen, dy_screen):
        self.x -= dx_screen / self.zoom
        self.y += dy_screen / self.zoom

    def resize(self, width, height):
        self.width = width
        self.height = height
