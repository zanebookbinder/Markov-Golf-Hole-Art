import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import os
import random

POSSIBLE_SQUARE_TYPES = [
	'F', # Fairway
	'R', # Rough
	'W', # Water
	'S', # Sand
	'G', # Green
	'A', # Tee box
	'W' # Woods
]
POSSIBLE_SQUARE_TYPES_FULL_NAMES = [
	'Fairway', 'Rough', 'Water', 'Sand', 'Green', 'Tee Box', 'Woods'
]
SQUARE_TO_NUMBER = {
	'F': 0,
	'R': 1,
	'W': 2,
	'S': 3,
	'G': 4,
	'A': 5,
	'W': 6
}
SQUARE_HEX_COLORS = ['#1cb314', '#277523', '#247ec7', '#e3bf54', '#b3e8b0', '#ecf2eb', '#12380c']
TRANSITION_MATRIX = {
	'FFF': {'F': 0.85, 'W': 0.075, 'S': 0.075},
	'FFR': {'F': 0.75, 'W': 0.05, 'S': 0.05, 'R': 0.15},
	'RFF': {'F': 0.75, 'W': 0.05, 'S': 0.05, 'R': 0.15},
	'RFR': {'F': 0.6, 'W': 0.05, 'S': 0.05, 'R': 0.3},

	'WWW': {'W': 0.4, 'R': 0.1, 'F': 0.5},
	'WWR': {'W': 0.3, 'R': 0.2, 'F': 0.5},
	'RWW': {'W': 0.3, 'R': 0.2, 'F': 0.5},
	'RWR': {'W': 0.15, 'R': 0.3, 'F': 0.55},

	'SSS': {'S': 0.25, 'W': 0.25, 'F': 0.5},
	'FSS': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'SSF': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'FSF': {'S': 0.25, 'W': 0.1, 'F': 0.65},

	'FFS': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'SFF': {'S': 0.25, 'W': 0.1, 'F': 0.65},

	'RRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'FRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'RRF': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'SRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'RRS': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'WRR': {'W': 0.4, 'S': 0.1, 'R': 0.3, 'F': 0.2},
	'RRW': {'W': 0.4, 'S': 0.1, 'R': 0.3, 'F': 0.2},

	'GGG': {'G': 0.7, 'R': 0.1, 'S': 0.1, 'W': 0.1},
	'GGR': {'G': 0.6, 'R': 0.3, 'S': 0.1},
	'RGG': {'G': 0.6, 'R': 0.3, 'S': 0.1},
	'RGR': {'G': 0.4, 'R': 0.4, 'S': 0.2},
	'RRG': {'G': 0.3, 'R': 0.5, 'S': 0.2},
	'GRR': {'G': 0.3, 'R': 0.5, 'S': 0.2},

	'R': {'F': 0.7, 'W': 0.05, 'S': 0.05, 'R': 0.2},
	'F': {'F': 0.8, 'W': 0.05, 'S': 0.05, 'R': 0.1},
	'S': {'F': 0.4, 'W': 0.05, 'S': 0.5, 'R': 0.05},
	'W': {'F': 0.4, 'W': 0.5, 'S': 0.05, 'R': 0.05},
	'G': {'G': 0.3, 'R': 0.5, 'S': 0.2}
}
HOLE_DIRECTION_TRANSITIONS = {
	'L': 0.25,
	'U': 0.25,
	'R': 0.25,
	'D': 0.25
}
POSSIBLE_NEXT_DIRECTIONS = ['L', 'U', 'R', 'D']
COURSE_DIMENSION = 1000

