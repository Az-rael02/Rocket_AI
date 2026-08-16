import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame
pygame.init()
import math
import random
import time
import sys
import numpy as np
import perlin_noise
import tkinter as tk
import copy

from Rescources import *
#Global Variables





class Obstacle:
    def __init__(self,x,y,w,h):
        self.position = Vector(x,y)
        self.w = w
        self.h = h

    def contains(self, spot):
        return (
            self.position.x <= spot.x <= self.position.x + self.w and
            self.position.y <= spot.y <= self.position.y + self.h
        )







    
#more globies
lifeSpan = 200
PopSize = 50
MutationRate = 0.01
Mode = "Classic"
iThruster = 5
nhiddenNN_Layers = 2
Elites = 2


clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
WIDTH = 1000
HEIGHT = 800
obstacles = [Obstacle(WIDTH/2-(WIDTH/8),HEIGHT/2-25,WIDTH/4,50)]
RocketSpawnPoint = Vector(WIDTH/2,HEIGHT-50)
TargetRadius = 30




class Setup:
    def __init__(self):
        self.Root = tk.Tk()
        self.Root.title("Setup")
        self.Root.geometry("300x150")

        #die Beschreibungen
        self.ModeDescription = tk.Label(self.Root,text="Neural Network, Classic, 5-Thrusters, FlowField")
        self.ModeDescription.pack(side=tk.BOTTOM)

        #von der Population das Eingabefeld
        self.PopFrame = tk.Frame(self.Root)
        self.PopEntry = tk.Entry(self.PopFrame)
        self.PopLabel = tk.Label(self.PopFrame,text="Population Size:")

        self.PopLabel.pack(side=tk.LEFT)
        self.PopEntry.pack(side=tk.RIGHT)
        self.PopEntry.insert(0, "50")

        #Eingabefeld der Mutation
        self.MutFrame = tk.Frame(self.Root)
        self.MutEntry = tk.Entry(self.MutFrame)
        self.MutLabel = tk.Label(self.MutFrame, text="Mutation Rate:")

        self.MutLabel.pack(side=tk.LEFT)
        self.MutEntry.pack(side=tk.RIGHT)
        self.MutEntry.insert(0, "1")

        # wie viele thruster im 5 Thruster Modus existieren sollen: STandard 5
        self.ThrusterSizeFrame = tk.Frame(self.Root)
        self.ThrusterSizeEntry = tk.Entry(self.ThrusterSizeFrame)
        self.ThrusterSizeLabel = tk.Label(self.ThrusterSizeFrame,text="Thruster: ")

        self.ThrusterSizeLabel.pack(side=tk.LEFT)
        self.ThrusterSizeEntry.pack(side=tk.LEFT)
        self.ThrusterSizeEntry.insert(0,"5")

        self.NNFrame = tk.Frame(self.Root)
        self.NNHiddenNodesLabel = tk.Label(self.NNFrame, text="Number of hidden Nodes: ")
        self.NNHiddenNodesEntry = tk.Entry(self.NNFrame)

        self.NNHiddenNodesLabel.pack(side=tk.LEFT)
        self.NNHiddenNodesEntry.pack(side=tk.LEFT)
        self.NNHiddenNodesEntry.insert(0,"6")

        self.ButtoFrame = tk.Frame(self.Root)
        self.ClassicStart = tk.Button(self.ButtoFrame, text="Classic",command= lambda: self.Initialize("Classic"))
        self.ThrusterStart = tk.Button(self.ButtoFrame,text="5-Thrusters", command= lambda:self.Initialize("5-Thrusters"))
        self.NeuralNetworkStart = tk.Button(self.ButtoFrame,text="Neural Network", command= lambda:self.Initialize("Neural Network"))

        self.ButtoFrame.pack()
        self.ClassicStart.pack(side=tk.LEFT)
        self.ThrusterStart.pack(side= tk.LEFT)
        self.NeuralNetworkStart.pack(side=tk.LEFT)

        self.start = False

        self.Root.protocol("WM_DELETE_WINDOW",lambda: self.Initialize("EXIT"))
    def Initialize(self, Exe):
        global PopSize,MutationRate,Mode,iThruster, NhiddenNN, nhiddenNN_NodesL
        if Exe == "EXIT":
            Mode = Exe
            self.Root.destroy()
            pygame.quit()
        else:    
            if not self.start:
                
                self.PopFrame.pack()
                self.MutFrame.pack()


                self.start = True
                match Exe:
                    case "Classic":
                        self.ThrusterStart.pack_forget()
                        self.NeuralNetworkStart.pack_forget()
                        
                    case "5-Thrusters":
                        self.ThrusterSizeFrame.pack()

                        self.ClassicStart.pack_forget()
                        self.NeuralNetworkStart.pack_forget()
                    case "Neural Network":
                        self.ClassicStart.pack_forget()
                        self.ThrusterStart.pack_forget()

                        self.NNFrame.pack()
            else:
                PopSize = int(self.PopEntry.get().strip())
                MutationRate = float(self.MutEntry.get().strip()) /100
                Mode = Exe
                match Exe:
                    case "5-Thrusters":
                        iThruster = int(self.ThrusterSizeEntry.get().strip())
                    case "Neural Network":
                        nhiddenNN_Nodes = int(self.NNHiddenNodesEntry.get().strip())
                        nhiddenNN_NodesL = []
                        for i in range(nhiddenNN_Layers):
                            nhiddenNN_NodesL.append(nhiddenNN_Nodes)

                self.Root.destroy()
        
























