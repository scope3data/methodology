# Life Cycle Analysis for Advertising

Life cycle assessment or LCA (also known as life cycle analysis) is a methodology for assessing environmental impacts associated with all the stages of the life cycle of a commercial product, process, or service. For instance, in the case of a manufactured product, environmental impacts are assessed from raw material extraction and processing (cradle), through the product's manufacture, distribution and use, to the recycling or final disposal of the materials composing it (grave). (from ["Life-Cycle Assessment"](https://en.wikipedia.org/wiki/Life-cycle_assessment) - Wikipedia).

From [Wikipedia](https://en.wikipedia.org/wiki/File:Life_cycle_analysis_and_GHG_carbon_accounting.jpg), an LCA diagram with GHG phases along the right side
![Example of an LCA with GHG emissions](images/lca_ghg.jpeg)

## Life Cycle Assessment of an Advertisement

To "manufacture" an ad impression, our raw materials are media (content), creative (the ad itself), and human attention (via ears and/or eyes). Different channels will have different combinations of these ingredients. For instance, a billboard often doesn't have content, just the ad.

The life cycle of an ad has five major components:

1. Producing the creative
2. Producing the content
3. Selecting which ad to display
4. Consumption of the media and creative
5. Consumer behavior after consuming the ad

![Lifecycle of an ad](images/lca_ad.png)

Note that this project *does not* recommend a life cycle boundary; rather, it produces outputs that can be included or excluded based on the selected life cycle span.

## Methodologies

There are three well-documented methodologies that we have seen produced by the industry in addition to this project:

- [DIMPACT](https://dimpact.org/methodology)
- [SRI](https://www.sri-france.org/wp-content/uploads/2021/11/SRI_Calculating-the-carbon-footprint_VF.pdf)
- [GroupM / EY](https://www.groupm.com/media-decarbonization-framework-groupm/)

### Life cycle boundaries by methodology

| Topic | DIMPACT | SRI | GroupM / EY
|---| --- | --- | ---
| Includes creative production | No | No | Yes
| Includes content production | Partial | No | Yes
| Includes ad selection | No | Partial | Yes
| Includes consumption of media and creative | Media only | Creative only | No
| Includes advertised emissions | No | No | No
| Includes embodied emissions for consumer device | Optional | Yes | Yes
| Includes embodied emissions for servers | Optional | No | Yes
| Includes embodied emissions for networking equipment | Optional | No | Yes
| Includes emissions from ad tech vendors | No | No | Yes
| Requires location-based emissions | Recommended | No | No


## Notes

DIMPACT: Includes "content management and distribution," excludes "HR systems, back-office administration, corporate business travel, and so forth." Excludes content production except when "content production is so intertwined with the operational and distribution systems that exclusion becomes impractical."
