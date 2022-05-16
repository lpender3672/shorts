import math

class variable(object):
  def __init__(self, name = "number", power = 1):
    self.name = name
    self.power = power
    # power could be a variable or an expression?



class term(object):
  def __init__(self, coefficient = 0, variables = [variable()]):

    self.coefficient = coefficient
    # coefficient could be a variable or an expression?
    self.variables = variables

  def __add__(self, b):
    return term(self.coefficient + b.coefficient, self.variables)

  def __sub__(self, b):
    return term(self.coefficient - b.coefficient, self.variables)

  def __mul__(self, b):
    var = self.variables + b.variables
        
        
    l = [[ a for a in var if a.name == var[i].name] for i in range(len(var))]
    fl = []
    for i in range(len(l)):
      if l[i] not in fl:
        fl.append(l[i])

    variables = []
    for lis in fl:
      pwr = 0
      for v in lis:
        pwr += v.power
      variables.append(variable(lis[0].name, pwr))

    return term(self.coefficient * b.coefficient, variables)

  def __truediv__(self, c):
    v = []
    for ve in c.variables:
      v.append(variable(ve.name, -ve.power))

    b = term(1/c.coefficient, v)
    
    var = self.variables + b.variables
        
    l = [[ a for a in var if a.name == var[i].name] for i in range(len(var))]
    fl = []
    for i in range(len(l)):
      if l[i] not in fl:
        fl.append(l[i])

    variables = []
    for lis in fl:
      pwr = 0
      for v in lis:
        pwr += v.power
      variables.append(variable(lis[0].name, pwr))

    return term(self.coefficient / b.coefficient, variables)

  def __str__(self):
    return str(expression([self]))
 

class expression(object):

  def __init__(self, terms):
    self.terms = terms



  def __add__(self, b):
    
    if isinstance(b, expression):
      t = []
      for t1 in self.terms:
        for t2 in b.terms:
          if set(t1.variables) == set(t2.variables):
            t.append(t1+t2)
            break
    
      return expression(t)
  
  def __sub__(self, b):
    
    if isinstance(b, expression):
      t = []
      for t1 in self.terms:
        for t2 in b.terms:
          if set(t1.variables) == set(t2.variables):
            t.append(t1-t2)
            break
    
      return expression(t)



  def __mul__(self, b):
    
    if isinstance(b, int) or isinstance(b, float):
      t = []
      for t1 in self.terms:
        t.append(term(t1.coefficient * b, t1.variables))
    
      return expression(t)

    if isinstance(b, term):
      t = []
      for t1 in self.terms:
        t.append(t1*b)
      
      return expression(t)
  
  def __truediv__(self, b):

    if isinstance(b, int) or isinstance(b, float):
      t = []
      for t1 in self.terms:
        t.append(term(t1.coefficient / b, t1.variables))
    
      return expression(t)

    if isinstance(b, term):
      
      t = []

      for t1 in self.terms:
        t.append(t1/b)
        
      
      return expression(t)


  def __str__(self):

    line = ""
    for term,i in zip(self.terms, range(len(self.terms))):

      if term.coefficient == 0:
        continue

      if term.coefficient > 0 and i != 0:
          line += "+"
      elif term.coefficient < 0:
          line += "-"

      if abs(term.coefficient) != 1:
          line += str(abs(term.coefficient))
          
      for v in term.variables:
        
        if v.name == "number":
          continue

        if v.power != 0:
          line += v.name
          if v.power != 1:
            line +=  "^" + str(v.power)

        

    
    return(line)


class vector3(object):
  def __init__(self, x,y,z):

    self.x, self.y, self.z = x,y,z

    if isinstance(x, expression) or isinstance(x, expression) or isinstance(x, expression):
      pass

    else:
      self.mod = math.sqrt(x**2 + y**2 + z**2)

      if self.mod == 1:
        self.norm = self
      else:
        self.norm = vector3(x/self.mod, y/self.mod, z/self.mod)

  def __mul__(self, b):
    
    if isinstance(b, float) or isinstance(b, int) or isinstance(b, term):
      return vector3(self.x*b, self.y*b, self.z*b)
    
    if isinstance(b, vector3):
      raise TypeError("unsupported operand types")
      # dot product and vector product

  def dot(self, b):
    pass
  
  def scalar(self, b):
    pass

  def __add__(self, b):
    
    if isinstance(b, float) or isinstance(b, int):
      return vector3(self.x+b, self.y+b, self.z+b)
    
    if isinstance(b, vector3):
      return vector3(self.x+b.x,self.y+b.y,self.z+b.z)
  
  def __sub__(self, b):
    
    if isinstance(b, float) or isinstance(b, int):
      return vector3(self.x-b, self.y-b, self.z-b)
    
    if isinstance(b, vector3):
      return vector3(self.x-b.x,self.y-b.y,self.z-b.z)



  def __str__(self):
    return str(self.x)+" "+str(self.y)+" "+str(self.z)


x = expression([term(2,[variable("x",2),variable("y")]), term(10)])
y = expression([term(4,[variable("x")]), term(5)])
z = expression([term(1,[variable("x")]), term(8)])
#print(x)

a = expression([term(4,[variable("x")]), term(5)])
xterm = term(1, [variable("x",2),variable("y",2)])

print(x, xterm)
print(x-x*2)

# expression inception