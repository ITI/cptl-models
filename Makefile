.DEFAULT_GOAL := help

export DES_HOME=/home/share/des
export PYTHONPATH=$(DES_HOME)/src:./src
export SCENARIO_REPO_HOME=/home/share/Code/cptl-models/build

export PORT=PEV
export YEAR=FY2018
export MONTH=10
export DESC=SouthPortImports
export SIM_DURATION_DAYS=2

export SCENARIO_REF=$(PORT)-$(DESC).$(YEAR)_$(MONTH)_$(SIM_DURATION_DAYS)
export SCENARIO_DIR=$(SCENARIO_REPO_HOME)/$(SCENARIO_REF)
export SIM_DURATION=$$(( $(SIM_DURATION_DAYS) * 1440 ))
export SIM_RUN_TIME=$$(( $(SIM_DURATION) + 5000 ))

help: help-core

include src/Makefile.econ
include src/Makefile.expdesign

help-core:
	@echo "-----------------------------------------------------------------------------------------"
	@echo "______          _    ______ _                      _   _               _____           _"
	@echo "| ___ \        | |   |  _  (_)                    | | (_)             |_   _|         | |"
	@echo "| |_/ /__  _ __| |_  | | | |_ ___ _ __ _   _ _ __ | |_ _  ___  _ __     | | ___   ___ | |"
	@echo "|  __/ _ \| '__| __| | | | | / __| '__| | | | '_ \| __| |/ _ \| '_ \    | |/ _ \ / _ \| |"
	@echo "| | | (_) | |  | |_  | |/ /| \__ \ |  | |_| | |_) | |_| | (_) | | | |   | | (_) | (_) | |"
	@echo "\_|  \___/|_|   \__| |___/ |_|___/_|   \__,_| .__/ \__|_|\___/|_| |_|   \_/\___/ \___/|_|"
	@echo "                                            | |"
	@echo "                                            |_|"
	@echo "-----------------------------------------------------------------------------------------"
	@echo "PDT CORE"
	@echo "-----------------------------------------------------------------------------------------"
	@echo "clean                  Clean build"
	@echo "init                   Initialize scenario for month"
	@echo "describe-corpus        Get data corpus for scenario"
	@echo "describe-scenario      Get scenario parameters"
	@echo "generate               Generate scenario from data"
	@echo "simulate               Run the simulation for scenario"
	@echo "calibration            Get calibration report for scenario"
	@echo "describe-calibration   Get calibration results"
	@echo "-----------------------------------------------------------------------------------------"
	@echo "PDT Extension Modules"
	@echo "-----------------------------------------------------------------------------------------"
	@echo "help.econ              PDT Economic Analysis"
	@echo "help.expdesign         PDT Experiment Design"
	@echo "-----------------------------------------------------------------------------------------"

clean:	## remove build artifacts
	rm -fr $(SCENARIO_DIR)

init: init-base init-config init-data init-flows init-network init-results

init-base:
	mkdir $(SCENARIO_DIR)	

init-config: ## initialize the artifacts
	mkdir $(SCENARIO_DIR)/config
	cp config/pdt_units.txt $(SCENARIO_DIR)/config
	cp config/inventory.json $(SCENARIO_DIR)/config

init-data:  # initialize the data dir
	mkdir $(SCENARIO_DIR)/data
	cp data/HS\ Codes.csv $(SCENARIO_DIR)/data
	cp data/$(PORT)-$(YEAR)/TEU\ Report.csv $(SCENARIO_DIR)/data
	cp -rf data/$(PORT)-$(YEAR)/$(MONTH)/* $(SCENARIO_DIR)/data

init-network:  #initialize the network dir
	mkdir $(SCENARIO_DIR)/networks
	cp data/$(PORT)-$(YEAR)/transportation.gnsi $(SCENARIO_DIR)/networks

init-flows: # initialize the flows dir
	mkdir $(SCENARIO_DIR)/flows

init-results: # initialize the results dir
	mkdir $(SCENARIO_DIR)/results

describe-corpus:
	cat   $(SCENARIO_DIR)/config/inventory.json

describe-scenario:
	@echo "---------------------------------------------------------------"
	@echo "Scenario Description"
	@echo "---------------------------------------------------------------"
	@echo "Port: 				$(PORT)"
	@echo "Year: 				$(YEAR)"
	@echo "Month: 				$(MONTH)"
	@echo "Ref:   				$(SCENARIO_REF)"
	@echo "Simulation Duration:		$(SIM_DURATION_DAYS) days"
	@echo "---------------------------------------------------------------"

generate: generate-schedules generate-shipments

generate-schedules:  
	python3 src/bin/generateVesselSchedule.py $(SCENARIO_DIR) $(MONTH)
	python3 src/bin/filterSchedule.py $(SCENARIO_DIR) 0 $(SIM_DURATION)

generate-shipments:  
	python3 src/bin/generateVesselShipments.py $(SCENARIO_DIR) $(MONTH)
	python3 src/bin/filterShipments.py $(SCENARIO_DIR) 

simulate: 
	$(DES_HOME)/src/multiCommodityNetworkSim.py -o $(SCENARIO_DIR)/results/output.sqlite -t $(SIM_RUN_TIME) -si 100 -s $(SCENARIO_DIR)/flows/schedule.json

calibration:
	python ./src/bin/calibrationReporter.py $(SCENARIO_DIR) $(MONTH) $(SIM_DURATION_DAYS)

describe-calibration:
	cat $(SCENARIO_DIR)/results/calibration.log




