import math

class equation(object):

  def __init__(self, terms):
    self.terms = terms


  def solve(self, equations = []):
    print("solving the function")
    expression.printfunction(self.terms)
    print("= 0")



class term(object):
  def __init__(self, coefficient = 0, name = "number" , power = 1):

    self.coefficientname = name
    self.coefficientvalue = coefficient
    self.power = power




class expression(object):

  def __init__(self, terms):
    self.terms = terms

  def __add__(left, right):
    
    t = []
    for t1 in left.terms:
      for t2 in right.terms:
        if t1.coefficientname == t2.coefficientname and t1.power == t2.power:
          t.append(term(t1.coefficientvalue + t2.coefficientvalue, t1.coefficientname, t1.power))
    
    return expression(t)
  
  def __sub__(left, right):
    
    t = []
    for t1 in left.terms:
      for t2 in right.terms:
        if t1.coefficientname == t2.coefficientname and t1.power == t2.power:
          t.append(term(t1.coefficientvalue - t2.coefficientvalue, t1.coefficientname, t1.power))
    
    return expression(t)


  def __mul__(left, right):
    return "?"

  def equalto(self, expres):

    for t1 in self.terms:
      for t2 in expres.terms:

        if t1.coefficientname == t2.coefficientname and t1.power == t2.power:

          t1.coefficientvalue -= t2.coefficientvalue
          

    return equation(self.terms)
  
  def equalto_n(self, n = 0):
    return self.equalto(expression([term(n)]))



  def printfunction(terms):

    line = ""
    for term,i in zip(terms, range(len(terms))):

      if term.coefficientvalue == 0:
          continue

      if term.coefficientvalue > 0 and i != 0:
          line += "+"
          firstterm = False

      if term.coefficientname == "number":
        line += str(term.coefficientvalue)
        continue

      if term.coefficientvalue == 1:
        line+= term.coefficientname
      else:
        line += str(term.coefficientvalue)
        line += term.coefficientname

      if term.power != 1 and term.power != 0:
        line +=  "^" + str(term.power)

    
    print(line)


    

x2 = term(-2,"x", 2)
x = term( 10,"x")
n = term( -32 )

expr1 = expression([x2,x,n])
expr2 = expression([x2,x,x2])
(expr1 - expr2).equalto_n().solve()
