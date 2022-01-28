#!/usr/bin/env python3

import string
from z3 import *

with open('answers.txt') as answers:
    ANSWERS = answers.read().splitlines()

# with open('guesses.txt') as guesses:
#     GUESSES = set(guesses.read().splitlines() + ANSWERS)

LENGTH = 5

Letter, letters = EnumSort('Letter', string.ascii_lowercase)
Result, (black, yellow, green) = EnumSort('Result', ['black', 'yellow', 'green'])
lettermap = dict(zip(string.ascii_lowercase, letters))
answer_arr = []
for i in range(LENGTH):
    answer_arr.append(Const(f'answer_{i}', Letter))

s = Solver()
s.add(Or(*[And(*[answer_arr[i] == lettermap[answer[i]] for i in range(LENGTH)]) for answer in ANSWERS]))

def parse_response(response):
    m = {'b' : black, 'y' : yellow, 'g' : green}
    return list(map(m.get, response))

def consequences(guess, results):
    information = []
    for i, (letter_str, result) in enumerate(zip(guess, results)):
        letter = lettermap[letter_str]
        if result == black:
            information.extend([answer_arr[j] != letter for j in range(LENGTH)])
        elif result == yellow:
            information.append(answer_arr[i] != letter)
            information.append(Or(*[answer_arr[j] == letter for j in range(LENGTH) if i != j]))
        elif result == green:
            information.append(answer_arr[i] == letter)
    return information

def pp(model):
    return ''.join([str(model[answer_arr[i]]) for i in range(LENGTH)])

def main():
    while True:
        check = s.check()
        if check != sat:
            print('Something went wrong, cannot solve')
            break
        guess = pp(s.model())
        results = [None]
        while None in results:
            response = input(f'Guess {guess}: ')
            results = parse_response(response)
        if results == [green] * LENGTH:
            print('yay')
            break
        s.add(consequences(guess, results))

if __name__ == "__main__":
    main()

