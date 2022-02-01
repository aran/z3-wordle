#!/usr/bin/env python3

import string
from itertools import combinations
from z3 import *

with open('answers.txt') as answers:
    ANSWERS = answers.read().splitlines()

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

    results_inv = {k: [] for k in [black, yellow, green]}
    results_inv.update({result: [i for i, r in enumerate(results) if result.eq(r)] for result in results})
    letter_inv = {letter: [i for i, l in enumerate(guess) if letter == l] for letter in guess}

    information.extend([answer_arr[i] == lettermap[guess[i]] for i in results_inv[green]])
    information.extend([answer_arr[i] != lettermap[guess[i]] for i in results_inv[yellow] + results_inv[black]])

    for letter, positions in letter_inv.items():
        remaining_positions = set(range(LENGTH)) - set(positions) - set(results_inv[green])
        at_least = len([results[i] for i in positions if results[i].eq(yellow)])
        is_exact = black in [results[i] for i in positions]

        location_possibilities = combinations(remaining_positions, at_least)
        collect = []
        for locations in location_possibilities:
            conjunct = [answer_arr[i] == lettermap[letter] for i in locations]
            if is_exact:
                not_it = remaining_positions - set(locations)
                conjunct.extend([answer_arr[i] != lettermap[letter] for i in not_it])
            collect.append(And(*conjunct))

        information.append(Or(*collect))

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
            response = input(f'Guess "{guess}": ')
            results = parse_response(response)
        if results == [green] * LENGTH:
            print('yay')
            break
        s.add(consequences(guess, results))

if __name__ == "__main__":
    main()