class Rocket:
    def __init__(self, x, y, dna: DNA, Mode):
        self.fitness = 0
        self.position = Vector(x,y)
        self.previousPosition = Vector(x, y)
        self.velocity = Vector(0,0)
        self.acceleration = Vector(0,0)
        self.dna = dna
        self.geneCounter = 0
        self.finishCounter = 0
        self.hitObstacle = False
        self.recordDistance = 100000
        self.recordPosition = Vector(100000,100000)
        self.hittarget = False
        self.NormFitness = 0
        self.Mode = Mode
        match self.Mode:
            case "Classic":
                pass
            case "5-Thrusters":
                self.SeqCounter = 0
                self.ThruCounter = 0


    def calculateFitness(self,target: Vector):
        distance = self.recordDistance
        if distance != 0:
            self.fitness = (1/ distance) * (1/self.finishCounter)
        else:
            self.fitness = 10
        self.fitness = math.pow(self.fitness,2)
        if self.hitObstacle:
            self.fitness *= 0.1
        if self.hittarget:
            self.fitness *=  2

        
    def checkTarget(self, target):
        distance = Vector.dist(self.position, target.position)
        if distance < self.recordDistance:
            self.recordDistance = distance
            self.recordPosition = Vector(self.position.x,self.position.y)
            Direction = (target.position-self.recordPosition).normalize()      
            step = 0
            stepSize = np.linspace(0,distance, 40)
            #for i in range(40):
            #    for obstacle in obstacles:
            #        if obstacle.contains(self.recordPosition +Direction*step):
            #            self.recordDistance += 200
            #            return
            #    step = stepSize[i]
                
        if target.contains(self.position):
            self.hittarget = True
            self.recordDistance = 0



    def crossover(self, Partner):
        child = DNA(self.Mode)


        match self.Mode:
            case "Classic":
                midpoint = random.randint(0,lifeSpan)
                for i in range(lifeSpan):

                    if i > midpoint: 
                        child.genes[i] = self.dna.genes[i]
                    else:
                        child.genes[i] = Partner.dna.genes[i]
                return child
            case "5-Thrusters":
                for i in range(iThruster):
                    Coinflip = random.random()
                    if Coinflip > 0.5:
                        child.genes[i] = self.dna.genes[i]
                    else:
                        child.genes[i] = Partner.dna.genes[i]
                return child
            case "Neural Network":
                child.genes.train_GA(self.dna.genes, Partner.dna.genes, )
                return child


    def checkObstacles(self, obstacles):
        for obstacle in obstacles:
            if obstacle.contains(self.position):
                self.hitObstacle = True
                break



    def ApplyForce(self,force: Vector):
        self.acceleration = self.acceleration.add(force)

    def update(self):
        self.previousPosition = Vector(self.position.x, self.position.y)
        self.velocity = self.velocity.add(self.acceleration)
        if 15 < math.sqrt(self.velocity.x**2 + self.velocity.y**2):
            self.velocity = self.velocity.normalize() * 15
        self.position = self.position.add(self.velocity)
        self.acceleration.x = 0
        self.acceleration.y = 0

    def Run(self,target):
        if not self.hittarget:
            self.finishCounter += 1
        if not self.hitObstacle and not self.hittarget:
            match self.Mode:
                case "Classic":
                    if self.geneCounter < len(self.dna.genes):
                        self.ApplyForce(self.dna.genes[self.geneCounter])
                case "5-Thrusters":
                    for gene in self.dna.genes:
                        if gene["BurnPoint"] < self.geneCounter:
                            if gene["Moment"] == self.SeqCounter:
                                self.ApplyForce(gene["Acceleration"])
                                if self.ThruCounter >= gene["Duration"]:
                                    self.SeqCounter += 1
                                    self.ThruCounter = 0
                                self.ThruCounter += 1
                case "Neural Network":
                    # Inputs ist der angle zum Target und distance, die eingestellten obstacles(distance and angle)
                    inputs = []
                    inputs.append(Vector.dist(self.position,target.position)/WIDTH)
                    inputs.append(Vector.dot(self.velocity, target.position-self.position)/WIDTH)

                    newTarget = target.position + Vector(target.w/2,target.h/2)

                    target_direction = newTarget - self.position
                    inputs.append(target_direction.x/WIDTH)
                    inputs.append(target_direction.y/HEIGHT)

                    for obstacle in obstacles:
                        inputs.append(Vector.dist(self.position,obstacle.position)/WIDTH)
                        inputs.append(Vector.dot(self.velocity, obstacle.position-self.position)/WIDTH)

                        obstacle_direction = obstacle.position - self.position
                        inputs.append(obstacle_direction.x/WIDTH)
                        inputs.append(obstacle_direction.y/HEIGHT)

                    

                    NormVelocity = self.velocity.normalize()
                    inputs.append(NormVelocity.x)
                    inputs.append(NormVelocity.y)

                    inputs.append(self.velocity.mag()/15)

                    outputs = self.dna.genes.feedforward(inputs)
                    self.ApplyForce(Vector(outputs[0], outputs[1])* self.dna.maxForce)
            self.geneCounter += 1
            self.update()
            self.checkObstacles(obstacles)
            self.checkTarget(target)
        else:
            return






