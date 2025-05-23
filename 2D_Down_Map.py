import pygame
import math

pygame.init()
displayRes = [500,500]
center = (displayRes[0]//2,displayRes[1]//2)
clock = pygame.time.Clock()

import numpy as np


#{input Classes
class user_input():
    def __init__(self):
        self.up = pygame.K_w
        self.down = pygame.K_s
        self.left = pygame.K_a
        self.right = pygame.K_d

    def movement(self,vector,location,speed):
        self.keys = pygame.key.get_pressed()

        if self.keys[self.up]:
            vector[1] = -1
        elif self.keys[self.down]:
            vector[1] =  1

        if self.keys[self.left]:
            vector[0] = -1
        elif self.keys[self.right]:
            vector[0] =  1
        
class npc_input():
    def __init__(self):
        self.movement_actions = ["detect","chase"]
        self.tracked_pawns = []
        self.detection_r = 100
        self.found_target = None

    def detect(self,location):
        for i in range (len(self.tracked_pawns)):
            target_location = self.tracked_pawns[i].location
            diff_distance = ((target_location[0] - location[0])**2 + (target_location[1] - location[1])**2) ** 0.5
            
            if diff_distance <= self.detection_r:
                self.found_target = self.tracked_pawns[i]
                #print("found")
            else:
                self.found_target = None
                #print("Cant see")

    def chase(self,vector,location):
        target_location = self.found_target.location
        vector[0] = (target_location[0] - location[0]) 
        vector[1] = (target_location[1] - location[1]) 

    def movement(self,vector,location,speed):
        for i in range (len(self.movement_actions)):
            if self.movement_actions[i] == "detect":
                self.detect(location)

            if self.movement_actions[i] == "chase":
                if self.found_target != None:
                    self.chase(vector,location)
#input Classes}


#{physics Classes
class physics():
    def __init__(self):
        self.collisions_type = None
        self.weight = None
        self.gravity = None
        self.mass = None
        self.acceleration = None

        self.solid_objects = []  # List of objects
        self.collision_point = [0,0] # Center of collisions eithier player or specific area better to use player as generates physics around player

    def normalize_vector(self, vector):
        if vector == [0,0]:
            return [0,0]
        else:
            vx, vy = vector
            vd = (vx**2 + vy**2) ** 0.5
            epsilon = 1e-10  # Smallest possible value to avoid zero division
            if vd < epsilon:
                return [0,0]
            return (vx/vd, vy/vd)
    
    def distance_diff_direct(self, location, target_location):
        return ((location[0] - target_location[0])**2 + (location[1] - target_location[1])**2) ** 0.5

    def distance_diff_length(self, location, target_location):
        return target_location[1] - location[1]

    def vector_move(self, vector, speed):
        norm_speed = delta * speed
        norm_vector = self.normalize_vector(vector)
        movement_vector = (norm_vector[0] * norm_speed, norm_vector[1] * norm_speed)
        return movement_vector

    def collisions(self):
        if self.collisions_type == "center_line":
            self.collisions_center_line()

    def collisions_center_line(self, radius=50):  # Define a radius limit
        filtered_objects = []  # Store objects within radius

        # Filter solid objects to only include those near the collision point
        for obj in self.solid_objects:
            distance = self.distance_diff_direct(self.collision_point, obj.location)
            if distance <= radius:  # Only consider objects within the radius
                filtered_objects.append(obj)

        # Perform collision detection only on nearby objects
        for i in range(len(filtered_objects)):
            obj = filtered_objects[i]
            location = self.collision_point
            hypotenuse = self.distance_diff_direct(location, obj.location)
            adjacent = self.distance_diff_length(location, obj.location)

            # Avoid division by zero
            if hypotenuse > 0:
                angle = math.acos(adjacent / hypotenuse)

            # Check overlap and resolve collision
            for j in range(len(filtered_objects)):
                if i != j:  # Avoid self-check
                    self.resolve_overlap(obj, filtered_objects[j])


    def resolve_overlap(self, obj1, obj2):
        """Pushes objects apart if overlapping based on their radii."""
        distance = self.distance_diff_direct(obj1.location, obj2.location)

        if distance < obj1.radius + obj2.radius:  # Objects overlap
            overlap = (obj1.radius + obj2.radius) - distance
            move_vector = self.normalize_vector((obj2.location[0] - obj1.location[0], obj2.location[1] - obj1.location[1]))

            # Adjust object positions
            obj1.location[0] -= move_vector[0] * (overlap / 2)
            obj1.location[1] -= move_vector[1] * (overlap / 2)
            obj2.location[0] += move_vector[0] * (overlap / 2)
            obj2.location[1] += move_vector[1] * (overlap / 2)
#physics Classes}

#{gamemode class
class gamemode():
    def __init__(self):
        self.physics_class = None
        self.solid_objects = None
        pass

    def controller(self):
        if self.physics_class != None:
            self.physics_class.solid_objects = self.solid_objects
            self.physics_class.collisions()

class gamemode_simple():
    def __init__(self):
        self.gamemode = gamemode()
        self.gamemode.physics_class = physics()
        self.gamemode.physics_class.collisions_type = "center_line"
        self.gamemode.solid_objects = None
#gamemode class}

#{Pawn Classes
class pawn():
    def __init__(self):
        self.movement_speed = 2
        self.location = [0,0]
        self.vector = [0,0]
        self.radius = 10
        self.movement_class = None
        self.physics_class = None

    def controller(self):
        if self.movement_class != None:
            self.movement_class.movement(self.vector,self.location,self.movement_speed)
            movement_vector = self.physics_class.vector_move(self.vector,self.movement_speed)
            self.vector = [0,0]

            self.location[0] += movement_vector[0]
            self.location[1] += movement_vector[1]
            

class player():
    def __init__(self):
        self.player = pawn()
        self.player.movement_speed = 100
        self.player.location = [10,10]
        self.player.movement_class = user_input()
        self.player.physics_class = physics()

class goblin():
    def __init__(self):
        self.goblin = pawn()
        self.goblin.movement_speed = 50
        self.goblin.location = [50,50]
        self.goblin.radius = 5
        self.goblin.movement_class = npc_input()
        self.goblin.physics_class = physics()
        self.goblin.movement_class.tracked_pawns = [player1.player]
#Pawn Classes}



#{Render Classes
class render_viewport():
    def __init__(self):
        self.display = pygame.display.set_mode(displayRes)
        pass

    def render_pawn(self,pawn):
        pygame.draw.circle(self.display,(255,255,255),pawn.location,pawn.radius)
#Render Classes}



import random


# Number of goblins to generate
NUM_GOBLINS = 200

gamemode1 = gamemode_simple()
player1 = player()

# Generate goblins dynamically
goblins = [goblin() for _ in range(NUM_GOBLINS)]

# Add player and goblins to solid objects list
gamemode1.gamemode.solid_objects = [player1.player] + [g.goblin for g in goblins]
gamemode1.gamemode.physics_class.collision_point = player1.player.location

# Assign tracking behavior to each goblin
for g in goblins:
    # Randomize spawn location within displayRes
    g.goblin.location = [
        random.randint(100, 450),  # X position within screen width
        random.randint(100, 450)   # Y position within screen height
    ]

render1 = render_viewport()

# Font for FPS display
pygame.font.init()
font = pygame.font.SysFont("Arial", 18)

clock = pygame.time.Clock()

while True:
    delta = clock.tick(60) / 1000

    render1.display.fill((0,0,0))

    # Update game controllers
    gamemode1.gamemode.controller()
    player1.player.controller()
    for g in goblins:
        g.goblin.controller()

    # Render all pawns
    render1.render_pawn(player1.player)
    for g in goblins:
        render1.render_pawn(g.goblin)

    # Display FPS counter
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    render1.display.blit(fps_text, (10, 10))

    pygame.display.update()
    
    # Quit event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()