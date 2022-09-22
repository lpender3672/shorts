
import csv
import string

with open('dictionary.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
    words = []
    for w in data:
        if len(w[0]) == 5 and w[0] not in words:
            words.append(w[0])


n = len(words)
letters = list(string.ascii_lowercase + "- '/")
occurances = dict(zip( letters ,[0 for i in range(30)]))



for w in words:
    for l in w.lower():
        occurances[l] += 1

total = sum(list(occurances.values())[0:26])
i = 0
for l,o in occurances.items():
    if i<26:
        occurances[l] = o/total
    i+=1


def optimised_guess(words):

    scores = {}
    for word in words:
        wl = word.lower()
        for l in word.lower():
            try: scores[word]
            except:
                scores[word] = occurances[l] / ( 2 ** wl.count(l) )
            else:
                scores[word] += occurances[l] / ( 2 ** wl.count(l) )

    sorted_words = sorted(scores, key= lambda x: scores[x], reverse = True)

    return sorted_words


def guess(green, yellow):  # guess when unique yellows + greens = 4 or something
    raise NotImplemented()



if __name__ == "__main__":
    done = False
    l = ""
    guessed = ["-"," ","'","/",'"']
    wordz = list(filter(lambda s: all([c.lower() not in guessed for c in s]), words))
    while len(wordz) > 0:

        
        # filters words so that every letter in word not in a guessed letter

        w = optimised_guess(wordz)
        print(w[:10])
        guessed += list(w[0])

        wordz = list(filter(lambda s: all([c.lower() not in guessed for c in s]), words))

        


