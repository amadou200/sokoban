# -*- coding: utf-8 -*-

try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox

from sokobanXSBLevels import *
from enum import Enum

"""
Direction :
    Utile pour gérer le calcul des positions pour les mouvements
"""
# class Direction(Enum):
#    Up = 1
#    Down = 2
#    Left = 3
#    Right = 4


class Direction(object):
    def __init__(self, direction):
        self.direction = direction

    def getDir(self):
        return self.direction

    def setDir(self, other):
        print("other", other)
        self.direction = other
        print("nd:", self.direction)


"""
Position :
    - stockage de coordoannées x et y,
    - vérification de x et y par rapport à une matrice
    - calcule de position relative à partir d'un offset (un décalage) et une direction
"""


class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Position(' + str(self.x) + ',' + str(self.y) + str(')')

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    # retoune la position vers la direction #direction en tenant compte de l'offset
    #   Position(3,4).positionTowards(Direction.Right, 2) == Position(5,4)
    # offset = 2 quand on deplace une box voir si mur apres
    def positionTowards(self, direction, offset):
        " a compléter "

    # Retourne True si les coordonnées sont valides dans le wharehouse
    def isValidInWharehouse(self, wharehouse):
        return wharehouse.isPositionValid(self)

    # Convertit le receveur en une position correspondante dans un Canvas
    def asCanvasPositionIn(self, elem):
        lx = self.getX() * elem.getWidth()
        ly = self.getY() * elem.getHeight()
        return Position(lx, ly)


"""
WharehousePlan : Plan de l'entrepot pour stocker les éléments.
    Les éléments sont stockés dans une matrice (#rawMatrix)
"""


class WharehousePlan(object):
    def __init__(self):
        # la matrice d'Elem
        self.rawMatrix = []

    def __str__(self):
        return "lignes : " + str(len(self.rawMatrix))

    def appendRow(self, row):
        self.rawMatrix.append([])

    def appendColumn(self, row, column):
        self.rawMatrix[row].append(None)

    def at(self, position):
        return 0

    def atPut(self, position, elem):
        self.x = position.getX()
        self.y = position.getY()
        self.rawMatrix[self.y][self.x] = elem

    def isPositionValid(self, position):
        self.x = position.getX()
        self.y = position.getY()

        if self.rawMatrix[self.x][self.y] == None:
            print("rien")
            return True
        elif self.rawMatrix[self.x][self.y].xsbChar() == ".":
            print("goal")
            return True
        elif self.rawMatrix[self.x][self.y].xsbChar() == "$":
            print("box")
            return 0
        else:
            print("mur")
            return False
        return False

    def hasFreePlaceAt(self, position):
        return self.at(position).isFreePlace()

    def asXsbMatrix(self):
        return xsbMatrix(self.rawMatrix)


"""
Floor :
    Représente une case vide de la matrice
    (pas de None dans la matrice)
"""


class Floor(object):
    def __init__(self, canvas, position):
        self.x = position.getX()
        self.y = position.getY()
        print(self.x, self.y)
        self.rect_id = canvas.create_rectangle(
            self.x, self.y, self.x+64, self.y+64, fill="gray")

    def isMovable(self):
        return False

    def canBeCovered(self):
        return True

    def xsbChar(self):
        return ' '

    def isFreePlace(self):
        return True


"""
Goal :
    Représente une localisation à recouvrir d'un BOX (objectif du jeu).
    Le déménageur doit parvenir à couvrir toutes ces cellules à partir des caisses.
    Un Goal est static, il est toujours déssiné en dessous :
        Le zOrder est assuré par le tag du create_image (tag='static')
        et self.canvas.tag_raise("movable","static") dans Level
"""


class Goal(object):
    def __init__(self, canvas, position):
        self.image = tk.PhotoImage(file='image/goal.png')
        self.x = position.getX()
        self.y = position.getY()

        canvas.create_image(self.x, self.y, image=self.image,
                            anchor=tk.NW, tags="static")

    def isMovable(self):
        return False

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def canBeCovered(self):
        return True

    def xsbChar(self):
        return '.'

    def isFreePlace(self):
        return False


