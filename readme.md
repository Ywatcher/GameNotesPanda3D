This is a repository of games made by panda3d, working with pyqt and vispy;<br>

please do not follow this repo, since it 
is a draft space for me and can be quite
messy. However you can look up the code
for how a certain thing is implemented,
which may help you with your own project.

# Games
There are several game plans in this repository, including
### space 
a space combat simulator, I am currently working on it.
<br> 
features in plan:
- realistic control
- modular health system and realistic penetration
- radio environment simulation 
- temperature and air pressure simulation 

### spy 
simulates a social network suspicion, personal control and 
transfer of information. (sounds terrible)<br>
I havn't done anything to it yet.
### infection 
simulates biological contamination with creatures reproduce 
themselves and mutate<br>
I havn't done anything to it yet.
### station 
a misterious facility where paranormal event happens, and the 
environment(i.e. the facility) itself is controlled by an 
agent. Since the environment will spontaneously become more 
chaotic(because of random events) over time, the goal of the 
agent for the environment is to induce players to expand the 
facility and maintain the degree of order for the facility.
<br>
other features:
- abnormal gravity
- counter-intuitive causality between events, e.g. players' behavior
may affect the random seed used to generate landscape 
I havn't done anything to it yet.

### other ideas 
an environment with seasons. The division of seasons in the game 
can be very different from reality. For example, there can be a 
season where everything become rusty, and a season where everything
including, non-living creatures, becomes somewhat active and 
eeriely ecstasy.<br> 

# dependencies 
sorry for not able to provide a consistent dependency list, since 
this is a still infant project and there are many package I havnt
decide whether to use. Current required packages include:
```
numpy 
sympy
pytorch  
pyyaml 
panda3d 
pyqt5 
qpanda3d 
vispy
glfw # serves as vispy backend, can be replaced 
	# by any other offscreen backend that works
```

see `dependencies.yaml` for the environment setting I am 
currently using. However there are many packages that I
planed to use before, but no longer required now. 

#  document for space game
TODO<br>
I plan to implement general interfaces for agent, so that you can 
use AI to control the ship.














# useful stuffs in this repo 
### vispy background for panda3d 
`p1/py_src/vispyutil` provides a way to use vispy canvas to render image in real time 
and use it as background in panda3d. The angle and ratio of camera keep synchronized 
between panda3d showbase and vispy canvas.
### spherical landscape
`p1/py_src/art/procedural_art/fractal_landscape` is a framework to generate spherical landscape
by spliting icosahedron to appoximate sphere. 
### decorators
`p1/py_src/util/py_decorators.py` implements several decorators for python class.  
Including:\
decorators to register decorated methods on a dictionary, and \
way to use object method as decorator for other methods of it 
# todo
