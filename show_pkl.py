import pickle
from pprint import pprint

with open('mahjong_agent.pkl', 'rb') as f:
    data = pickle.load(f)

pprint(data)