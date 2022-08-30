#!/usr/bin/env python
import argparse
from glob import glob
from pathlib import Path

import yaml
from utils import populate_facts
from yaml.loader import SafeLoader

parser = argparse.ArgumentParser(description="Find sources for a fact")
parser.add_argument("fact", nargs="?", type=str, const=1, help="the fact to find")
args = parser.parse_args()

facts: dict[str, list[float]] = {}
files = glob("sources/**/*.yaml", recursive=True)
for file in files:
    stream = open(file, "r")
    document = yaml.load(stream, Loader=SafeLoader)
    pth = Path(file)
    if "company" in document and "sources" in document["company"]:
        populate_facts(facts, "/".join(pth.parts[-2:]), document["company"]["sources"])
    if "sources" in document:
        populate_facts(facts, "/".join(pth.parts[-2:]), document["sources"])

for fact in facts:
    if args.fact:
        if fact != args.fact:
            continue
    print(f"{fact}: {facts[fact]}")
