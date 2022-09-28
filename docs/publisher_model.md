# Publisher Model

Publishers (media owners, platforms, etc) tend to be complex businesses, often with thousands of employees and complex organizational structures. Publishers often own and operate properties in different countries, sometimes with joint ventures, and have multiple revenue streams.

Modeling the emissions for a single digital ad impression on a property requires three buckets of work:

- [Ad tech emissions](#computing-emissions-from-ad-tech)
- [Consumer device emissions](#calculating-consumer-device-emissions)
- [Content production](#content-production)

This model is intended to apply all digital media including web, mobile app, and CTV. DOOH should work but we have not thought through it fully. The examples below are generally built around web and need to be updated for other channels.

At the bottom of this document we list some [concerns and caveats](#caveats-complications-and-concerns).

## Visualizing the publisher model

![Visual representation of the publisher model](publisher_model.jpg)

## Computing Emissions from Ad Tech

There are three primary types of ad tech on publisher properties:

- Core delivery systems - ad serving, order management systems (OMS), and data management platforms (DMP) - are used to deliver and track the bulk of the ads delivered by a publisher
- Programmatic ad tech is used to find incremental demand for ad impressions through a real-time auction. This process generally requires synching some kind of user identification with all of the ad tech companies, driving cookie syncs and the use of a consent management platform (CMP). We represent the multi-level auction as the "ad tech graph" since all of the calls made look like a directed acyclic? graph.
- Native ad networks insert ads into the content of the page without going through the ad server. These generally also interact with the programmatic ecosystem.

When an advertiser or agency purchases an ad impression from a publisher, they generally know if the ad has been purchased directly (non-programmatically). Depending on the monetization waterfall, these impressions may interact with the core delivery systems or also with the ad tech graph. Ads purchased programmatically may operate through the ad server or be purchased from a native ad network, and the buyer may not know which thanks to the obfuscation of the programmatic ecosystem.

We model ad tech in three steps:

1. Determine the waterfall used by the publisher so we can differentiate direct buys from programmatic buys, including the number of auctions run at each stage
2. Determine the ad tech graph
3. Use the [Ad Tech Platform Model](adTechModel.md) to determine emissions for each ad tech platform

### The Monetization Waterfall

When publishers determine which ad to display to a user they generally have a priority system that can be visualized as a waterfall. First, serve a sponsorship (or guaranteed, or programmatic guaranteed) campaign if one is eligible to deliver. If not, the impression spills over to an auction where the highest value impression wins. There is often a third tranche where mediation will occur, which can be thought of as a daisy chain of ad networks. Finally, a house or public-service ad will act as a default if nothing else can deliver.

In recent years, many publishers have adopted a unified yield strategy which runs the auction process before the sponsorship phase, enabling a high bid to preempt the sponsorship from serving.

From a sustainability perspective, most of the emissions from ad tech happen during the auction phase. In the waterfall model, serving a sponsorship involves a few technology partners for the publisher (the ad server and DMP) and a few for the advertiser (their ad server and brand safety provider). In the unified yield model, every ad tech platform will engage to try to bid on the impression, making a sponsorship just as costly from an emissions perspective as a programmatic campaign.

Many web publishers run multiple auctions on a single impression. The first auction is often Prebid.js running client-side, then one or more server-side auctions like Amazon's TAM. Then the impression is passed to Google Ad Manager (GAM) which calls into its Open Bidding layer. Each of these auctions makes requests to multiple ad tech platforms (SSPs, ad networks, and/or exchanges), most of which will then make requests to other ad tech platforms.

To understand how publishers interact with ad tech platforms, we need to know how many auctions they run and how these interact with each other and with the priority in the ad server. Generally, information about the monetization waterfall is not available in ads.txt or app-ads.txt. For websites, we can scan the code of the page to see client-side auctions like Prebid.js. For apps and server-side auctions, we need to get this information from publishers or make a best guess based on typical configurations.

### Mapping the ad tech graph

We use ads.txt to understand the direct and indirect ad tech platforms in the graph. There is risk here that publishers will not put all of their vendors in the ads.txt file, and we are relying on the increased enforcement from the programmatic ecosystem to make sure that these files are correct. We also strongly recommend that buyers stop purchasing "masked" inventory where the publisher or supply chain are obfuscated.

Ads.txt file have a number of issues, including the lack of a geographic indicator. Publishers often share the same ads.txt file across multiple domains, which causes problems if each domain has a different publisher ID for a particular ad tech platform (it will look like that ATP is called multiple times on every domain, instead of once per domain). At Scope3, we have a secondary set of filters that we use to manually clean up this information, and we also work with publishers directly to make this as accurate as possible.

### Determining programmatic auctions

One challenge is understanding how many auctions a publisher operates. We can scan the code on a page to see, for instance, Prebid.js code. However, we can't tell from the client side whether a publisher is using Google Open Bidding inside of GAM, or if they are running server-side auctions through Prebid Server or Amazon's TAM.

## Calculating Consumer Device Emissions

To calculate the emissions from the consumer side of the media experience, we need to understand:

- Emissions from the device being used to consume media
- Emissions from networking between the consumer device and the edge of the internet
- Emissions to get data from the core internet to the edge
- Grid mix at the consumer location

### Consumer behavior and devices

One of the challenges we face is that advertisers generally do not know if a consumer is using a laptop or desktop. Some ad tech platforms provide data on computer vs tablet vs phone, and in the TV space, we may know whether we are working through a set-top box, smart TV, or a media gateway. However, we are unlikely to know whether the consumer is on wifi or ethernet, whether they are using a large TV or a small one, whether they have a monitor attached to their computer, and so forth.

To best understand energy use across the various parts of a media property, we would want to sample user sessions and replicate their device and behavior. At Scope3, we license a consumer panel with 5M user devices that lets us simulate this at least to some degree of accuracy.

For purposes of this open-source model, a simpler way to get the basic data about a website is to use [Pingdom](https://tools.pingdom.com), which will scan a page of a site and provide basic metrics about page size, network requests, and load time (question: does this properly bypass cookie banners? If not, it understates emissions significantly). We can combine this data with the SimilarWeb data about pages per visit to estimate the time spent actively rendering a page and the time spent reading the content.

### Measuring energy use of consumer devices

This [2019 paper](https://www.researchgate.net/publication/335911295_Residential_Consumer_Electronics_Energy_Consumption_in_the_United_States_in_2017) models the use of various consumer devices in the US in 2017. Based on the analysis, about 3.5 billion devices in 119 million homes consumed 148 TWh.

This study estimates, for instance, desktop computer + monitor as using 115W when active and 59W when idle and a laptop as using 22W active and 11W idle. We can use these data to map to the loading/browsing times calculated above.

As an example, SimilarWeb shows [BZ](https://www.similarweb.com/website/bz-berlin.de/#overview) as having 2.24 pages per visit and average visit duration of 120 seconds. [Pingdom](https://tools.pingdom.com/#60b937d3cb000000) shows a load time of 1.35 seconds. For a laptop, we would model this as 3 seconds of active use per visit at 22W plus 117 seconds of idle time for a total of 0.376Wh per visit. (TODO: this should include embodied emissions).

In the open source version, we ask for the above data as inputs into the calculation (in the `publisher.properties` object). In the Scope3 version, we operate a crawler that simulates loading multiple pages of each website and measures actual CPU and network usage, creating a weighted average of consumer device emissions for each domain.

### Assessing the carbon footprint of network traffic

As a sanity check on the total environmental impact of network infrastructure, this paper: [The electricity consumption and operational carbon emissions of ICT network operators](https://www.diva-portal.org/smash/get/diva2:1177210/FULLTEXT01.pdf) uses confidential information provided by network operators to produce an estimate of the total and per-subscriber emissions.

> - The total annual operational carbon emissions of the ICT networks are estimated to 169 Mtonnes CO2e for 2015. This corresponds to 0.53% of the global carbon emissions related to energy (about 32 Gtonnes), or 0.34% of all carbon emissions (about 50 Gtonnes).
> - The total annual operational electricity consumption of the overall ICT networks globally is estimated to 242 TWh for 2015 including both grid (215 TWh) and on-site generated electricity (27 TWh). The total corresponds to 1.15% of the total electricity grid supply.

The paper shows that electricity use and emissions per subscriber are relatively flat over the period 2010 to 2015 due to increased efficiency of the underlying technology (Moore's law), and demonstrates that electricity use and emissions are not growing proportionately to data transfer, which grew dramatically over this period.

The paper calculates emissions per fixed broadband (37 kgCO2e/sub) and mobile (14 kgCO2e/sub) subscribers, with an average of 19 kgCO2e per subscriber.

The same author, Jens Malmodin, produced a graphic showing the sources of power usage per user at the [Science & Society Forum](https://www.youtube.com/watch?v=Xo0PB5i_b4Y&t=2520s) in Sweden in 2020:
![Real power figures per user](malmodin2020.png)

These bottom-up numbers indicate that the majority of emissions from broadband users are fixed and change little based on data transfer, while mobile emissions are somewhat based upon data transfer (presumably because the access network uses energy to transmit more actively). An expansion of this analysis that compares to other assessments of emissions from network use can be found in *IEA (2020), [The carbon footprint of streaming video: fact-checking the headlines]( https://www.iea.org/commentaries/the-carbon-footprint-of-streaming-video-fact-checking-the-headlines), IEA, Paris*

For the current version, we are using a simplistic value of 0.1 kWh per GB from the [most recent peer-reviewed study](https://www.mdpi.com/2071-1050/10/7/2494) we have found to estimate emissions from data transfer. In future versions, we will distinguish mobile and fixed broadband as well as streaming vs non-streaming use cases. For mobile vs fixed data there is a great [2020 EU study](https://circabc.europa.eu/sd/a/8b7319ba-ce4f-49ea-a6e6-b28df00b20d1/ICT%20impact%20study%20final.pdf) that is more or less in line with the above numbers (0.03 kWh/GB for fixed, 0.14 kWh/GB for mobile).

### Grid mix

There are (at least) two companies that provide grid mix data for a broad range of companies and regions: [Electricity Map](https://electricitymaps.com) and [Watt Time](https://www.watttime.org). Each of these can provide data on the current and historical carbon intensity of the electricity grid. They use slightly different methodologies (Electricity Map uses average intensity; Watt Time is marginal intensity) and have different coverage areas. In both cases, it is necessary to map from grid regions to administrative regions (states and provinces) in countries like the US.

At Scope3, we subscribe to Watt Time and use their API; in this open source repo you can pass the carbon intensity into the model on the command line.

## Content Production

The final part of the publisher model is to allocate corporate overhead - representing the emissions from content production, monetization, and marketing - to each impression.

We do this by calculating corporate emissions per month and dividing by the number of ads per month.

### Calculating corporate emissions

See [Corporate Emissions](./corporate_model.md)

### Allocation of corporate emissions by channel and business model

For a digital property, we attempt to allocate only the digital ad revenue for each publisher, excluding print and other channels as well as revenue from subscriptions and affiliate programs.
(TODO)

### Allocation of corporate emissions to properties

We allocate corporate emissions to properties based on relative time spent across properties. This could also be done based on raw traffic or revenue - curious if there are any standards or best practices (or opinions!) around this.

For purposes of the open source repo, we suggest using SimilarWeb to add facts to the `properties` object for `visits_per_month` and `average_visit_duration_s`. We sum these to produce total publisher time, and then assign to each property based on property time divised by total publisher time.

### Quality ads per month

We can pull session information from SimilarWeb for each of the publisher's properties to determine the number and length of sessions for each.

To determine ads per session, Scope3 uses a crawler to detect ads per page, but we have found a number of issues with this approach:

- Ad layouts can be dramatically different on a site's home page vs internal pages
- It is difficult to trigger ads in every type of content (for instance, a mobile game may only show an incentivized ad after a certain amount of playing the game)
- Our scanner is technically a bot and should not actually see ads if ad tech companies are doing their job properly
- Infinite scroll layouts are complicated to measure accurately. How far should we scroll?
- If we divide corporate emissions by the actual number of ad slots on a page, that implies that all ads are created equal. Does a tiny ad at the bottom of a long page actually contribute equally to revenue as a very prominent ad at the top?

Instead of using the actual ads we detect, we decided to use a "quality ad load" metric that represents the maximum quality ad load that a publisher can deploy in a session. Based on consultation with some major publishers, we estimate that 20% of impressions produce 60% of revenue, and that around 5 ads per page is a reasonable ad load that can produce meaningful attention. Translating these numbers into a "quality ad load," we came up with around 1 ad per 10 seconds of session length as a default for a typical news website. A similar metric for TV might be 1 ad per 133 seconds of viewing (22 30-second ads per 49 minutes).

Future state: Get an attention measurement company to open source some attention data to compute these metrics for various channels and property types

### Sample publisher YAML
This is an example of the minimal YAML that would be passed into `./scope3methodology/cli/model_publisher_emissions.py` to produce an estimate of emissions. This does not include emissions from the ad tech supply chain.

```yaml
---
type: publisher
company: The Guardian
properties:
  - template: news_with_print
    identifier: theguardian.com
    facts:
      - visits_per_month: 359200000
        source_id: 1
      - pages_per_visit:  3.35
        source_id: 1
      - average_visit_duration_s: 290
        source_id: 1
      - page_size_mb: 3.0
        source_id: 2
      - load_time_s: 1.89
        source_id: 2
      - corporate_emissions_g_co2e_per_impression: 0.017779455902004453
        comment: Output of model Sept 20, 2022
      - revenue_allocation_to_ads_pct: 33.3
    raw_facts:
      - requests_per_page: 219
        source_id: 2
    sources:
      - id: 1
        year: 2022
        month: 7
        url: https://www.similarweb.com/website/theguardian.com/#overview
      - id: 2
        year: 2022
        month: 7
        url: https://tools.pingdom.com/#60bbdd2e2a800000
```

To compute the emissions for publisher, then run:

```sh
./scope3_methodology/cli/model_publisher_emissions.py -v [--corporateEmissionsG]  [--corporateEmissionsGPerImp] [company_file.yaml]

```

## Caveats, Complications, and Concerns

### Unified measurement across the value chain

One of the biggest challenges of trying to produce an industry standard for measuring emissions is that each participant in the value chain often has different data about a particular impression or campaign. For instance, a publisher may know the exact geographical location of a consumer from a device's GPS, but not be able to share that data with ad tech provider or advertisers due to privacy. Similarly, Google may have a deep understanding of a consumer's device if she is on Android, but have little information for consumers using Apple devices.

The risk here is that each participant will see the impression slightly differently, making it impossible to have an actionable discussion about how to make changes in buying and monetization behavior to reduce the carbon footprint of media and advertising.

Our approach has been to create statistical averages of various inputs into the model that ensure that all emissions are captured and that decisions made based on the data will have the desired effect.

For instance, a device model for a user that we know is on a personal computer of some sort. We assume that a "personal computer" is the weighted average of electricity use of a desktop (38%), laptop (62%), and monitor (52%) based on publicly-available data. By merging these together we do lose the ability to optimize a campaign to run only against laptops, which would save significant energy. However, this is not a feature available in any advertising platform that we are aware of, and even if it were, this data would not be generally available to the ecosystem at large.

### Interaction with content

When we try to replicate consumer behavior, we need to interact with the content in basic ways - scrolling, clicking to start videos, accepting (or rejecting) cookies. These are relatively complex from a technical perspective and difficult to model in context of a "typical" session. The risk here is probably that we are underestimating the CPU and network intentsity by not interacting with the content.
