#!/bin/bash

#
# Iterate through and generate visualizations for all commodity codes
# 
# Generate case for individual codes
#
# - Make sure networks/csv directory in place
# - 
#

EXPERIMENT_NAME=nolhDisrupted

generateVisualizations(){
    code=$1
    export NAICS_CODE=$code
    export HS_PREFIX=hs$code
    #make gen-flowmovie
    #make gen-dashboard
    #make gen-teu_durations
    #make gen-teu_counts
    #make gen-lateness_hist
    make gen-delay_costs.sim
    make gen-delay_costs.opt
}

rm -rf ~/$EXPERIMENT_NAME-viz
mkdir ~/$EXPERIMENT_NAME-viz

for expId in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17;
do
    EXP_DIR=build/$EXPERIMENT_NAME/PEV-SouthPortImports.FY2018_10_8_nolhBaseline_0_nolhDisrupted$expId
    EXP_RESULTS_DIR=~/$EXPERIMENT_NAME-viz/exp$expId
    
    cd config
    rm makeParams    
    ln -s makeParams.onfdesExp$expId.txt makeParams
    cd ..

    rm -rf $EXP_DIR/results
    mkdir -p $EXP_DIR/results
    
    # Run the required tasks to do the 
    make simulate
    make optimize.opt
    #make postprocess.econ
    make init-measurements measurements

    # Generate visualizations for opt
    mkdir -p $EXP_DIR/results/vizs
    for code in all;
    do
	generateVisualizations $code
	mv $EXP_DIR/results/*.png $EXP_DIR/results/vizs
	#mv $EXP_DIR/results/*.mp4 $EXP_DIR/results/opt-viz
    done

    # Switch over
    #mv $EXP_DIR/results/output.opt.sqlite $EXP_DIR/results/output.opt-true.sqlite
    #cp $EXP_DIR/results/output.sqlite $EXP_DIR/results/output.opt.sqlite
    #make postprocess.econ
    
    # Generate visualizations for sim
    #mkdir -p $EXP_DIR/results/sim-viz
    #for code in all;
    #do
    #	generateVisualizations $code
    #	mv $EXP_DIR/results/*.png $EXP_DIR/results/sim-viz
	#mv $EXP_DIR/results/*.mp4 $EXP_DIR/results/sim-viz
    #done
    #mv $EXP_DIR/results/output.opt.sqlite $EXP_DIR/results/output.sqlite
    #mv $EXP_DIR/results/output.opt-true.sqlite $EXP_DIR/results/output.opt.sqlite
    
    # TARBALL VISUALIZATIONS
    mkdir $EXP_RESULTS_DIR
    cp -rf $EXP_DIR/results/vizs $EXP_RESULTS_DIR
    #cp -rf $EXP_DIR/results/ $EXP_RESULTS_DIR    
done

tar -czvf $EXPERIMENT_NAME-viz55.tar.gz ~/$EXPERIMENT_NAME-viz
