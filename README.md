# Overview

This is a repository that contains the SWMM model for the Newport area

## Things to change
 - In file `Newport_Baseline_WithLID_20190418.inp`, the paths need to be changed. This starts on line `13077`
 - In file `scripts.py`, the path on line `8` needs to be changed

## Output directory
 - Files in the `./Output/Original` directory are simulation results for the original water quality data with data from 01/02/2010 and 01/03/2010 wiped
 - Files in the `./Output/Modified` directory are simulation results for the water quality data wiped from 01/02/2010 and 01/03/2010 and pollutants doubled for input files `./WaterQualityFiles/IRVF05P07_Cu.dat` and `./WaterQualityFiles/IRVF05P07_EColi.dat` on 01/01/2010
 - Files in the `./Output/Diff` directory list the nodes that were affected above a certain threshold and the first time at which the change was detected
 - The `location.csv` file shows the randomly generated input files that should be altered
