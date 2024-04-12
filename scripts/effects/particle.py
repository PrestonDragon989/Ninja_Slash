class Particle:
    def __init__(self, game, p_type, pos, velocity=(0, 0), frame=0, change_length=False):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = velocity
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame
        self.animation.img_duration = self.animation.img_duration if not change_length else change_length

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))