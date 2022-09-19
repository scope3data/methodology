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

## Mapping emissions into business units

 For a company like Google, the corporate sustainability report will be produced for the entire company. Some business units, like YouTube, will be broken out with specific emissions data; other business units will not be.

 For a business unit like ad tech inside Google, we need to allocate a percentage of the overall corporate emissions based on percentage of revenue or another method.

## Calculating industry-average emissions factors

In this repository we aggregate public data from companies who produce sustainability reports - for instance, [Axel Springer](../sources/companies/axel%20springer/data.yaml). We pull facts from these reports and use them to produce industry average values including:

- Office Emissions Per Employee Per Month
- Commuting Emissions Per Employee Per Month
- Travel Emissions Per Employee Per Month
- Datacenter Emissions Per Employee Per Month (may include cloud)
- Overhead Emissions Per Employee Per Month (this bucket includes third party software and marketing expenses; we need to get it broken out in a consistent way)

We only include data that includes all scope 3 categories and uses location-based emissions for electricity use. Unfortunately, this means that very few sustainability reports are usable for us, though we expect this to change quickly.

## How we parse and understand corporate sustainability reports

### Scope 3 Aggregation

One of the issues with combining sustainability reports across a supply chain is that, at least in theory, the upstream supply partner should already be accounted for by the downstream partner and vice versa.

In other words, a publisher should be including programmatic supply chain emissions already, as should a DSP, SSP, all the way through to the agency and advertiser. When we parse these reports, we should be excluding these in order to get a non-overlapping boundary.

In practice, at least in 2022, when we have asked companies - both publishers and ad tech companies - they have told us that these emissions are not included in their reporting boundaries today. Therefore we are not making any additional exclusions. In the future, we suggest that companies be explicit about what parts of their value chain are included recursively so that a de-duplication is possible (h/t Benjamin Davy for pointing this out!)

For the purposes of the current project, we are assuming the following categories of scope 3 emissions are fairly comprehensive for companies in the media and advertising space:


### offsets, RECs, and PPAs

to discuss

## Usage

Note: this will change soon to support hierarchical organizations

Create a YAML file that describes the company you would like to model. The YAML file should look like this:

```yaml
company:
  name: Criteo
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
