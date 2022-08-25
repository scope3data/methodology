# Ad Tech Platform Model
The ad tech platform (ATP) model is built around the idea that ATPs integrate with other ATPs as part of a complex network. For instance, making a bid request to an SSP will generate many more bid requests to DSPs and possibly to real-time data providers as well.

Our model is focused on the primary emissions from an ATP. Understanding the secondary emissions would require modeling every downstream ATP and the relationships between the ATPs. Since most of these models and relationshipps require confidential data, we have included a stub to add this data.

# Methodology

TODO - link to Miro or copy as an image here?

# Usage
Create a YAML file that describes the company you would like to model. The YAML file should look like this:
```
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
- `company.products` with at least one product
- Each product should specify a template from the `templates` directory
- Some number of facts, with `employees` required at a minimum unless you provide full corporate emissions data
