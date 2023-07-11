# An open framework for measuring digital advertising emissions

Our goal with this project is to build a framework where the media and advertising industry can collaborate on best practices for measuring emissions from the advertising value chain. This project was originally developed by Scope3 and is used to produce the Scope3 dataset.

Measuring emissions is extremely complicated in general. In the words of one industry leader, "it took us 100 years to figure out how to do financial accounting... and now we're trying to figure out carbon accounting in 2 or 3." As such, we feel like it's critical to learn in public and to be honest about what we know and what we don't know. Assuming the carbon accounting will require the same auditing and assurance process as the financial accounting world, we hope that this project will enable every step of the process to be traced and validated.

This measurement process, at a high level, works as follows:

1. Gather public materials referencing sustainability and other related data from industry participants
2. Pull out factual statements from these reports and normalize them into a common framework
3. Apply the facts we have about each company to a model that outputs emissions by activity (for instance, per ad impression)

As of now (summer of 2022) most sustainability reports have few useful facts that help us model the emissions of a company. They often omit entire categories of emissions, omit methodology information, and blend data from disparate business units. Trying to pull out data at a product or activity level is essentially impossible. Therefore, we need to apply domain knowledge to understand how these businesses work. We also need to integrate third-party data sources to increase the granularity of our data - for instance, using a service like SimilarWeb to get sessions and traffic for a domain or app. Finally, we can use the facts that we have across the industry to fill in gaps for companies that don't fully report all of the information we need.

## What's inside

This project is an attempt to "show our work" as we fill in the gaps in our knowledge. We encourage companies to use this project to improve their disclosures and even to consider providing machine-readable versions of their sustainability data.

In this project you will find:

- Public sustainability materials and the structured "fact" data from them. These are in the `data/companies` directory
- Scope3 has received confidential sustainability data from a number of companies. Some of this data is useful for producing default values, and is aggregated and included anonymously in `data/private/scope3`.
- A script to scan through the source data and produce industry defaults for various types of company. The script is `./scope3_methodology/cli/compute_defaults.py` and the templates are in `templates`. Also see `./scope3_methodology/cli/fact_finder.py` to see how defaults are derived from the data sources we have analyzed.
- A script to model the emissions for ad tech platforms (ssps, dsps, ad networks, dmps, creative ad servers, etc). See [ad tech platform docs](docs/ad_tech_model.md).
- A script to model the emissions for publishers. See [publisher docs](docs/publisher_model.md).
- Documentation of our calculations and assumptions in the `docs` directory. See [instructions on adding to docs](docs/README.md).

## Installation

[poetry](https://python-poetry.org/docs/) is used for python dependency management. See the poetry docs for offical instructions.

On Mac you can also install poetry via [brew](https://brew.sh/)

```sh
brew install poetry
```

Install Dependencies

```sh
poetry install
```

Activate virtual environment

```sh
poetry shell
```

If you want to commit code, install pre-commit hooks

```sh
pre-commit install
```

## Usage

To write defaults from latest sources:

```sh
./scope3_methodology/cli/compute_defaults.py
```

To run tests:

```sh
python -m unittest
```

To compute the corporate emissions, pass in its YAML file and org type (which will make defaults more accurate):

```sh
./scope3_methodology/cli/model_corporate_emissions.py --verbose {generic,atp,publisher} [company_file.yaml]
```

To compute the emissions for an ad tech company, pass in its YAML file:

```sh
./scope3_methodology/cli/model_ad_tech_platform.py -v [--corporateEmissionsG]  [--corporateEmissionsGPerRequest] [company_file.yaml]
```

To compute the emissions for publisher, pass in its YAML file:

```sh
./scope3_methodology/cli/model_publisher_emissions.py -v [--corporateEmissionsG]  [--corporateEmissionsGPerImp] [company_file.yaml]

```
