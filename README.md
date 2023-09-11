# System Title: Markov Golf Course Designer

# Description
This program generates a golf hole (or a collection of golf holes) using a Markov Chain. It 
starts each hole with a small fairway and green, and then expands both to include water, sand, and rough
based on hard-coded probability distributions (in the future, that could be expanded so that the user 
could choose how much of each element they wanted in their course). The system uses a Markov Chain
to select the type of terrian for a piece of the grid based on the three squares to directly to
its left. There are 5 example holes in the `example-holes` directory and 5 example courses in the
`example-courses` directory.

Note: when viewing an individual hole, the white square on the left is where the hole begins, and
the light-green patch on the right edge is the green (where the hole is located).

# How to setup and run code
After cloning this repository, run `python main.py` or `python3 main.py` (depending upon your setup) 
from the terminal to run the code.
Currently, the program will create one golf hole and show the diagram. I have put 
commented-out code in the `main()` function which can be uncommented to create an 
entire course or to create a given number of example courses and save them to png files. 
Numpy and Matplotlib must be installed for the code to function properly.

# How this system is personally meaningful to me
This system is meaningful to me because I really enjoy playing golf, and I especially like
when a course is very well-designed. While my course designer program isn't directly applicable
(because a real course would have to be placed within the confines of the nature of the area), 
it could help give professional designers ideas about interesting ways to organize water hazards,
bunkers, and more.

# Challenge
I had already worked with Markov Chains in AI, so I decided to challenge myself by repeatedly 
expanding upon my original idea and adding layers that make it 
more complicated and cooler. I started out by creating a single hole with just a fairway and a green.
Then I added water and sand traps, which made the designs much more realistic and interesting.
From there, I challenged myself even further by creating entire courses instead of single 
holes. This addition took extra effort because I needed to ensure that the holes were 
somewhat-close together, but also arranged randomly and in an interesting shape. My algorithm 
for this part of the code isn't perfect in terms of efficiency and accuracy, but it gets the 
job done and produces a very cool-looking output, unlike some of the algorithms I tried originally.

I pushed myself outside of my comfort zone by developing my own algorithm for arranging the 
course. This challenge was important for me because it gave me a lot of confidence in my 
ability to create complicated code, which I sometimes struggle with. One next step for me could 
be to ensure that my algorithms are time- and space-optimal. I know that this aspect of programming 
is extremely important for employers, so I'd like to practice the skill.

# Creativity
I definitely believe that this system is creative because it generates a completely new golf hole or 
course every time the program is run (novelty). It also outputs some really interesting holes, many 
of which I would like to play! I think that aspect checks off the 'valuable' box for creativity, 
as I could envision a (more complex and location-specific) system helping golf course designers 
with their work.

# Sources
I didn't consult with any colleagues for this project. I gathered some code snippets (especially for 
matplotlib commands) from StackOverflow and other online sources. Other than that, the ideas and 
code are entirely mine.