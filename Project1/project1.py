import argparse
import string
from collections import defaultdict
from ascii_graph import Pyasciigraph
from ascii_graph.colors import *
from ascii_graph.colordata import vcolor
from pathlib import Path
from tqdm import tqdm
import time

parser = argparse.ArgumentParser(description='This is a script for argparse')
parser.add_argument('-f', '--filename', help='File to process')
parser.add_argument('-n', '--number', help='Number of words to appear in a histogram', type=int, default=10)
parser.add_argument('-l', '--length', help='Minimal length of the word to appear in a histogram', type=int, default=0)
parser.add_argument('-L', '--list', help='A list of words to ignore', nargs='*', default=[])
parser.add_argument('-c', '--chars', help='Sequences of characters to ignore', nargs='*', default=[])
parser.add_argument('-C', '--characters', help='Sequences of characters that must appear in words', nargs='*', default=[])
parser.add_argument('-F', '--folder', help='Folder to search in')
args = parser.parse_args()

d = defaultdict(int)   # initialise a dictionary

translator = str.maketrans('', '', string.punctuation + '–')   # make text uniform (remove capital letters and punctuation)

if args.folder:   # process all .txt files in a given folder
    folder = Path(args.folder)
    for files in folder.glob('*.txt'):
        with open(files, 'r', encoding='utf-8') as file:
            for line in tqdm(file, desc=f'Processing {files.name}', unit=' lines'):   # progress bar
                time.sleep(0.01)   # artificial delay to see progress
                line = line.translate(translator).lower()
                words = line.split()   # split a line into separate words
                for word in words:   # process each word separately
                    if len(word) >= args.length and (not args.characters or any(seq in word for seq in args.characters)):
                        if word in args.list or (args.chars and any(seq in word for seq in args.chars)):
                            continue
                        d[word] += 1
else:   # process a given .txt file
    with open(args.filename, 'r', encoding='utf-8') as file:
        for line in tqdm(file, desc=f'Processing {args.filename}', unit=' lines'):   # progress bar
            time.sleep(0.01)   # artificial delay to see progress
            line = line.translate(translator).lower()
            words = line.split()   # split a line into separate words
            for word in words:   # process each word separately
                if len(word) >= args.length and (not args.characters or any(seq in word for seq in args.characters)):
                    if word in args.list or (args.chars and any(seq in word for seq in args.chars)):
                        continue
                    d[word] += 1

sorted_d = dict(sorted(d.items(), key=lambda x: x[1], reverse=True))   # sort a dictionary in a descending order for keys
trimmed = list(sorted_d.items())[:args.number]   # convert a sorted dictionary into a list (needed for ascii_graph) and trim to a given number of words

graph = Pyasciigraph()   # prepare a graph
pattern = [IPur , Pur, ICya, Cya, Blu]   # prepare an array of colours
data = vcolor(trimmed, pattern)   # build a 'coloured' data list

for line in graph.graph('Sample Graph', data):
    print(line)