import math
import random
import pygame
import nn
import torch

pygame.init()
window = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont("times new roman", 15)
device = torch.device('cpu')

speed = 150
obstaclesDistance = 300


class Bird:
    def __init__(self):
        self.x = 200
        self.y = 200
        self.speed = 0
        self.is_dead = False
        self.score = 0
        self.model = nn.Model().to(dtype=torch.float32, device=device)
        self.parent = False

        self.gravity = 1500
        self.jumpSpeed = 450
        self.radius = 20

    def draw(self):
        if self.parent:
            pygame.draw.circle(window, (255, 0, 0), (self.x, self.y), self.radius)
        elif self.is_dead:
            pygame.draw.circle(window, (200, 150, 0), (self.x, self.y), self.radius)
        else:
            pygame.draw.circle(window, (255, 230, 0), (self.x, self.y), self.radius)
        pygame.draw.circle(window, (0, 0, 0), (self.x, self.y), self.radius, 1)

    def is_jumping(self):
        i = 0
        while obstacles[i].x + obstacles[i].width + self.radius <= self.x:
            i += 1
        data = [self.y, self.speed, obstacles[i].x - self.x, obstacles[i].y, obstacles[i + 1].x - self.x,
                          obstacles[i + 1].y]
        return self.model.forward(
            torch.Tensor(data).to(
                dtype=torch.float32, device=device)) > 0

    def update(self, deltaTime):
        if not self.is_dead and self.is_jumping():
            self.speed = -self.jumpSpeed
        self.y += self.speed * deltaTime
        if self.y >= window.get_height():
            self.y = window.get_height()
            self.speed = 0
            self.is_dead = True
        if self.y <= 0:
            self.y = 0
            self.speed = 0
            self.is_dead = True
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
        self.y = random.randint(0, 330)
        # self.y = random.randint(0, 1) * 230 + 50

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


def mutateState(state: dict[str, torch.Tensor]):
    for tensor in state.values():
        shape = tensor.shape
        sz = 1
        for j in shape:
            sz *= j
        tensor = tensor.reshape(sz)
        for i in range(sz):
            if random.random() < mutationProbability:
                tensor[i] *= 1 + random.random() * mutationScale * 2 - mutationScale
                # tensor[i] += random.random() * mutationScale * 2 - mutationScale
        tensor = tensor.reshape(shape)
    return state


birdsCount = 20
mutationProbability = 0.02
mutationScale = 0.1

birds: list[Bird] = [Bird() for _ in range(birdsCount)]
obstacles: list[Obstacle] = [Obstacle(500)]

gen = 1
maxScore = 0


def update(deltaTime):
    global birds, obstacles, gen, maxScore, mutationScale
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            mx = 0
            for i in range(birdsCount):
                if birds[i].score > birds[mx].score:
                    mx = i
            torch.save(birds[mx].model.state_dict(), 'last.pt')
            exit(0)
    while len(obstacles) != 0 and obstacles[0].x + obstacles[0].width < 0:
        obstacles.pop(0)
    while len(obstacles) < 5:
        obstacles.append(Obstacle(obstacles[-1].x + obstaclesDistance))
    for obstacle in obstacles:
        obstacle.update(deltaTime)
    for bird in birds:
        bird.update(deltaTime)
    for obstacle in obstacles:
        for bird in birds:
            if obstacle.is_intersects(bird.x, bird.y, bird.radius):
                bird.is_dead = True
    for obstacle in obstacles:
        obstacle.draw()
    for bird in birds:
        bird.draw()
    window.blit(font.render("Поколение: " + str(gen), True, (0, 0, 0)), (20, 20))
    window.blit(font.render("Максимальный счет: " + str(math.floor(maxScore)), True, (0, 0, 0)), (20, 50))
    mx = 0
    for i in range(birdsCount):
        if birds[i].score > birds[mx].score:
            mx = i
    window.blit(font.render("Текущий счет: " + str(math.floor(birds[mx].score)), True, (0, 0, 0)), (20, 80))

    gameEnded = True
    for bird in birds:
        if not bird.is_dead:
            gameEnded = False
    if gameEnded:
        model = birds[mx].model
        if birds[mx].score > maxScore:
            maxScore = birds[mx].score
            torch.save(model.state_dict(), 'noname.pt')
        birds = [Bird() for _ in range(birdsCount)]
        birds[0].model.load_state_dict(model.state_dict())
        birds[0].parent = True
        for i in range(1, birdsCount):
            birds[i].model.load_state_dict(mutateState(model.state_dict()))
        obstacles = [Obstacle(500)]
        gen += 1


def main():
    startState = torch.load("noname.pt")
    for bird in birds:
        bird.model.load_state_dict(startState)
    lastTime = pygame.time.get_ticks()
    while True:
        deltaTime = (pygame.time.get_ticks() - lastTime) / 1000
        lastTime = pygame.time.get_ticks()
        pygame.draw.rect(window, (0, 187, 243), (0, 0, window.get_width(), window.get_height()))
        update(deltaTime)
        pygame.display.update()
        clock.tick(120)


main()
