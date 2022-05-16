from data import network

def dijkstras(startnetwork, startvertex):

  vertexnetwork = network(startnetwork.vertexnamelist())
  for key in vertexnetwork.vertexes:
    vertexnetwork.vertexes[key].values = [0]

  vertexnetwork.vertexes[startvertex].finalvalue = 0
  step = 0
  vertexnetwork.vertexes[startvertex].step = step

  finalnetwork = network([startvertex])


  while len(finalnetwork.vertexes) != len(startnetwork.vertexes):
    
    

    for key in finalnetwork.vertexes:
      v = finalnetwork.vertexes[key]

      connectingarcs = startnetwork.getconnectingarcs(v)
      #print(v.name, connectingarcs)

      for arc in connectingarcs:
        if arc.v2.name not in finalnetwork.vertexnamelist():

          oldvalues = vertexnetwork.vertexes[arc.v2.name].values
          prev = vertexnetwork.vertexes[v.name].finalvalue
          
          if arc.weight + prev < oldvalues[-1:][0] or len(oldvalues) == 1:
            vertexnetwork.vertexes[arc.v2.name].values.append(arc.weight + prev)
            vertexnetwork.vertexes[arc.v2.name].oldvertex = v
    
    step+=1
    
    vertexnetworklist = [vertexnetwork.vertexes[key] for key in vertexnetwork.vertexes if vertexnetwork.vertexes[key].name not in finalnetwork.vertexnamelist() and vertexnetwork.vertexes[key].values[-1:][0] > 0]
    # list of vertexnetwork verticies that doesnt include the final value ones in the finalnetwork
    sortedvertexes = sorted(vertexnetworklist, key = lambda x : x.values[-1:][0])
    
    closestvertextostart = sortedvertexes[0]

    vold = closestvertextostart.oldvertex
    newarc = startnetwork.getarc(vold, closestvertextostart)
    vertexnetwork.addarc(newarc.v1, newarc.v2, newarc.weight)

    vertexnetwork.vertexes[closestvertextostart.name].finalvalue = closestvertextostart.values[-1:][0]
    vertexnetwork.vertexes[closestvertextostart.name].step = step
    finalnetwork.addvertex(closestvertextostart.name)
  
  return vertexnetwork