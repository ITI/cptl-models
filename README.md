# cptl-models
CPTL Models

## Scenario Server
The scenario server provides a REST webservice for critical infrastructure networks and flows.

### Installation
1.  virtualenv -p python3 cptl-models.venv
2.  source cptl-models.venv/bin/activate
3.  pip install -r requirements.txt (not tested)
4.  export PTYHONPATH=`pwd`/src
5.  ant startServer

### Example Queries

1.  Get a list of scenarios
`curl http://localhost:1336/cptl/api/v0.1/scenarios`

2.  Retrieve a particular scenario (infrastructure networks and flows)
`curl http://localhost:1336/cptl/api/v0.1/scenarios/pevtest-v1`

3.  Retrieve a particular network.  
`curl http://localhost:1336/cptl/api/v0.1/scenarios/pevtest-v1/networks/trans-southport-v1`

4.  Retrieve a flow archive (TBD)
`curl http://localhost:1336/cptl/api/v0.1/scenarios/pevtest-v1/flows/<flow_id>`

## TODO
1.  Validate results against schema
2.  Allow for POST
3.  Download ZIP for flows

