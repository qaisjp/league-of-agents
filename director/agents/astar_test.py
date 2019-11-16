import pickle
from .classes import *
obs = pickle.load( open( "good_obs.pickle", "rb" ) )
print(obs)
