import math
import random
import numpy as np
import perlin_noise
import tkinter as tk
import copy

noise = perlin_noise.PerlinNoise(octaves=1, seed=1)


def cleanUp(Target, func: None = None): 
    i = [Target]
    counter = [0]
    result = []
    dirty = True
    Next = 0
    Element = None
    while dirty:
        if Next == 0:
            try:
                Element = i[0][counter[Next]]
            except IndexError:
                dirty = False
                continue
        else:
            try:
                Element = i[Next][counter[Next]]
            except:
                counter.pop(Next)
                i.pop(Next)
                Next -= 1
                continue

        if isinstance(Element,Matrix):
            Element = Element.toList()
            for E in Element:
                if func:
                    result.append(func(E))
                else:
                    result.append(E)
            counter[Next] += 1
        
        
        if isinstance(Element,Vector):
            if func:
                result.append(func(Element.x))
                result.append(func(Element.y))
            else:
                result.append(Element.x)
                result.append(Element.y)
            counter[Next] += 1
        elif isinstance(Element, (list,tuple)):
            counter.append(0)
            counter[Next] += 1
            i.append(Element)

            Next += 1
        else: 
            if func:
                result.append(func(Element))
            else:
                result.append(Element)
            counter[Next] += 1
    return result

class MyMath:
    @staticmethod
    def rand(x: float, mult: float = 1):
        x = np.sin(x) * mult
        i = np.floor(x)
        return abs(x - i)

    @staticmethod
    def mix(a, b, t):
        return a * (1 - t) + b * t

    @staticmethod
    def smoothstep(edge0, edge1, x):
        t = MyMath.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)    


    @staticmethod
    def clamp(x, minimum, maximum):
        return max(minimum, min(x, maximum))

    @staticmethod
    def sigmoid(x):
        return 2 / (1 + math.exp(-x)) -1
        




class PerlinNoise:
    def __init__(self, x,y = 0):
        self.x = x
        self.y = y

        self.ix = np.floor(x)
        self.fx = abs(x - self.ix)

        self.iy = np.floor(y)
        self.fy = abs(y - self.iy)



    def Noise0(self):
        self.z1 = MyMath.rand(self.ix)
        self.z2 = MyMath.rand(self.iy)
        return Vector(self.z1,self.z2).normalize()

    def Noise1(self):
        self.z1 = MyMath.mix(MyMath.rand(self.ix), MyMath.rand(self.ix + 1.0), self.fx)
        self.z2 = MyMath.mix(MyMath.rand(self.iy), MyMath.rand(self.iy + 1.0), self.fy)
        return Vector(self.z1, self.z2).normalize() * math.pi * 2

    def Noise2(self):
        self.z1 = MyMath.mix(MyMath.rand(self.ix), MyMath.rand(self.ix + 1.0), MyMath.smoothstep(0,1,self.fx))
        self.z2 = MyMath.mix(MyMath.rand(self.iy), MyMath.rand(self.iy + 1.0), MyMath.smoothstep(0,1,self.fy))
        return Vector(self.z1, self.z2).normalize() * math.pi * 2

    def True2D_Noise(self, scale = 0.001):
        angle = (noise([self.x*scale,self.y*scale])+1)/2
        angle = angle* 4 * math.pi

        direction = Vector(math.cos(angle),math.sin(angle))
        return direction








