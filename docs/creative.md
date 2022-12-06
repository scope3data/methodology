# Creative

The Creative API supports multiple digital channels and formats so some specific examples are provided below for common use cases.

## Methodology

The lifecycle of a creative starts with its production. Depending on the channel and format, creative production can be very lightweight (typing a couple of lines of text into a search tool) or have a significant carbon footprint (an on-location shoot with a full crew). Currently, this project does not include modeling creative production, but we are considering this for future development.

The use phase of a creative has three areas of impact:

- The [consumer device](./consumer_devices.md) uses energy to display the creative
- Energy is used to [transfer](./data_transfer.md) the creative from a server to the device
- Various [vendors](./ad_tech_model.md) participate in the delivery and reporting of the creative.

### Consumer Device Emissions

The energy used by the consumer during the display of the creative is determined by multiplying the duration of the creative by the energy use of the consumer device.

For instance, a 30 second video ad played on a television will use 0.73 Wh of energy and an allocation of 0.63 gCO2e from the production of the television (see [consumer device methodology](./consumer_devices.md) for details on these numbers).

For a banner or native ad that does not have an inherent duration and does not generally use the full screen, we recommend assuming a 1 second duration based on the MRC viewability standard.

### Data Transfer Emissions

The payload of a creative is the number of bytes transferred to display the ad. We calculate the energy used per GB from the [data transfer methodology](./data_transfer.md) based on the network type.

As an example, a 30 second video at 500kbit/s is 0.001875 GB. On a mobile network we estimate 0.14 kWH/GB, so downloading this ad will use 0.26 Wh of energy.

### Vendor Emissions

For each vendor that participates in delivering and tracking the creative, we need to calculate the emissions per creative delivery request. This is part of the [ad tech vendor methodology](./ad_tech_model.md).

## Input parameters

| Parameter    | Values                      | Required | Comments                                                                    |
| ------------ | --------------------------- | -------- | --------------------------------------------------------------------------- |
| Payload Size | bytes                       | yes      | Bytes transferred to fully display the creative                             |
| Duration     | seconds (float)             | yes      | Used for consumer device calculation. For static creative this should be 1. |
| Impressions  | integer                     | yes      |                                                                             |
| Network Type | fixed, mobile               | yes      |                                                                             |
| Device Type  | mobile, pc, tablet, tv, ooh | yes      |                                                                             |

### Output parameters

| Parameter                 | Values |
| ------------------------- | ------ |
| Device Energy             | kWh    |
| Device Embodied Emissions | gCO2e  |
| Data Transfer Energy      | kWh    |

## Use Case: Banner Ad

| Parameter    | Values | Comments                             |
| ------------ | ------ | ------------------------------------ |
| Payload Size | 24882  | The size of the creative in bytes    |
| Duration     | 1      | Recommended value for static banners |
| Impressions  | 831211 |                                      |
| Network Type | mobile |                                      |
| Device Type  | mobile |                                      |

This will output:
| Parameter | Value | Comments |
| -- | -- | -- |
| Device Energy | 0.18 kWh | 1 x 831211 x 0.77 / 3600 / 1000 |
| Device Embodied Emissions | 4322.3 gCO2e | 1 x 831211 x 0.0052|
| Data Transfer Energy | 2.70 kWh | 0.14 x 24882 / 1024 / 1024 / 1024 \* 831211 |

At 390 g/kWh, this creative execution would generate 5.4 kg of CO2e.

## Use Case: Video ad on CTV

| Parameter    | Value   | Comments        |
| ------------ | ------- | --------------- |
| Payload Size | 1875000 | 500kbit/s x 30s |
| Duration     | 30      |                 |
| Impressions  | 831211  |                 |
| Network Type | fixed   |                 |
| Device Type  | tv      |                 |

This will output:

| Parameter                 | Value          | Comments                                      |
| ------------------------- | -------------- | --------------------------------------------- |
| Device Energy             | 605.4 kWh      | 30 x 831211 x 87.4 / 3600 / 1000              |
| Device Embodied Emissions | 523662.9 gCO2e | 30 x 831211 x 0.021                           |
| Data Transfer Energy      | 43.5 kWh       | 0.03 x 1875000 / 1024 / 1024 / 1024 \* 831211 |

At 390 g/kWh, this creative execution would generate 777 kg of CO2e.