"""
Wall : pour délimiter les murs
    Le déménageur ne peut pas traverser un mur.
    Un Wall est static, il est toujours déssiné en dessous :
        Le zOrder est assuré par le tag du create_image (tag='static')
        et self.canvas.tag_raise("movable","static") dans Level
"""


class Wall(object):
    def __init__(self, canvas, position):
        self.image = tk.PhotoImage(file='image/wall.png')
        self.x = position.getX()
        self.y = position.getY()

        canvas.create_image(self.x, self.y, image=self.image,
                            anchor=tk.NW, tags="static")

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def isMovable(self):
        return False

    def canBeCovered(self):
        return False

    def xsbChar(self):
        return '#'

    def isFreePlace(self):
        return False


"""
Box : Caisse à déplacer par le déménageur.
    Etant donné qu'une caisse doit être déplacé, le canvas et la matrice sont necessaires pour
    reconstruire l'image et mettre en oeuvre sont déplacement (dans le canvas et dans la matrice)
    Un Box est "movable", il est toujours déssiné au dessus des objets "static" :
        Le zOrder est assuré par le tag du create_image (tag='movable')
        et self.canvas.tag_raise("movable","static") dans Level
    Un Box est représenté differemment (image différente) suivant qu'il se situe sur un emplacement marqué par un Goal ou non.
 """


class Box(object):
    def __init__(self, canvas, wharehouse, position, onGoal):
        self.image = tk.PhotoImage(file='image/box.png')
        self.x = position.getX()
        self.y = position.getY()

        canvas.create_image(self.x, self.y, image=self.image,
                            anchor=tk.NW, tags="movable")

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    def isMovable(self):
        return True

    def canBeCovered(self):
        return False

    def moveTowards(self, direction):
        return 0

    def xsbChar(self):
        # if self.under.isFreePlace(): return '$'
        # else: return '*'
        return '$'

    def isFreePlace(self):
        return False

    def startGoalCoveredAnimation(self):
        return 0

    def cleanUpAnimation(self):
        return 0

    def goalCoveredAnimation(self):
        return 0


"""
Mover : C'est  le déménageur.
    La classe Mover met en oeuvre la logique du jeu dans #canMove et #moveTowards.
    Etant donné qu'un Mover se déplace, le canvas et la matrice sont necessaires pour
    reconstruire l'image et mettre en oeuvre sont déplacement (dans le canvas et dans la matrice)
    Un Mover est "movable", il est toujours déssiné au dessus des objets "static" :
        Le zOrder est assuré par le tag du create_image (tag='movable')
        et self.canvas.tag_raise("movable","static") dans Level
    Un Box est représenté differemment (image différente) suivant la direction de déplacement (même si le dépplacement s'avère impossible).
"""