class GolfHoleDesigner():
	def __init__(self, transitionMatrix, width=30, height=7):
		self.transitionMatrix = transitionMatrix
		self.width = width
		self.height = height
		self.holeGrid = self.setupHole(width, height)
		self.courseGrid = self.setupCourse()

	def setupHole(self, width, height):
		holeGrid = [['R' for _ in range(width)] for _ in range(height)]
		middleRow = height // 2

		holeGrid[middleRow][0] = 'A'
	
		holeGrid[middleRow-1][2] = 'F'
		holeGrid[middleRow][2] = 'F'
		holeGrid[middleRow+1][2] = 'F'

		holeGrid[middleRow-1][-4] = 'G'
		holeGrid[middleRow][-4] = 'G'
		holeGrid[middleRow+1][-4] = 'G'

		return holeGrid
	
	def setupCourse(self):
		return [['W' for _ in range(1000)] for _ in range(1000)]

	def designHole(self):
		if self.width < 10 or self.height < 5:
			return [[]]
		
		# build fairway
		for col in range(3, self.width-6):
			for row in range(1, self.height-1):
				self.holeGrid[row][col] = self.getNextSquare(row, col)

		# build green
		for col in range(self.width-3, self.width):
			for row in range(2, self.height-2):
				self.holeGrid[row][col] = self.getNextSquare(row, col, green=True)

	def designCourse(self):
		holes = []
		for _ in range(9):
			self.designHole()
			holes.append([row[:] for row in self.holeGrid])

		i = j = 500

		for hole in holes:
			nextDirection = np.random.choice(
				POSSIBLE_NEXT_DIRECTIONS,
				p=[HOLE_DIRECTION_TRANSITIONS[nextDir] for nextDir in POSSIBLE_NEXT_DIRECTIONS]
			)

			hole = self.rotateHole(hole, nextDirection)
			holeHeight = len(hole)
			holeWidth = len(hole[0])

			i, j = self.findOpenArea(holeHeight, holeWidth, i, j, nextDirection)
			self.fillInCourse(hole, i, j)

			i += holeHeight
			j += holeWidth

		self.cutoffEdges()
	
	def findOpenArea(self, holeWidth, holeHeight, i, j, dir):
		if dir == 'R':
			j -= holeWidth
		elif dir == 'L':
			i -= holeHeight
		elif dir == 'D':
			i -= holeHeight
		elif dir == 'U':
			i -= holeHeight
			j -= holeWidth

		return (i, j)
		
	def cutoffEdges(self):
		top = left = 1000
		bottom = right = 0

		for i in range(len(self.courseGrid)):
			for j in range(len(self.courseGrid[0])):
				if not self.courseGrid[i][j] == 'W':
					top = min(top, i)
					left = min(left, j)

					bottom = max(bottom, i)
					right = max(right, j)

		self.courseGrid = self.courseGrid[top:bottom+1]
		self.courseGrid = [row[left:right+1] for row in self.courseGrid]

	def rotateHole(self, hole, nextDirection):
		if nextDirection == 'L':
			return [row[::-1] for row in hole]
		if nextDirection == 'D':
			return list(zip(*hole[::-1]))
		if nextDirection == 'U':
			return list(zip(*hole[::-1]))[::-1]
		return hole

	def fillInCourse(self, hole, i, j):
		for a in range(len(hole)):
			for b in range(len(hole[0])):
				self.courseGrid[i+a][j+b] = hole[a][b]

	def getNextSquare(self, row, col, green=False):
		previousSquares = self.holeGrid[row-1][col-1] + self.holeGrid[row][col-1] + self.holeGrid[row+1][col-1]
		
		if previousSquares in TRANSITION_MATRIX:
			transitions = TRANSITION_MATRIX[previousSquares]
		else:
			transitions = TRANSITION_MATRIX[self.holeGrid[row][col-1]]

		possibleNextSquares = list(transitions.keys())

		nextSquare = np.random.choice(
			possibleNextSquares,
			p=[transitions[possibleNextSquare] for possibleNextSquare in possibleNextSquares]
		)

		if green and nextSquare == 'F':
			return 'R'
		return nextSquare
	
	def createColorMap(self, type='hole'):
		if type == 'course':
			holeGridColors = np.array(
				[[SQUARE_TO_NUMBER[square] for square in row] for row in self.courseGrid],
				dtype=float
			)
		else:
			holeGridColors = np.array(
				[[SQUARE_TO_NUMBER[square] for square in row] for row in self.holeGrid],
				dtype=float
			)

		cmap = LinearSegmentedColormap.from_list('', SQUARE_HEX_COLORS, len(SQUARE_HEX_COLORS))
		plt.imshow(holeGridColors, cmap=cmap, vmin=0, vmax=len(SQUARE_HEX_COLORS) - 1)
		plt.xticks([])
		plt.yticks([])
		plt.title("The Most Interesting Golf Course Ever Designed")

		# I found the below code on this page: 
		# https://stackoverflow.com/questions/25482876/how-to-add-legend-to-imshow-in-matplotlib
		patches = [
			mpatches.Patch(
				color=SQUARE_HEX_COLORS[i],
				label="{l}".format(l=POSSIBLE_SQUARE_TYPES_FULL_NAMES[i])
			)
			for i in range(len(SQUARE_HEX_COLORS))
		]
		plt.legend(
			handles=patches,
			bbox_to_anchor=(1.1, 0),
			ncol=4,
			handletextpad=0.2
		)
		return plt

	def printHoleGrid(self):
		for row in self.holeGrid:
			print(' '.join(row))

	def createNExamples(self, directory, n):
		path = './' + directory
		if not os.path.exists(path):
			os.mkdir(path)
		for i in range(1,n+1):
			width = height = 1000
			while width > 250 or height > 250:
				self.designCourse()
				height = len(self.courseGrid)
				width = len(self.courseGrid[0])

			plt = self.createColorMap('course')
			fileName = path + '/example-' + str(i) + '.png'
			plt.savefig(fileName)
			self.courseGrid = self.setupCourse()

	def printDimensions(self, grid):
		print('Height:', len(grid), 'Width:', len(grid[0]))

def main():
	holeDesigner = GolfHoleDesigner(TRANSITION_MATRIX)
	holeDesigner.createNExamples('example2', 5)
	# holeDesigner.designCourse()
	# plt = holeDesigner.createColorMap('course')
	# plt.show()

if __name__ == "__main__":
	main()