class Vector:
    def __init__(self, x, y):
        self.x:float = x
        self.y:float = y

    def __add__(self, other: Vector):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, other:float):
        return Vector(self.x/other, self.y/other)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    __str__ = __repr__



    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2)
        if length != 0:
            x = self.x / length
            y = self.y / length
        if length == 0:
            return Vector(0,0)
        return Vector(x,y)


    def add(self,Guest):
        if isinstance(Guest, Vector):
            return Vector(self.x + Guest.x,self.y + Guest.y)
        if isinstance(Guest,(float,int)):
            return Vector(self.x + Guest,self.y + Guest)

    def sub(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    @staticmethod
    def dist(v1: Vector, v2: Vector):
        return math.sqrt((v2.x - v1.x)**2 + (v2.y - v1.y)**2)

    @staticmethod
    def Random2D():
        angle = random.uniform(0, 360)
        angle_rad = math.radians(angle)
        return Vector(math.cos(angle_rad), math.sin(angle_rad))

    @staticmethod
    def dot(v1:Vector, v2:Vector):
        return v1.x * v2.x + v1.y * v2.y

    @staticmethod
    def angle(x:Vector, y:Vector):
        return math.acos(Vector.dot(x,y)/(x.mag()*y.mag()))

    def mag(self):
        return math.sqrt(self.x*self.x + self.y*self.y)




class Matrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = []

        for i in range(self.rows):
            self.data.append([])
            for j in range(self.cols):
                self.data[i].append(0)

    def __repr__(self):
        return f"{self.data}"

    def randomize(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.data[i][j] = random.random()*2-1
    
    def transpose(self):
        result = Matrix(self.cols,self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[j][i] = self.data[i][j]

        return result
    def add(self,n):
        if isinstance(n,Matrix):
            for i in range(self.rows):
                for j in range(self.cols):
                    self.data[i][j] += n.data[i][j]
        else:
            for i in range(self.rows):
                for j in range(self.cols):
                    self.data[i][j] += n

    @staticmethod
    def Smultiply(m1,m2):
        if not m1.cols == m2.rows:
            raise ValueError(f"Cannot multiply {m1.rows}x{m1.cols} with {m2.rows}x{m2.cols}")
        result = Matrix(m1.rows,m2.cols)
        
        a = m1.data
        b = m2.data
        for i in range(result.rows):
            for j in range(result.cols):
                #Dot product of rows and collumns
                Sum = 0
                for k in range(m1.cols):
                    Sum += a[i][k] * b[k][j] 
                result.data[i][j] = Sum
        return result        

    def multiply(self,n):
            #Scalar Product
        for i in range(self.rows):
            for j in range(self.cols):
                self.data[i][j] *= n

    def Map(self, func):
        for i in range(self.rows):
            for j in range(self.cols):
                self.data[i][j] = func(self.data[i][j])
        

    @staticmethod
    def fromList(List:list):
        List = cleanUp(List)

        result = Matrix(len(List),1)
        for i, El in enumerate(List):
            result.data[i][0] = El
        return result

    def toList(self):
        Lisz = []
        for i in range(self.rows):
                    for j in range(self.cols):
                        Lisz.append(self.data[i][j])
        return Lisz





class NeuralNetwork():
    def __init__(self, nInputs , nOutputs ,nHiddenLayers , *nHiddenNodes, MutChance = 0.01):
        self.MutationChance = MutChance
        self.LearningRate = 0.01
        
        self.Inputs_nodes = nInputs
        self.Outputs_nodes = nOutputs
        self.nHidden_Layers = nHiddenLayers

        for i in nHiddenNodes:
            if isinstance(i, (list,tuple)):
                nHiddenNodes = i
                break
            

        if not self.nHidden_Layers == len(nHiddenNodes):
            raise SyntaxError
        
        self.HiddenLayerNodes = []
        if isinstance(nHiddenNodes, (list, tuple)):
            for i in range(self.nHidden_Layers):
                self.HiddenLayerNodes.append(int(nHiddenNodes[i]))


        #these weights get indexed, the one from input to hidden layer 1 is 0, the next 1 and so forth
        #weights are stored [InputWeights, HiddenWeigths, OutputWeights] where HiddenWheights can be any size(aditional)
        # these are stored with[wheight, bias]
        #bias is a (und,1) matrix and wheights is the wheigths Matrix with the data field where all the weights are in a list
        self.weights = []
        for i in range(self.nHidden_Layers):
            if i == 0:
                weight = Matrix(self.HiddenLayerNodes[i], nInputs)
            else:
                weight = Matrix(self.HiddenLayerNodes[i],self.HiddenLayerNodes[i-1])
            bias = Matrix(self.HiddenLayerNodes[i], 1)
            weight.randomize()
            bias.randomize()
            self.weights.append([weight, bias])
        #and the outputs
        weight = Matrix(self.Outputs_nodes, self.HiddenLayerNodes[-1])
        bias = Matrix(self.Outputs_nodes, 1)
        weight.randomize()
        bias.randomize()
        self.weights.append([weight, bias])


    def feedforward(self,inputs):
        # getting Input and returning an Output, as specified by the nInputs and nOutputs
        #using ∂(weights * Inputs +bias)

        #making a matrix
        if isinstance(inputs, (list,tuple)):
            feed = Matrix.fromList(inputs)
        else:
            return None
        #generating the hidden and output results
        #optional: dont apply the sigmoid function to the output
        for i in self.weights:
            feed = Matrix.Smultiply(i[0],feed)
            feed.add(i[1])
            #if i == len(self.weights)-1:
                #continue
            feed.Map(MyMath.sigmoid)

        return feed.toList()

    def train_backpropogation(self, inputs, Answer):
        pass

    def train_GA(self, NNA:NeuralNetwork, NNB:NeuralNetwork):
        #noch checken ob die NN's überhaupt gleich sind
        if not NNA.Inputs_nodes == NNB.Inputs_nodes:
            return
        elif not NNA.nHidden_Layers == NNB.nHidden_Layers:
            return
        elif not NNA.Outputs_nodes == NNB.Outputs_nodes:
            return
        elif not NNA.HiddenLayerNodes == NNB.HiddenLayerNodes:
            return
        # ich will alle wheights übergeben, ohne deren Positionen zu ändern
        # dann Mutation anwenden: Die Werte um einen kleinen Betrag ändern
        cleanList_A = []
        for i in NNA.weights:
            cleanList_A.append(cleanUp(i[0].data))
            cleanList_A.append(cleanUp(i[1].data))
        cleanList_A = cleanUp(cleanList_A)

        cleanList_B = []
        for i in NNB.weights:
            cleanList_B.append(cleanUp(i[0].data))
            cleanList_B.append(cleanUp(i[1].data))
        cleanList_B = cleanUp(cleanList_B)

        cleanList_S = []
        for i in self.weights:
            cleanList_S.append(cleanUp(i[0].data))
            cleanList_S.append(cleanUp(i[1].data))
        cleanList_S = cleanUp(cleanList_S)

        midpoint = random.randint(0, len(cleanList_A)-1)

        for i in range(len(cleanList_S)):
            if i >= midpoint:
                cleanList_S[i] = cleanList_A[i]
            else:
                cleanList_S[i] = cleanList_B[i]

        # mutations here
        for i,W in enumerate(cleanList_S):
            if random.random()<self.MutationChance:
                cleanList_S[i] += random.uniform(-self.LearningRate, self.LearningRate)

        # ich muss probably cleanList wieder zusammenbauen



        New_Weights = copy.deepcopy(self.weights)
        counter = 0
        #duch alle layer iterieren
        for i in range(len(self.weights)):
            #wheight und bias neu festlegen
            for y in range(2):
                #die x und y coordinaten der einzelnen Matrix Elemente bestimmen
                for j in range(New_Weights[i][y].rows):
                    for k in range(New_Weights[i][y].cols):
                        New_Weights[i][y].data[j][k] =  cleanList_S[counter]
                        counter += 1

        self.weights = copy.deepcopy(New_Weights)



class FlowField:
    def __init__(self, PointCountY,PointCountX,WIDTH,HEIGHT):
        self.PointCountY = PointCountY
        self.PointCountX = PointCountX
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.CreatePoints()
        self.CreateVectors()
        self.combine()
    def CreatePoints(self):
        PointsY = np.linspace(0,self.HEIGHT,self.PointCountY)
        PointsX = np.linspace(0,self.WIDTH,self.PointCountX)

        self.Pointlist = []
        for pointY in PointsY:
            for pointX in PointsX:
               self.Pointlist.append(Vector(pointX,pointY))

    def CreateVectors(self):
        self.VectorList0 = []
        self.VectorList1 = []
        self.VectorList2 = []           
        self.VectorListTrue2D = []

        for point in self.Pointlist:
            self.VectorListTrue2D.append(PerlinNoise(point.x,point.y).True2D_Noise())
            self.VectorList2.append(PerlinNoise(point.x,point.y).Noise2())
            self.VectorList1.append(PerlinNoise(point.x,point.y).Noise1())
            self.VectorList0.append(PerlinNoise(point.x,point.y).Noise0())

    def combine(self):
        self.FlowList0 = []
        self.FlowList1 = []
        self.FlowList2 = []
        self.FlowListTrue2D = []
        

        for i,point in enumerate(self.Pointlist):
            self.FlowListTrue2D.append((point,self.VectorListTrue2D[i]))
            self.FlowList2.append((point,self.VectorList2[i]))
            self.FlowList1.append((point,self.VectorList1[i]))
            self.FlowList0.append((point,self.VectorList0[i]))

        self.Grid_2D = []
        Row = []
        for i, point in enumerate(self.FlowListTrue2D):
            Row.append(point)
            if len(Row) == self.PointCountX:
                self.Grid_2D.append(Row)
                Row = []

    def dynamicFlowField_2D(self, offset):

        self.VectorListTrue2D = []
        for point in self.Pointlist:
            self.VectorListTrue2D.append(PerlinNoise(point.x+offset,point.y+offset).True2D_Noise())

        self.FlowListTrue2D = []
        for i,point in enumerate(self.Pointlist):
                    self.FlowListTrue2D.append((point,self.VectorListTrue2D[i]))


        self.Grid_2D = []
        Row = []
        for i, point in enumerate(self.FlowListTrue2D):
            Row.append(point)
            if len(Row) == self.PointCountX:
                self.Grid_2D.append(Row)
                Row = []