class DNA:
    def __init__(self, Mode):
        self.genes = []
        self.Mode = Mode
        self.maxForce = 0.6
        self.maxForce2 = 1.5
        self.minForce = 0.1
        match self.Mode:
            case "Classic":
                for i in range(lifeSpan):
                    self.genes.append(Vector.Random2D() * self.maxForce)
            case "5-Thrusters":
                for i in range(5):
                    Strength = random.uniform(self.minForce,self.maxForce2)
                    if len(self.genes) == 0:
                        MinBurnPoint = 0
                        MaxBurnPoint = 1
                    else:
                        MinBurnPoint = int(self.genes[-1]["BurnPoint"] + self.genes[-1]["Duration"])
                        MaxBurnPoint = int(MinBurnPoint + lifeSpan/(iThruster*2))
                    self.genes.append({"Duration": random.randint(0,int(lifeSpan/iThruster)), "Acceleration": Vector.Random2D() * Strength, "Moment": i, "BurnPoint": random.randint(MinBurnPoint, MaxBurnPoint)})
            case "Neural Network":
                self.genes = NeuralNetwork(7+len(obstacles)*4,2,nhiddenNN_Layers,nhiddenNN_NodesL, MutChance=MutationRate)



        
# I will probably make a own neral network class
#Inputs: Distance to target, angle to target, distance and angle to obstacles

#Outputs will be two, one for horizontal and one for vertical movement






