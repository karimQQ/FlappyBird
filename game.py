import random
import math
import pygame

pygame.init()
window = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont("times new roman", 15)

speed = 150
obstaclesDistance = 300


class Bird:
    def __init__(self):
        self.x = 200
        self.y = 200
        self.speed = 0
        self.is_dead = False
        self.score = 0

        self.gravity = 1500
        self.jumpSpeed = 450
        self.radius = 20

    def draw(self):
        pygame.draw.circle(window, (255, 230, 0), (self.x, self.y), self.radius)
        window.blit(font.render("Score: " + str(math.floor(self.score)), True, (0, 0, 0)), (300, 20))

    def is_jumping(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
        return False

    def update(self, deltaTime, events):
        if not self.is_dead and self.is_jumping(events):
            self.speed = -self.jumpSpeed
        self.y += self.speed * deltaTime
        if self.y >= window.get_height():
            self.y = window.get_height()
            self.speed = 0
            self.is_dead = True
        if self.y <= 0:
            self.y = 0
            self.speed = 0
        self.speed += self.gravity * deltaTime
        if self.is_dead:
            self.x -= speed * deltaTime
        else:
            self.score += speed * deltaTime


def is_point_in_rectangle(x1, y1, x2, y2, x, y):
    return x1 <= x <= x2 and y1 <= y <= y2


def is_point_in_circle(x1, y1, radius, x, y):
    return (x1 - x) ** 2 + (y1 - y) ** 2 <= radius ** 2


class Obstacle:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(50, 280)

        self.height = 150
        self.width = 100

    def draw(self):
        pygame.draw.rect(window, (115, 121, 45), (self.x, 0, self.width, self.y))
        pygame.draw.rect(window, (115, 121, 45),
                         (self.x, self.y + self.height, self.width, window.get_height() - self.y - self.height))

    def update(self, deltaTime):
        self.x -= speed * deltaTime

    def is_intersects(self, x, y, radius):
        if is_point_in_rectangle(self.x - radius, 0, self.x + self.width + radius, self.y, x, y):
            return True
        if is_point_in_rectangle(self.x, 0, self.x + self.width, self.y + radius, x, y):
            return True
        if is_point_in_rectangle(self.x - radius, self.y + self.height, self.x + self.width + radius,
                                 window.get_height(), x, y):
            return True
        if is_point_in_rectangle(self.x, self.y + self.height - radius, self.x + self.width, window.get_height(), x, y):
            return True
        if is_point_in_circle(self.x, self.y, radius, x, y):
            return True
        if is_point_in_circle(self.x + self.width, self.y, radius, x, y):
            return True
        if is_point_in_circle(self.x, self.y + self.height, radius, x, y):
            return True
        if is_point_in_circle(self.x + self.width, self.y + self.height, radius, x, y):
            return True
        return False


bird = Bird()
obstacles: list[Obstacle] = [Obstacle(500)]


def update(deltaTime):
    global bird, obstacles
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    while len(obstacles) != 0 and obstacles[0].x + obstacles[0].width < 0:
        obstacles.pop(0)
    while len(obstacles) < 5:
        obstacles.append(Obstacle(obstacles[-1].x + obstaclesDistance))
    for obstacle in obstacles:
        obstacle.update(deltaTime)
    bird.update(deltaTime, events)
    for obstacle in obstacles:
        if obstacle.is_intersects(bird.x, bird.y, bird.radius):
            bird.is_dead = True
    for obstacle in obstacles:
        obstacle.draw()
    bird.draw()

    if bird.is_dead:
        bird = Bird()
        obstacles = [Obstacle(500)]


def main():
    lastTime = pygame.time.get_ticks()
    while True:
        deltaTime = (pygame.time.get_ticks() - lastTime) / 1000
        lastTime = pygame.time.get_ticks()
        pygame.draw.rect(window, (0, 187, 243), (0, 0, window.get_width(), window.get_height()))
        update(deltaTime)
        pygame.display.update()
        clock.tick(120)


main()
