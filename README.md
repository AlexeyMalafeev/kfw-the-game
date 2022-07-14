# About KFW

KFW, short for Kung-Fu World, is a turn-based hot-seat role-playing game. It has been in development, on and off, since 2013, as my pet project. Having developed and playtested it for countless hours with my friends, it's only now that I've decided to release it to a wider audience. If you are into old school films about Chinese kung-fu and don't mind nerdy text-based games, you may enjoy it. That said, it is still work in progress, although perfectly playable.  

### Some features:

* Hot-seat play with your friend(s) and/or AI players
* Lots of randomly-generated content: tens of thousands of unique styles, moves, etc.
* Weird ASCII art that will hopefully make you smile
* Goofy dialogues in the spirit of low-budget Hong-Kong flicks
* Fight AI is trained with a custom-implemented genetic algorithm
* Machine learning-based fight outcome prediction

The game looks something like this:

<img width="308" alt="image" src="https://user-images.githubusercontent.com/10167436/178922104-f26d6bfb-2499-4437-962f-29a807a8b269.png">

<img width="428" alt="image" src="https://user-images.githubusercontent.com/10167436/178922621-e7b6f80d-6f81-47e0-a97d-a6ee6e8c88c1.png">

## Installing and running the game

Grab the latest release (I don't recommend just cloning master, as it has a lot of extra files that are used in development, but not necessary for playing the game). To play, you only need Python 3.8 or greater (install from python.org).  

Note: some ML-related modules do require such external dependencies as `pandas`, `numpy` and `sklearn`, but these are not needed to just play the game. 

To start a new game, run `NG_default.py`. To load a previously saved game, run `load_game.py`.  Note that it won't work correctly if you run either of the scripts in an IDE like PyCharm. Instead, run these scripts from the command line.

## How to play

In this game, you play as a beginner kung-fu practitioner. You train hard to improve your fighting skills, protect the weak against oppressors and, one day, even found your own martial arts school. You have to compete with other practitioners as well as stand up against thugs and wrongdoers to prove your worth. Become stronger by either practicing or defeating foes in the streets of Foshan, learn new moves and techniques, take part in tournaments and enjoy your life in this fantasy Kung-Fu World.

There are four ways to win in this game:
1. **Grandmaster**: simply reach level 20
2. **Folk Hero**: become known for doing good deeds such as protecting the weak and helping the poor
3. **Kung-fu Legend**: perform a few of unique Accomplishments
4. **Greatest Fighter**: win in a crazy number of fights

## Note about the code

Should you want to take a peek at the code, since we're on GitHub and all, be warned that it is messy. The bulk of it was written back when my Python kung-fu was still weak, and I don't have much time these days to clean up accrued technical debt. That said, the code base in its present state is not completely terrible; it is somewhat readable and hopefully free of major bugs. I hope that one day I'll get around to refactoring everything. :P

## Final remarks

Thank you for reading this and for your interest in this game! If you decide to give KFW a try, I hope you enjoy playing the game as much as I did creating and play-testing it. 