class Mover(object):
    def __init__(self, canvas, wharehouse, position, onGoal):
        self.image = tk.PhotoImage(file='image/playerDown.png')
        self.x = position.getX()
        self.y = position.getY()
        self.canvas = canvas

        self.playerId = canvas.create_image(
            self.x, self.y, image=self.image, anchor=tk.NW, tags="movable")
        self.playerX = self.x
        self.playerY = self.y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, other):
        self.x = other

    def setY(self, other):
        self.y = other

    def isMoveable(self):
        return True

    def moveInCanvas(self, direction):
        return 0

    """
        Retourne True si le Mover peut se déplacer dans la direction demandée.
        Le calcul necessite de voir l'élément adjacent mais aussi l'élément suivant (offset de 2)
    """

    def canMove(self, direction):
        return 0

    """
        Pour le déplacement, il faut penser à déplacer éventuellemnt le Box et ensuite déplacer le Mover
    """

    def moveTowards(self, direction):
        return 0

    """
        Le Mover est représenté differemment suivant la direction de déplacement
    """

    def setupImageForDirection(self, direction):
        dire = direction.getDir()
        if dire == "Up":
            self.image = tk.PhotoImage(file='image/playerUp.png')
            self.playerId = self.canvas.create_image(
                self.x, self.y, image=self.image, anchor=tk.NW, tags="movable")
        if dire == "Down":
            self.image = tk.PhotoImage(file='image/playerDown.png')
            self.playerId = self.canvas.create_image(
                self.x, self.y, image=self.image, anchor=tk.NW, tags="movable")
        if dire == "Left":
            self.image = tk.PhotoImage(file='image/playerLeft.png')
            self.playerId = self.canvas.create_image(
                self.x, self.y, image=self.image, anchor=tk.NW, tags="movable")
        if dire == "Right":
            self.image = tk.PhotoImage(file='image/playerRight.png')
            self.playerId = self.canvas.create_image(
                self.x, self.y, image=self.image, anchor=tk.NW, tags="movable")

    """
        Pour le déplacement :
            - image changée en fonction de la direction
            - si on ne peut pas se déplacer dans cette direction -> abandon
            - sinon, bin le Mover est déplacé
    """

    def push(self, direction):
        self.setupImageForDirection(direction)
        if not self.canMove(direction):
            self.startImpossiblePushAnimation()
            return
        self.moveTowards(direction)

    def xsbChar(self):
        if self.under.isFreePlace():
            return '@'
        else:
            return '+'

    def isFreePlace(self):
        return False

    def startImpossiblePushAnimation(self):
        return 0

    def cleanUpAnimation(self):
        return 0

    def impossiblePushAnimation(self):
        return 0


"""
    Le jeux avec tout ce qu'il faut pour dessiner et stocker/gérer la matrice d'éléments
    
"""