class Population:
    def __init__(self, mutation, length, Mode):
        
        self.mutationrate = mutation
        self.population = []
        self.generations = 0
        self.Mode = Mode


        for _ in range(length):
            self.population.append(Rocket(RocketSpawnPoint.x, RocketSpawnPoint.y, DNA(self.Mode),self.Mode))

    def fitness(self, target):
        for Rakete in self.population:
            Rakete.calculateFitness(target)
    def selection(self):
        totalFitness = 0
        for rocket in self.population:
            totalFitness += rocket.fitness
        for rocket in self.population:
            rocket.NormFitness = rocket.fitness / totalFitness

    def reproduction(self):
        newPopulation = []
        for i in range(len(self.population)-Elites):
            parentA = self.weightedSelection()
            parentB = self.weightedSelection()
            child = parentA.crossover(parentB)
            self.Mutation(child)
            newPopulation.append(Rocket(RocketSpawnPoint.x, RocketSpawnPoint.y, child, self.Mode))

        #the elites
        best = sorted(self.population,key=lambda rocket: rocket.fitness,reverse=True)[:Elites]
        
        
        #best = [self.population[0],self.population[1]]
        #for rakete in self.population:
        #    for i,Brocket in enumerate(best):
        #        if rakete.fitness > Brocket.fitness:
        #            best[i] = rakete
        for bes in best:
            newPopulation.append(copy.deepcopy(bes))
        self.population = newPopulation

    def Mutation(self,child):
        match self.Mode:
            case "Classic":
                for i, gene in enumerate(child.genes):
                    if random.random() < self.mutationrate:
                        child.genes[i] = Vector.Random2D() * child.maxForce
            case "5-Thrusters":
                for i, gene in enumerate(child.genes):
                    if random.random() < self.mutationrate:
                        Atribute = random.randint(0,2)
                        if Atribute == 0:
                            child.genes[i] = {"Duration": random.randint(0,int(lifeSpan/iThruster)), "Acceleration": gene["Acceleration"], "Moment": i, "BurnPoint": gene["BurnPoint"]}    
                        if Atribute == 1:
                            Strength = random.uniform(child.minForce,child.maxForce2)
                            child.genes[i] = {"Duration": gene["Duration"], "Acceleration": Vector.Random2D() * Strength, "Moment": i, "BurnPoint": gene["BurnPoint"]}
                        if Atribute == 2:
                            if child.genes[i]["Moment"] == 0:
                                MinBurnPoint = 0
                                MaxBurnPoint = 1
                            else:
                                MinBurnPoint = int(child.genes[i-1]["BurnPoint"] + child.genes[i-1]["Duration"])
                                MaxBurnPoint = int(MinBurnPoint + lifeSpan/(iThruster*2))
                            
                            child.genes[i] = {"Duration": gene["Duration"], "Acceleration": gene["Acceleration"], "Moment": i, "BurnPoint": random.randint(MinBurnPoint, MaxBurnPoint)}
            case "Neural Network":
                pass




    
    def weightedSelection(self):
        index = 0
        start = random.random()
        while start > 0:
            start -= self.population[index].NormFitness
            index += 1
        index -= 1
        return self.population[index]

    def live(self, target):
        for rocket in self.population:
            rocket.Run(target)




def draw(population:Population, screen,target, Generation):
    Paused = True
    bestdistance = 10000#
    recordTime = lifeSpan
    while True:
        lifecounter = 0
        while lifecounter<lifeSpan:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if Paused:
                            Paused = False
                        else:
                            Paused = True
                                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        target.position.x = mouse_pos[0]
                        target.position.y = mouse_pos[1]
                    if event.button == 3:
                        if Mode == "Neural Network":
                            continue
                        Exit = False
                        mouse_pos = pygame.mouse.get_pos()
                        Obstaclexy = Vector(mouse_pos[0],mouse_pos[1])
                        for obstacle in obstacles:
                            if obstacle.contains(Obstaclexy):
                                obstacles.remove(obstacle)
                                Exit = True
                        while not Exit:
                            clock.tick(60)
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    sys.exit()
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    newMousePos = pygame.mouse.get_pos()
                                    Obstaclexy2 = Vector(newMousePos[0],newMousePos[1])
                                    if Obstaclexy.x > Obstaclexy2.x:
                                        Obstaclexy2.x = Obstaclexy.x
                                        Obstaclexy.x = newMousePos[0]
                                    if Obstaclexy.y > Obstaclexy2.y:
                                        Obstaclexy2.y = Obstaclexy.y
                                        Obstaclexy.y = newMousePos[1]
                                    Exit = True
                                    obstacles.append(Obstacle(Obstaclexy.x,Obstaclexy.y,Obstaclexy2.x-Obstaclexy.x,Obstaclexy2.y-Obstaclexy.y))
            
            if not Paused:   
                population.live(target)
                lifecounter += 1

            fuel_text = font.render(f"Frames left: {lifeSpan-lifecounter}/{lifeSpan}",False,(255,255,255))
            GenerationText = font.render(f"Generation: {Generation}",False,(255,255,255))
            
            for rocket in population.population:
                if rocket.recordDistance < bestdistance:
                    bestdistance = rocket.recordDistance 
                if rocket.finishCounter < recordTime and rocket.hittarget:
                    recordTime = rocket.finishCounter
            bestdistTExt = font.render(f"Record Distance: {round(bestdistance, 2)}",False,(255,255,255))
            bestTimeText = font.render(f"Fastest Time: {recordTime}", False,(255,255,255))

            screen.fill((0, 0, 0))

            for rocket in population.population:
                draw_triangle(screen,rocket.position, velocity=rocket.velocity)

            pygame.draw.circle(screen,(255, 0, 0), (target.position.x+target.w/2, target.position.y+target.h/2),target.w/2)
            pygame.draw.circle(screen,(255,0,0),(RocketSpawnPoint.x,RocketSpawnPoint.y),10)

            for obstacle in obstacles:
                pygame.draw.rect(screen,(100,100,55),[obstacle.position.x,obstacle.position.y,obstacle.w,obstacle.h])

            screen.blit(fuel_text, (10, 10))
            screen.blit(GenerationText,(10,30))
            screen.blit(bestdistTExt,(10,50))
            screen.blit(bestTimeText,(10,70))
            clock.tick(60)
            pygame.display.flip()
        population.fitness(target)
        population.selection()
        population.reproduction()
        Generation += 1



