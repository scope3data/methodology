# Key metrics
For a given datacenter, we need to know power efficiency (PUE), water efficiency (WUE?), number and type of servers, location, power sources, etc.

### Energy and offset calculation topics to discuss (todo):
- Market-based vs location-based
- Do renewable energy certificates (RECs) count?
- How do we adjust for 24/7 renewable energy as per Google?
- Marginal vs average grid mix

### Embodied emissions / cradle-to-grave
While embodied emissions are not broadly reported, we can make some assumptions to correct existing reports based on reported ratios of emissions from power usage (ignoring RECs and offsets) to emissions from manufacturing and end-of-life.

As an example, if our estimated ratio is 3:1 energy:embodied, then a company that reports 900 mt of emissions from energy usage would be adjusted to 1200 mt.

Note that methodologies for calculating embodied emissions here are not standardized, and the service lifetime of servers is a key input. For instance, a server with 300 mt of embodied emissions would have 100 mt/yr of emissions if its lifetime were three years, but only 60mt/yr of emissions if its lifetime were stretched to five years. Extending the useful lifecycle of servers can increase the energy usage thanks to continued improvements in power per watt, so companies should make an optimal lifecycle calculation.

### Recommendations for reporting emissions
- Provide the average lifetime of servers, or even better, new servers installed vs old servers decommissioned each year
