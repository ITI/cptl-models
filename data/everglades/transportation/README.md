## Port Everglades, South Port Container Operations, May 2017
##### Gabe Weaver, March 24, 2019

### Overview
This is a scenario for South Port container operations in Port
Everglades, FL for May, 2017.  We only look at imports.

### Files
#### Transportation Network (`network-baseline.extended.json`)
We have extended the transportation network with per-container 
origin and destination nodes.  These have been geocoded using a 
GeoPy library.

#### Schedule (`schedule.json`)
We only consider vessels that go to South Port.
In May, around 8% of the vessels don't have a match.

#### Shipments (`shipments/*.json`)
The start date was chosen based on minimizing the discrepancy between
containers billed and the PIERS census data.  It is advised to round
up the number of TEU in each element in the 'commodities' dictionary.

In addition, origin/destination pairs for containers are based on an
empirical distribution of per-commodity group origin/destination pairs
from the PIERS dataset.  In the future, we can improve this assignment
by possibly conditioning on the vessel route.

### Schema (`schema/*.json`)
These files have been generated from data sources and some minor
changes to the schema have been made.  Generated files have been
validated against this modified schema prior to writing to file.

1.  `network.schema.v2.json`:  added additional 'Goods' category to cargo_categories
2.  `schedule.schema.v2.json`:  converted type of 'time' from number
to string.  Really this should be a regexp
3.  `shipment.schema.v2.json`: changed EAT/LDT from number to
     string. Allowed for empty commodities list as well.
