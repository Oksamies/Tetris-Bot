from engine.game_object import GameObject, Vector2
from ..constants import RenderLayers, PLAY_AREA


class Level(GameObject):

    def init(self):
        self.free_space = set()
        for x in range(PLAY_AREA[0]):
            for y in range(PLAY_AREA[1]):
                self.free_space.add(Vector2(x, y))
        self.head = self.create_snake_head()
        self.cherry = self.create_cherry()

    def on_cherry_eaten(self):
        self.cherry = self.create_cherry()

    def cherry_position_lottery(self):
        import random
        return random.choice(list(self.free_space))

    def create_cherry(self):
        return GameObject.instantiate(
            self.game_interface,
            Cherry,
            level=self,
            position=self.cherry_position_lottery()
        )

    def create_snake_head(self):
        return GameObject.instantiate(
            self.game_interface,
            SnakeHead,
            level=self
        )

    def occupy_space(self, position):
        if position in self.free_space:
            self.free_space.remove(position)

    def unoccupy_space(self, position):
        if position not in self.free_space:
            self.free_space.add(position)


class SnakeHead(GameObject):

    def init(self, level):
        self.level = level
        self.position = Vector2(0, 0)
        self.direction = Vector2(1, 0)
        self.length = 3

    def load_content(self, content_loader):
        self.tile_texture = content_loader.load_texture("piece-blue.png")

    def get_render_layer(self):
        return RenderLayers.SNAKE

    def render(self, screen):
        draw_pos = self.position * (
            self.tile_texture.get_width(),
            self.tile_texture.get_height()
        )
        screen.blit(self.tile_texture, draw_pos)

    def update_input(self, controller):
        self.direction = controller.get_direction()

    def on_cherry_eaten(self):
        self.level.cherry.on_being_eaten()
        self.length += 1
        # TODO: Reward AI?

    def on_collision(self):
        # TODO: Die
        pass

    def update(self):
        self.level.unoccupy_space(self.position)
        old_pos = self.position.clone()
        self.position += self.direction

        if self.position not in self.level.free_space:
            self.on_collision()

        self.level.occupy_space(self.position)

        if self.position == self.level.cherry.position:
            self.on_cherry_eaten()

        GameObject.instantiate(
            self.game_interface,
            SnakePiece,
            level=self.level,
            position=old_pos,
            head=self
        )

        if self.position.x >= PLAY_AREA[0]:
            self.position.x = 0
        if self.position.y >= PLAY_AREA[1]:
            self.position.y = 0


class SnakePiece(GameObject):

    def init(self, level, position, head):
        self.level = level
        self.position = position
        self.head = head
        self.age = 0
        self.level.occupy_space(self.position)

    def load_content(self, content_loader):
        self.tile_texture = content_loader.load_texture("piece-blue.png")

    def get_render_layer(self):
        return RenderLayers.SNAKE

    def render(self, screen):
        draw_pos = self.position * (
            self.tile_texture.get_width(),
            self.tile_texture.get_height()
        )
        screen.blit(self.tile_texture, draw_pos)

    def update(self):
        self.age += 1
        if self.head.length - self.age <= 0:
            self.level.unoccupy_space(self.position)
            GameObject.destroy(self)


class Cherry(GameObject):

    def init(self, level, position):
        self.level = level
        self.position = position

    def load_content(self, content_loader):
        self.tile_texture = content_loader.load_texture("piece-purple.png")

    def get_render_layer(self):
        return RenderLayers.SNAKE

    def on_being_eaten(self):
        self.level.on_cherry_eaten()
        GameObject.destroy(self)

    def render(self, screen):
        draw_pos = self.position * (
            self.tile_texture.get_width(),
            self.tile_texture.get_height()
        )
        screen.blit(self.tile_texture, draw_pos)
