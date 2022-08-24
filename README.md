# methodology
Measurement methodology for advertising emissions

Secondary (downstream) emissions are stubbed. Discuss.
Where does YAML come from?

To install (MacOS):
$ brew install pyenv pipenv
$ pyenv install 3.10.6
$ pipenv --python 3.10 install
$ pipenv shell

To write defaults from latest sources:
$ python3 computeDefaults.py

To compute the emissions for a company, pass in its YAML file:
$ python3 adTechModel.py sources/companies/criteo/data.yaml
