# Key metrics
For a given datacenter, we need to know power efficiency (PUE), water efficiency (WUE?), number and type of servers, location, power sources, etc.

## Energy and offset calculation topics to discuss (todo):

- Market-based vs location-based
- Do renewable energy certificates (RECs) count?
- How do we adjust for 24/7 renewable energy as per Google?
- Marginal vs average grid mix

## Embodied emissions / cradle-to-grave

While embodied emissions are not broadly reported, we can make some assumptions to correct existing reports based on reported ratios of emissions from power usage (ignoring RECs and offsets) to emissions from manufacturing and end-of-life.

Boavizta provides an [API and methodology](https://doc.api.boavizta.org) for measuring embodied emissions. Manufacturing is in a different (and very possibly dirtier) grid than where it's used, so this should not be tied to the use location. Using the average of their 54 server models and an average server lifespan of 3.89 years (all defaults) we get a scope 3 measurement for manufacturing, transport, and end-of-life phases of 418 kgCO2e per year vs scope 2 electricity use of 1552 kWh. See `sources/research/boavizta/data.yaml`.

Note that methodologies for calculating embodied emissions here are not standardized, and the service lifetime of servers is a key input. For instance, a server with 300 mt of embodied emissions would have 100 mt/yr of emissions if its lifetime were three years, but only 60mt/yr of emissions if its lifetime were stretched to five years. Extending the useful lifecycle of servers can increase the energy usage thanks to continued improvements in power per watt, so companies should make an optimal lifecycle calculation.

It's also important to understand if emissions are allocated for purchased equipment at the moment of purchase or if these emissions are amortized across the lifetime of the equipment.

This [Facebook paper](https://ugupta.com/files/ChasingCarbon_HPCA2021.pdf) discusses this topic as capex vs opex, which implies that using publicly avaialble capex numbers could be a better proxy into emissions outside of the use phase. Have not investigated this further.

## Measuring technology providers

- Document snowflake (todo)


### Recommendations for reporting emissions

- Provide the average lifetime of servers, or even better, new servers installed vs old servers decommissioned each year
- Document how (if) embodied emissions are calculated
- Provide detail on whether emissions are taken at moment of purchase or amortized
