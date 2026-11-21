# What a Rubik’s Cube Solver Needs to Know

*Mingpu (Andy) Wu*

If someone hands me a scrambled Rubik’s Cube, I can see where every piece ended up, but I have no record of the turns that put it there. Can a program find its way back using only what I can see? In high school, I explored that question with Alyna Tang through the CSIRE program at Stony Brook University, under the mentorship of Professor David Gu. Alyna’s part of our final presentation explained how sequences of turns could reposition selected pieces. My part focused on turning that mathematics into code.

The first decision was how to describe the cube. A corner can sit in its correct slot with its three colors facing the wrong directions. Recording its location alone would lose exactly the information a solver needs to finish the puzzle. The model therefore tracks both the position and orientation of eight corners and twelve edges. Each face turn rearranges those pieces according to a fixed rule. Once a turn can be expressed that way, the program can apply it, undo it, or combine it with another. That was where group theory became tangible for me. The same operation I could perform with my hands could also be a rule the computer could search over.

Years later, I returned to the project with the presentation slides still available and the original source code missing. This repository is a renewal of that work. The new Python implementation, developed with OpenAI Codex assistance, uses a four-phase search based on Thistlethwaite’s algorithm. In the first phase, for example, the solver cares only about which edges are flipped. Two cubes that look quite different can count as the same state for that part of the search. Once the edges are oriented, later phases use turns that preserve that progress. By the final phase, half turns are enough to finish the cube.

One test returns to the question that started the project. The renewed solver received 100 legal cube states generated directly from piece positions and orientations. There was no scramble history to reverse. For all 100 states, replaying the returned moves restored the solved cube. What I like about this result is that anyone holding the same scrambled cube can check it, one turn at a time.

## Project materials

- [Run the solver and explore the implementation](SOLVER.md)
- [Original CSIRE midterm presentation](originals/CSIRE-midterm.pptx)
- [Original CSIRE final poster and implementation slides](originals/CSIRE-final-poster.pptx)
