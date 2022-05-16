import random



def is_sorted(self):
    for elem,next_elem in zip(self.l, self.l[1:]):
        if elem > next_elem:
            return False
    return True

def bogo_sort(l):
    while not is_sorted(l):
        random.shuffle(l)