def draw_triangle(screen, position, velocity = Vector(0,0), direction = None, size = 20):
    if velocity.x == 0 and velocity.y == 0 and not direction:
        return
    if direction == None:
        direction = velocity.normalize()
    side = Vector(-direction.y, direction.x)


    tip = position.add(direction * size)
    back = position.sub(direction * size * 0.6)
    left = back.add( side * size * 0.5)
    right = back.sub( side * size * 0.5)

    points = [(tip.x, tip.y), (left.x, left.y), (right.x, right.y)]
    pygame.draw.polygon(screen, (0, 255, 0), points)



def ObstacleDrawPhase(screen, target):
    running = True
    while running:
            for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    running = False
                                                
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 1:
                                    mouse_pos = pygame.mouse.get_pos()
                                    target.position.x = mouse_pos[0]
                                    target.position.y = mouse_pos[1]
                                if event.button == 3:
                                    Exit = False
                                    mouse_pos = pygame.mouse.get_pos()
                                    Obstaclexy = Vector(mouse_pos[0],mouse_pos[1])
                                    for obstacle in obstacles:
                                        if obstacle.contains(Obstaclexy):
                                            obstacles.remove(obstacle)
                                            Exit = True
                                    while not Exit:
                                        clock.tick(60)
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                sys.exit()
                                            if event.type == pygame.MOUSEBUTTONDOWN:
                                                newMousePos = pygame.mouse.get_pos()
                                                Obstaclexy2 = Vector(newMousePos[0],newMousePos[1])
                                                if Obstaclexy.x > Obstaclexy2.x:
                                                    Obstaclexy2.x = Obstaclexy.x
                                                    Obstaclexy.x = newMousePos[0]
                                                if Obstaclexy.y > Obstaclexy2.y:
                                                    Obstaclexy2.y = Obstaclexy.y
                                                    Obstaclexy.y = newMousePos[1]
                                                Exit = True
                                                obstacles.append(Obstacle(Obstaclexy.x,Obstaclexy.y,Obstaclexy2.x-Obstaclexy.x,Obstaclexy2.y-Obstaclexy.y))
            screen.fill((0, 0, 0))
            pygame.draw.circle(screen,(255, 0, 0), (target.position.x+target.w/2, target.position.y+target.h/2),target.w/2)
            pygame.draw.circle(screen,(255,0,0),(RocketSpawnPoint.x,RocketSpawnPoint.y),10)
            
            for obstacle in obstacles:
                pygame.draw.rect(screen,(100,100,55),[obstacle.position.x,obstacle.position.y,obstacle.w,obstacle.h])
            pygame.display.flip()












if __name__ == "__main__": 
    # we want different modes in which this is used. 
    setup = Setup()
    setup.Root.wait_window()
    notlikely = True
    if Mode == "EXIT":
        sys.exit()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    target = Obstacle(WIDTH/2-TargetRadius, 40, TargetRadius*2,60)
    ObstacleDrawPhase(screen,target)
    
    population = Population(MutationRate,PopSize, Mode)
    
    
    time.sleep(1)
    Generation = 1
    draw(population,screen,target,Generation)
        






"funny thing"
#dna = DNA(Mode)
#Rakete = Rocket(1,1,1,dna,Mode)
#Rakete.dna.genes.weights[1][0].data[0][0]
#thats the way of an other object to access one weight of the Neural Network of the rocket