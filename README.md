# pyromu
A faster Version Of Python's Stdlib Random module using algorythms provided by the website: http://www.romu-random.org/ as well as this paper: http://arxiv.org/abs/2002.11331.pdf written by Mark A. Overton.

## Updates
- I am rewriting this library's C End to use arrays for greater speeds and bytearrays for easier memory managment otherwise it will be a cython internal class.

## Why Write Such A Library?
The Python Random stdlib-module is fast in all but it suffers from it's overall memory consumption not to mention that it's running the 
Mersenne Twister under the hood and with that 624 integers that need to be pulled when you want to get or set the random module's states
which is a large amount of numbers considering each integer is 32 bits.
Functions like `getrandbits()` and it's brother `randbytes()` have a flaw where they need to convert gigantic integers which can lead to numerous 
bottlenecks. By replacing these and other low-level functions it maybe possible to have an overall faster and more friendly random module. 
Being able to optionally pick between different Romu Algorythms can beneift you in deciding which would be best for your projects.
It is my goal to make this library simillar to libraries such as uvloop with the goal of replacing stdlib modules with faster ones.

## TODOS
- Find a way to override _random.Random() and the random.Random() class objects with our own.
- Try to write as many functions as we can in Cython whenever possible so that we don't loose any speed long-term
- Fix Licensing Issues.

