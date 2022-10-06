#!/usr/bin/env python
""" Fact finder extracts all facts from data yaml files"""
import argparse

from scope3_methodology.utils.utils import get_all_facts


def main():
    """
    Find facts from yaml data files in the repo.
    Optional arguments to find specific fact
    Default: finds all facts
    """
    parser = argparse.ArgumentParser(description="Find sources for a fact")
    parser.add_argument("fact", nargs="?", type=str, const=1, help="the fact to find")
    args = parser.parse_args()

    facts = get_all_facts()

    for fact in facts:
        if args.fact:
            if fact != args.fact:
                continue
        print(f"{fact}: {facts[fact]}")


if __name__ == "__main__":
    main()
