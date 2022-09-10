# Estimating corporate emissions

Imagine a company that has done a perfect job of measuring its carbon emissions. This company would have analyzed every expense in its financials, gone a level deeper to get activity data, performed lifecycle analysis on each of its products, and then asked each company in its supply chain to do the same.

This idealized company does not exist, though Google, Microsoft, Axel Springer, and Salesforce - among others - are making substantive efforts to get there. We can think of this as a spectrum where on the far left is a company that has done nothing to measure its emissions, on the middle-right are these best-of-breed companies, at at the far right is this idealized company who has measured everything.

We need a way to estimate corporate emissions based on the information we have available. We can translate the spectrum above into a table that translates what we know into a methodology to fill in the gaps of what we don't know:

What we know | Estimation methodology
---|---
Nothing | Use industry-average emissions per impression
Number of employees | Use industry-average emissions per employee
Sustainability report with missing or aggregated scope 3 categories | Use industry-average emissions per employee for missing categories
Complete sustainability report with suboptimal methodology (market-based vs location-based, or omitting embodied emissions, for instance) | Use industry average correction factors

## Calculating industry-average emissions factors

In this repository we aggregate public data from companies who produce sustainability reports - for instance, ![Axel Springer](../sources/companies/axel%20springer/data.yaml). We pull facts from these reports and use them to produce industry average values including:

- Office Emissions Per Employee Per Month
- Commuting Emissions Per Employee Per Month
- Travel Emissions Per Employee Per Month
- Datacenter Emissions Per Employee Per Month (may include cloud)
- Overhead Emissions Per Employee Per Month (this bucket includes third party software and marketing expenses; we need to get it broken out in a consistent way)
- Quality Ad Impressions Per Employee Per Month

We only include data that includes all scope 3 categories and uses location-based emissions for electricity use. Unfortunately, this means that very few sustainability reports are usable for us, though we expect this to change quickly.

## How we parse and understand corporate sustainability reports

**office emissions mt per month**
Emissions related to buildings and offices, ideally excluding production facilities (printing presses for instance).

**commuting emissions mt per month**
Includes home office emissions

**offsets and PPAs**
to discuss

## Usage

Note: this will change soon to support hierarchical organizations

Create a YAML file that describes the company you would like to model. The YAML file should look like this:

```yaml
company:
  name: Criteo
  products:
  - product:
      name: Criteo
      template: network
      identifier: criteo.com
  sources:
  - source:
      facts:
      - fact:
          employees: 2810
```

The file must have:

- Some number of facts, with `employees` required at a minimum unless you provide full corporate emissions data

To model emissions, make sure defaults have been computed. Then run:

```sh
./scope3_methodology/corporate.py --verbose {generic,atp,publisher} your_model.yaml
```
