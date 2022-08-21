from glob import glob
import yaml
from yaml.loader import SafeLoader
from typing import Dict, List

# get a list of all facts from our sources
facts: Dict[str, List[float]] = {}

files = glob('sources/**/*.yaml', recursive=True)
for file in files:
    stream = open(file, 'r')
    documents = list(yaml.load_all(stream, Loader=SafeLoader))
    for document in documents:
        if 'company' not in document:
            print('No company found in ' + document)
            continue
        if 'sources' not in document['company']:
            print('No sources found in ' + document)
            continue
        for source in document['company']['sources']:
            for fact in source['source']['facts']:
                keys = [key for key in fact['fact'] if key != 'reference' and key != 'comment']
                for key in keys:
                    if key not in facts:
                        facts[key] = []
                    facts[key].append(fact['fact'][key])
print(facts)
