"""
A class that creates unique and interesting golf holes and courses.
Args:
	transitionMatrix (dict): transition probabilities
	length (int, optional): the length of each golf hole
	width (int, optional): the width of each golf hole
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import os

# All terrain types
POSSIBLE_SQUARE_TYPES = [
	'F', # Fairway
	'R', # Rough
	'W', # Water
	'S', # Sand
	'G', # Green
	'A', # Tee box
	'Wo' # Woods
]

# Full names for all terrain types
POSSIBLE_SQUARE_TYPES_FULL_NAMES = [
	'Fairway', 'Rough', 'Water', 'Sand', 'Green', 'Tee Box', 'Woods'
]

# Map for assigning terrain types to numbers (and later colors)
SQUARE_TO_NUMBER = {
	'F': 0,
	'R': 1,
	'W': 2,
	'S': 3,
	'G': 4,
	'A': 5,
	'Wo': 6
}

# Hex colors for each square type
SQUARE_HEX_COLORS = ['#1cb314', '#277523', '#247ec7', '#e3bf54', '#b3e8b0', '#ecf2eb', '#12380c']

"""
Transition matrix for many possible combinations
of squares. Given the following squares
1	2	3
4	5 	6
7	8	9	
The value of square 6 will be based on squares
2, 5, and 8. If a combo isn't included in the 
matrix, the transition will be based on the 
square directly to the left. See the end of the 
transition matrix for the default dictionaries 
in such a case. Note: these transition probabilities
are based on 1) my own knowledge of how golf courses
should look and 2) a lot of tweaking the matrix to ensure
that each terrain type didn't dominate any other.
"""
TRANSITION_MATRIX = {
	# Fairway transitions
	'FFF': {'F': 0.85, 'W': 0.075, 'S': 0.075},
	'FFR': {'F': 0.75, 'W': 0.05, 'S': 0.05, 'R': 0.15},
	'RFF': {'F': 0.75, 'W': 0.05, 'S': 0.05, 'R': 0.15},
	'RFR': {'F': 0.6, 'W': 0.05, 'S': 0.05, 'R': 0.3},

	# Water transitions
	'WWW': {'W': 0.4, 'R': 0.1, 'F': 0.5},
	'WWR': {'W': 0.3, 'R': 0.2, 'F': 0.5},
	'RWW': {'W': 0.3, 'R': 0.2, 'F': 0.5},
	'RWR': {'W': 0.15, 'R': 0.3, 'F': 0.55},

	# Sand transitions
	'SSS': {'S': 0.25, 'W': 0.25, 'F': 0.5},
	'FSS': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'SSF': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'FSF': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'FFS': {'S': 0.25, 'W': 0.1, 'F': 0.65},
	'SFF': {'S': 0.25, 'W': 0.1, 'F': 0.65},

	# Rough transitions
	'RRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'FRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'RRF': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'SRR': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'RRS': {'W': 0.1, 'S': 0.1, 'R': 0.4, 'F': 0.4},
	'WRR': {'W': 0.4, 'S': 0.1, 'R': 0.3, 'F': 0.2},
	'RRW': {'W': 0.4, 'S': 0.1, 'R': 0.3, 'F': 0.2},

	# Green transitions
	'GGG': {'G': 0.7, 'R': 0.1, 'S': 0.1, 'W': 0.1},
	'GGR': {'G': 0.6, 'R': 0.3, 'S': 0.1},
	'RGG': {'G': 0.6, 'R': 0.3, 'S': 0.1},
	'RGR': {'G': 0.4, 'R': 0.4, 'S': 0.2},
	'RRG': {'G': 0.3, 'R': 0.5, 'S': 0.2},
	'GRR': {'G': 0.3, 'R': 0.5, 'S': 0.2},

	# Default transitions (in case of a combo not
	# included above)
	'R': {'F': 0.7, 'W': 0.05, 'S': 0.05, 'R': 0.2},
	'F': {'F': 0.8, 'W': 0.05, 'S': 0.05, 'R': 0.1},
	'S': {'F': 0.4, 'W': 0.05, 'S': 0.5, 'R': 0.05},
	'W': {'F': 0.4, 'W': 0.5, 'S': 0.05, 'R': 0.05},
	'G': {'G': 0.3, 'R': 0.5, 'S': 0.2}
}

# Direction to place the next hole
# when creating a course
HOLE_DIRECTION_TRANSITIONS = {
	'L': 0.25,
	'U': 0.25,
	'R': 0.25,
	'D': 0.25
}

# Possible directions for the next hole
POSSIBLE_NEXT_DIRECTIONS = ['L', 'U', 'R', 'D']

# Width and length of a course (before
# adding anything or trimming the edges)
COURSE_DIMENSION = 1000

# How many holes to include in a course
HOLES_PER_COURSE = 9

class GolfHoleDesigner():
	def __init__(self, transitionMatrix, length=30, width=7):
		"""
		Creates a golf hole or an entire course. Sets up class
		variables to store a hole and a course.
		Args:
			transitionMatrix (dict): transition probabilities
			length (int, optional): the length of each golf hole
			width (int, optional): the width of each golf hole
		"""
		self.transitionMatrix = transitionMatrix
		self.length = length
		self.width = width
		self.holeGrid = self.setupHole(length, width)
		self.courseGrid = self.setupCourse()

	def setupHole(self, length, width):
		"""
		Sets up a hole with a starter fairway and green.
		All other squares should be rough.
		Args:
			length (int): the length of the hole
			width (int): the width of the hole
		"""
		holeGrid = [['R' for _ in range(length)] for _ in range(width)]
		middleRow = width // 2

		holeGrid[middleRow][0] = 'A' # tee box
	
		# 1x3 starter fairway
		holeGrid[middleRow-1][2] = 'F'
		holeGrid[middleRow][2] = 'F'
		holeGrid[middleRow+1][2] = 'F'

		# 1x3 starter green
		holeGrid[middleRow-1][-4] = 'G'
		holeGrid[middleRow][-4] = 'G'
		holeGrid[middleRow+1][-4] = 'G'

		return holeGrid
	
	def setupCourse(self):
		"""
		Sets up a course with entirely woods.
		"""
		return [['Wo' for _ in range(COURSE_DIMENSION)] for _ in range(COURSE_DIMENSION)]

	def designHole(self):
		"""
		Designs a hole with water, sand, fairway, and rough.			
		"""
		# if an insufficient width and height were passed in,
		# there won't be room for a fairway and green
		if self.length < 10 or self.width < 5:
			return [[]]
		
		# build all squares near the fairway
		for col in range(3, self.length-6):
			for row in range(1, self.width-1):
				self.holeGrid[row][col] = self.getNextSquare(row, col)

		# build all squares near the green
		for col in range(self.length-3, self.length):
			for row in range(2, self.width-2):
				self.holeGrid[row][col] = self.getNextSquare(row, col, green=True)

	def designCourse(self):
		"""
		Create HOLES_PER_COURSE holes and arrange them
		randomly in the self.courseGrid object	
		"""
		holes = [] # a list of HOLES_PER_COURSE different holes
		for _ in range(HOLES_PER_COURSE):
			self.designHole()
			holes.append([row[:] for row in self.holeGrid])

		# begin in the middle of the grid
		i = j = COURSE_DIMENSION//2

		for hole in holes:
			# randomly choose in which direction to place the hole
			nextDirection = np.random.choice(
				POSSIBLE_NEXT_DIRECTIONS,
				p=[HOLE_DIRECTION_TRANSITIONS[nextDir] for nextDir in POSSIBLE_NEXT_DIRECTIONS]
			)

			# rotate the hole grid according to the direction
			hole = self.rotateHole(hole, nextDirection)
			holeHeight = len(hole)
			holeWidth = len(hole[0])

			# move the i and j pointers to an open area next to the previous hole
			i, j = self.findOpenArea(holeHeight, holeWidth, i, j, nextDirection)

			# place the hole on the course
			self.fillInCourse(hole, i, j)

			i += holeHeight
			j += holeWidth

		# trim the unused edges of the course
		self.cutoffEdges()
	
	def findOpenArea(self, holeLength, holeWidth, i, j, direction):
		"""
		Move the pointers to an open area near the previous hole
		Args:
			holeLength (int): the length of the rotated hole 
			holeWidth (int): the width of the rotated hole
			i (int): the current row of the next-hole pointer
			j (int): the current column of the next-hole pointer
			direction (str): the chosen direction of the next hole
		"""
		if direction == 'R':
			j -= holeLength
		elif direction == 'L':
			i -= holeWidth
		elif direction == 'D':
			i -= holeWidth
		elif direction == 'U':
			i -= holeWidth
			j -= holeLength

		return (i, j)
		
	def cutoffEdges(self):
		"""
		Trim the edges of the self.courseGrid object. The grid 
		starts as 1000x1000, but all of that space isn't necessary
		after the holes have been added.
		"""
		top = left = COURSE_DIMENSION
		bottom = right = 0

		for i in range(len(self.courseGrid)):
			for j in range(len(self.courseGrid[0])):
				# search for a square that belongs to a hole
				if not self.courseGrid[i][j] == 'Wo':
					top = min(top, i)
					left = min(left, j)

					bottom = max(bottom, i)
					right = max(right, j)

		# trim vertically
		self.courseGrid = self.courseGrid[top:bottom+1]

		# trim horizontally
		self.courseGrid = [row[left:right+1] for row in self.courseGrid]

	def rotateHole(self, hole, nextDirection):
		"""
		Rotate the hole according to the direction
		it will be arranged in.
		Args:
			hole (2D list of str): the grid representing a hole
			nextDirection (str): the direction of that hole
		"""
		if nextDirection == 'L':
			# flip horizontally
			return [row[::-1] for row in hole]
		if nextDirection == 'D':
			# rotate 90 degrees clockwise
			return list(zip(*hole[::-1]))
		if nextDirection == 'U':
			# rotate 270 degrees clockwise
			return list(zip(*hole[::-1]))[::-1]
		
		# leave hole as it is
		return hole

	def fillInCourse(self, hole, i, j):
		"""
		Place a rotated hole in the proper spot
		on the course.
		Args:
			hole (2D list of str): the grid representing a hole
			i (int): the current row of the next-hole pointer
			j (int): the current column of the next-hole pointer
		"""
		for a in range(len(hole)):
			for b in range(len(hole[0])):
				self.courseGrid[i+a][j+b] = hole[a][b]

	def getNextSquare(self, row, col, green=False):
		"""
		Get the type for the square located at 
		(row, col) based on the transition matrix.
		Args:
			row (int): the row of the square type to obtain
			col (int): the column of the square type to obtain
			green (bool, optional): True if this square is part of the green
		"""

		# a list of the previous three squares (upper left, directly left, lower left)
		previousSquares = \
			self.holeGrid[row-1][col-1] + \
			self.holeGrid[row][col-1] + \
			self.holeGrid[row+1][col-1]
		
		# if the three-square combo exists in the matrix, use that
		if previousSquares in TRANSITION_MATRIX:
			transitions = TRANSITION_MATRIX[previousSquares]

		# otherwise, take the default transition matrix
		else:
			transitions = TRANSITION_MATRIX[self.holeGrid[row][col-1]]

		possibleNextSquares = list(transitions.keys())
		nextSquare = np.random.choice(
			possibleNextSquares,
			p=[transitions[possibleNextSquare] for possibleNextSquare in possibleNextSquares]
		)

		# no fairway squares should be near the green
		if green and nextSquare == 'F':
			return 'R'
		return nextSquare
	
	def createColorMap(self, entireCourse=False):
		"""
		Convert the current hole into a matplotlib heatmap
		Args:
			entireCourse (bool): True if this map should contain an entire course
		"""
		if entireCourse:
			holeGridColors = np.array(
				[[SQUARE_TO_NUMBER[square] for square in row] for row in self.courseGrid],
				dtype=float
			)
		else:
			holeGridColors = np.array(
				[[SQUARE_TO_NUMBER[square] for square in row] for row in self.holeGrid],
				dtype=float
			)

		# gather the colors for the heatmap
		cmap = LinearSegmentedColormap.from_list('', SQUARE_HEX_COLORS, len(SQUARE_HEX_COLORS))
		plt.imshow(holeGridColors, cmap=cmap, vmin=0, vmax=len(SQUARE_HEX_COLORS) - 1)

		# remove axis labels and ticks
		plt.xticks([])
		plt.yticks([])

		if entireCourse:
			plt.title("The Most Interesting Golf Course Ever Designed")
		else:
			plt.title("The Most Interesting Golf Hole Ever Designed")

		# I found the below code on this page for adding a legend:
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
		"""
		Print the current hole grid to the terminal.
		"""
		for row in self.holeGrid:
			print(' '.join(row))

	def createNExamples(self, directory, n):
		"""
		Create n example courses to a specified directory
		Args:
			directory (str): the directory to place outputs in
			n (int): how many examples to create
		"""
		path = './' + directory
		if not os.path.exists(path):
			os.mkdir(path)

		for i in range(1,n+1):
			# create a compact course
			width = height = 1000
			while width > 250 or height > 250:
				self.designCourse()
				height = len(self.courseGrid)
				width = len(self.courseGrid[0])

			plt = self.createColorMap(True)
			fileName = path + '/example-' + str(i) + '.png'

			# save the figure to the user's file system
			plt.savefig(fileName)

			# reset the courseGrid
			self.courseGrid = self.setupCourse()

def main():
	holeDesigner = GolfHoleDesigner(TRANSITION_MATRIX)

	# The below code creates a single hole
	# and displays it
	################
	holeDesigner.designHole()
	plt = holeDesigner.createColorMap()
	plt.show()
	################


	# Uncomment the below code to create a single course
	# and display it
	################
	# holeDesigner.designCourse()
	# plt = holeDesigner.createColorMap(entireCourse=True)
	# plt.show()
	################


	# Uncomment the below code to create 5 example courses
	# and output them to a directory.
	################
	# holeDesigner.createNExamples('example-courses-2', 5)
	################

if __name__ == "__main__":
	main()