class Level(object):
    def __init__(self, root, xsbMatrix):
        self.root = root
        self.wharehouse = WharehousePlan()

        # calcul des dimensions de la matrice
        nbrows = len(xsbMatrix)
        nbcolumns = 0

        for line in xsbMatrix:
            nbc = len(line)
            if nbc > nbcolumns:
                nbcolumns = nbc

        self.height = nbrows * 64
        self.width = nbcolumns * 64

        self.canvas = tk.Canvas(
            self.root, width=self.width, height=self.height, bg="gray")
        self.canvas.pack()

        self.initWharehouseFromXsb(xsbMatrix)
        self.root.bind("<Key>", self.keypressed)

    def initWharehouseFromXsb(self, xsbMatrix):

        nbrows = len(xsbMatrix)

        nbcolumns = 0
        for line in xsbMatrix:
            nbc = len(line)
            if nbc > nbcolumns:
                nbcolumns = nbc

        # on a besoin de deux matrices pour pouvoir déplacer les éléments déplacables
        # sans écraser les éléments non déplacables
        self.staticMatrix = []
        self.movableMatrix = []
        for lineIdx in range(nbrows):
            self.staticMatrix.append([])
            self.movableMatrix.append([])
            self.wharehouse.appendRow([])
            for elemIdx in range(nbcolumns):
                self.staticMatrix[lineIdx].append(None)
                self.movableMatrix[lineIdx].append(None)
                self.wharehouse.appendColumn(lineIdx, [])

        # Initialisation des matrices à partir de la matrice Xsb
        y = 0
        for lineIdx in range(len(xsbMatrix)):
            x = 0
            for elemIdx in range(len(xsbMatrix[lineIdx])):
                e = xsbMatrix[lineIdx][elemIdx]
                if e == '#':
                    self.staticMatrix[y][x] = 0
                    self.wharehouse.atPut(Position(x, y), Wall(
                        self.canvas, Position(x*64, y*64)))
                if e == '$':
                    self.staticMatrix[y][x] = 0
                    self.wharehouse.atPut(Position(x, y), Box(
                        self.canvas, WharehousePlan(), Position(x*64, y*64), False))
                if e == '.':
                    self.movableMatrix[y][x] = 0
                    self.wharehouse.atPut(Position(x, y), Goal(
                        self.canvas, Position(x*64, y*64)))
                # if e == ' ' or e == '-':
                 #   self.staticMatrix[y][x] = 0
                  #  self.wharehouse.atPut(Position(x, y), Floor(self.canvas, Position(x*64,y*64)))
                elif e == '@':
                    self.movableMatrix[y][x] = 0
                    self.playerId = Mover(
                        self.canvas, WharehousePlan(), Position(x*64, y*64), False)
                    self.wharehouse.atPut(Position(x, y), self.playerId)
                else:
                    None
                x = x + 1
            y = y + 1
            x = 0

        self.canvas.tag_raise("movable", "static")

    def keypressed(self, event):
        xBefore = int(Mover.getX(self.playerId)/64)
        yBefore = int(Mover.getY(self.playerId)/64)
        xAfter = int(Mover.getX(self.playerId)/64)
        yAfter = int(Mover.getY(self.playerId)/64)

        # adapter les coordonnées du player en fonction du déplacement voulu
        if event.keysym == 'Up':
            yAfter = yAfter-1
            self.direction = Direction("Up")

        elif event.keysym == 'Down':
            yAfter = yAfter+1
            self.direction = Direction("Down")

        elif event.keysym == 'Left':
            xAfter = xAfter-1
            self.direction = Direction("Left")

        else:
            xAfter = xAfter+1
            self.direction = Direction("Right")

        if self.wharehouse.isPositionValid(Position(yAfter, xAfter)) == True:
            # met à jour la position du player
            self.playerId = Mover(self.canvas, WharehousePlan(
            ), Position(xAfter*64, yAfter*64), False)
            # supprimer l'ancienne image dans le canvas
            self.wharehouse.atPut(Position(xBefore, yBefore), None)
            # créer une nouvelle image dans le canvas à la bonne coordonnée
            self.wharehouse.atPut(Position(xAfter, yAfter), self.playerId)

        elif self.wharehouse.isPositionValid(Position(yAfter, xAfter)) == 0:
            print("pousse vers: ", self.direction)
            if self.direction.getDir() == "Up":
                if self.isPositionValid(Position(self.x, self.y-1)) == True:
                    self.atPut(Position(self.x, self.y-1), Box(self.canvas,
                               WharehousePlan(), Position(self.x*64, self.y-1*64), False))
                    return True
            if self.direction.getDir() == "Down":
                if self.isPositionValid(Position(self.x, self.y+1)) == True:
                    self.atPut(Position(self.x, self.y+1), Box(self.canvas,
                               WharehousePlan(), Position(self.x*64, self.y+1*64), False))
                    return True
            if self.direction.getDir() == "Left":
                if self.isPositionValid(Position(self.x-1, self.y)) == True:
                    self.atPut(Position(self.x-1, self.y), Box(self.canvas,
                               WharehousePlan(), Position(self.y*64, self.x*64), False))
                    print("en coord: ",  self.x-1, self.y)
                    return True
            if self.direction.getDir() == "Right":
                if self.isPositionValid(Position(self.x+1, self.y)) == True:
                    self.atPut(Position(self.x+1, self.y), Box(self.canvas,
                               WharehousePlan(), Position(self.x+1*64, self.y*64), False))
                    return True

        else:
            yAfter = yBefore
            xAfter = xBefore


class Sokoban(object):
    '''
    Main Level class
    '''

    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Sokoban")
        print('Sokoban: ' + str(len(SokobanXSBLevels)) + ' levels')
        self.level = Level(self.root, SokobanXSBLevels[1])
        # self.level = Level(self.root, [
        # ['-','-','$','+','$','.','-','.','.','.','.','-','-','.','.','-','-','.','-'] ])
        # self.level = Level(self.root, [ ['@'] ])

    def play(self):
        self.root.mainloop()


Sokoban().play()
