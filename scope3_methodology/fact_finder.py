#!/usr/bin/env python
import argparse

from utils import get_all_facts

parser = argparse.ArgumentParser(description="Find sources for a fact")
parser.add_argument("fact", nargs="?", type=str, const=1, help="the fact to find")
args = parser.parse_args()

facts = get_all_facts()

for fact in facts:
    if args.fact:
        if fact != args.fact:
            continue
    print(f"{fact}: {facts[fact]}")
