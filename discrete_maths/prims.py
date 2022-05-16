from data import network

def prims(startnetwork, startvertex):

  minimumspanningtree = network([startvertex])
  while len(minimumspanningtree.vertexes) != len(startnetwork.vertexes):
    # add nearest vertexes
    possiblearcs = []
    for key in minimumspanningtree.vertexes: # for every vertex in the minimum spanning tree
      v = minimumspanningtree.vertexes[key]
      
      connectingarcs = startnetwork.getconnectingarcs(v) # get connecting arcs
      
      for arc in connectingarcs: # for every connected arc

        if arc.v2.name not in minimumspanningtree.vertexnamelist(): # thats not already in the tree 
          possiblearcs.append(arc)
    
    sortedarcs = sorted(possiblearcs, key = lambda x : x.weight)
    shortestarc = sortedarcs[0] # take the shortest possible
    minimumspanningtree.addvertex(shortestarc.v2.name)
    minimumspanningtree.addarc(shortestarc.v1, shortestarc.v2, shortestarc.weight)

  return minimumspanningtree