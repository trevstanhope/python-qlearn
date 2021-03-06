import numpy as np
import scipy as sp
import json
import skfuzzy as fuzz
import sklearn
import matplotlib.pyplot as plt

class FuzzyLearner:
    """
    """
    def __init__(self, rules, Q=None):
        if Q is not None:
            self.load_matrix(Q)
        else:
            self.new_matrix()
        self.load_rules(rules)

    # Load Rules
    def load_rules(self, filename):
        with open(filename, 'r') as jsonfile:
                rules = json.loads(jsonfile.read())
                self.actions = rules['actions']
                self.state = rules['state']
                self.rules = rules['results']
                self.x = np.arange(self.state['min'], self.state['max'])
                for subset, parts in self.rules.items():
                    aggregated = []
                    points = []
                    for n, v in parts.items():
                        print n
                        if v['mf'] == 'tri':
                            mf = fuzz.trimf(self.x, v['shp'])
                        if v['mf'] == 'trap':
                            mf = fuzz.trapmf(self.x, v['shp'])
                        elif v['mf'] == 'gbell':
                            mf = fuzz.gbellmf(self.x, v['shp'])
                        aggregated.append(mf)
                        points.append(v['pts'])
                    self.rules[subset] = (aggregated, points)

    # Save Matrix
    def save_matrix(self, filename):
        """
        Save current Q-matrix to file
        """
        l = self.Q.tolist()
        with open(filename, 'w') as jsonfile:
            jsonfile.write(json.dumps(l, indent=4))

    # New Matrix
    def new_matrix(self, s_shape, d_shape):
        """
        Generate new blank Q-matrix
        """
        self.Q = np.zeros(s_shape + d_shape)

    # Load Matrix
    def load_matrix(self, filename):
        """
        Load Q-matrix from file
        """
        with open(filename, 'r') as jsonfile:
            self.Q = np.array(json.loads(jsonfile.read()))
    
    # Guess
    def guess(self, s):
        a = np.argmax(self.Q[s]) # if Q is all zero, then defaults to first action
        return a

    # Classify result
    def classify(self, r):
        """
        For a given result (r) of action, determine the fuzzy membership.
        Returns the class (0 to n) o associated with the result.
        """
        try:
            for subset, rules in self.rules.items():
                aggregated, points = rules
                m = [fuzz.interp_membership(self.x, mf, r) for mf in aggregated] # Calculate membership values
                c = np.argmax(m)
                return c
        except Exception as error:
            raise error

    # Train
    def train(self, s, a, r):
        """
        Given the previous state (s) and result (r) and the Q-matrix, decide which action should be taken
        """
        c = self.classify(r)
        p = self.points[c]
        self.Q[s][a] = self.Q[s][a] + p
        print("%s\t--> %s\t--> %s\t--> %s" % (str(s), str(a), str(r), str(p)))
        #print("Points: %f" % p)
        return p

if __name__ == '__main__':
    fl = FuzzyLearner("rules.json", Q="matrix.json")
    fl.new_matrix((640,640,10), (len(fl.actions),))
    if True:
        t = np.linspace(-16*np.pi, 160*np.pi, 100)
        x = 30 * np.sin(t)
        dx = 30 * np.sin(t)
        vel = 1
        for v in range(0, vel):
            for e in x.astype(int).tolist():
                for de in dx.astype(int).tolist():
                    r = e + int(5*np.random.normal())
                    a = fl.guess((e, de, v)) # guess action
                    #print fl.actions[a]
                    # c = fl.classify(e) # classify result, do not train matrix
                    fl.train((e, de, v), a, r) # train matrix
            for i in range(len(fl.actions)):        
                plt.plot(fl.Q[:,:,0,i])
            plt.show()
    fl.save_matrix("matrix.json")
    print 'end'
