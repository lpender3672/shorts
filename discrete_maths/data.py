
def convertfraction(n):

  if round(n,3) == int(n):
    return str(int(n))
  
  for i in range(2,100):
    if round(n*i, 3) % 1 == 0:
      return str(int(n*i)) + "/" + str(i)
  return str(round(n,5))
  


class vertex(object):
  def __init__(self, name):
    self.name = name
    self.arcs = []
  
  def attacharc(self, arc):
    self.arcs.append(arc)

class arc(object):
  def __init__(self, v1, v2, weight):
    self.weight = weight
    self.v1 = v1
    self.v2 = v2
    self.code = v1.name + v2.name



class network(object):
  def __init__(self, vertexnamelist):
    self.arcs = []
    self.vertexes = {}

    for v in vertexnamelist:
      self.vertexes[v] = vertex(v)

  def vertexnamelist(self):
    return [key for key in self.vertexes]

  def table(self):
    return self.arcs


  def getvertex(self, v1):

    if isinstance(v1, str):
      if v1 in self.vertexnamelist():
        return self.vertexes[v1]
    
    elif isinstance(v1, vertex):
      if v1.name in self.vertexnamelist():

        return self.vertexes[v1.name]


  def getarc(self, vertex1, vertex2):
    v1 = self.getvertex(vertex1)
    v2 = self.getvertex(vertex2)

    code = v1.name + v2.name

    for arc in self.arcs:
      if arc.code == code:
        return arc


  def addvertex(self, v):
    self.vertexes[v] = vertex(v)

  def addarc(self, startvertex, endvertex, weight = 0, directional = False):
    v1 = self.getvertex(startvertex)
    v2 = self.getvertex(endvertex)

    forwardarc = arc(v1, v2, weight) # 
    self.vertexes[v1.name].attacharc(forwardarc)
    self.arcs.append(forwardarc)
    
    if not directional:
      backwardarc = arc(v2, v1, weight) # if the arc is two directional
      self.vertexes[v2.name].attacharc(backwardarc)
      self.arcs.append(backwardarc)

  def getconnectingarcs(self, v):
    thisnetworksvertex = self.getvertex(v)
    return thisnetworksvertex.arcs




  def getcleanarcs(self):
    cleaned = []
    for arc in self.arcs:
      cleanedarc = "".join(sorted(arc.code) + [" ", str(arc.weight)])
      if cleanedarc not in cleaned:
        cleaned.append(cleanedarc)

    return cleaned

# # r o w
# c
# o
# l



class table(object):

  def __init__(self, rowcount, columncount, rownames = [], collumnnames = []):
    
    self.collumnnames = collumnnames
    self.rownames = rownames
    self.rowcount = rowcount
    self.collumncount = columncount
    self.tab = []
      


  def addcollumn(self, collumn):
    
    if len(collumn) != self.rowcount:
      raise InterruptedError("invalid number of rows added in the collumn")
    
    self.rowcount = len(collumn)
    self.collumncount+=1

    for i in range(len(collumn)):
      
      if not isinstance(self.tab[i], list):
        self.tab.append([])
      self.tab[i].append(collumn[i])


  def addrow(self, row):

    if len(row) != self.collumncount:
      raise InterruptedError("invalid number of collumns added in the row")
    
    self.collumncount = len(row)
    self.rowcount+=1
    self.tab.append(row)


  def getcollumn(self, rowindex):

    collumn = []
    for row in self.tab:
      collumn.append(row[rowindex])

    return collumn

  def getrow(self, collumnindex):
    row = self.tab[collumnindex]
    return row

  def getitem(self, collumnindex, rowindex):
    item = self.tab[rowindex][collumnindex]
    return item

  
  def setitem(self, item, collumnindex, rowindex):
    self.tab[collumnindex][rowindex] = item

  
  def setrow(self, collumnindex, key):

    for i in range(len(self.tab[collumnindex])):
      self.tab[collumnindex][i] = key(self, i)

  def setcollumn(self, rowindex, key):

    for i in range(len(self.tab)):
      self.tab[i][rowindex] = key(self, self.tab[i][rowindex])

  def printsimplex(self):

    longestitemlen = 0
    for row in self.tab:
      for item in row:
        if len(convertfraction(item)) > longestitemlen:
          longestitemlen = len(convertfraction(item))
    for item in self.collumnnames:
      if len(item) > longestitemlen:
        longestitemlen = len(item)

    spaces = ""
    for n in range(longestitemlen):
      spaces+=" "
    
    toprow = "|" + spaces
    for item in self.collumnnames:
      toprow += "|"
      toprow += spaces[:longestitemlen -len(str(item))]
      toprow += item
    
    print(toprow + "|")

    for row,i in zip(self.tab,range(self.rowcount)):
      rowname = self.rownames[i]
      if self.rownames[i-1] == "p":
        gap = ""
        for i in range(self.collumncount + 1):
          gap +="+"
          for i in range(len(spaces)):
            gap += "-" 
        print(gap + "+")

      rowstring = "|" 
      rowstring += spaces[:longestitemlen -len(rowname)]
      rowstring += rowname
      for item in row:
        rowstring += "|" 
        rowstring += spaces[:longestitemlen -len(convertfraction(item))]
        rowstring += convertfraction(item)
      print(rowstring + "|")





    

