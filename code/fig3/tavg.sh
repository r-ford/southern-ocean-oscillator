#!/bin/bash -l
#PBS -N tavg
#PBS -A XXXX####
#PBS -j oe
#PBS -k oe 
#PBS -q main@desched1
#PBS -l walltime=8:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

module load nco/5.3.1

INPUT_DIR="/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1"
TEMP_DIR="/glade/derecho/scratch/rford2/ihesp-regrid/tmp"
SAVE_DIR="/glade/u/home/rford2/ihesp"

VARS=("XMXL")

for VAR in "${VARS[@]}"; do
    ncra ${INPUT_DIR}/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.${VAR}.*.nc \
         ${SAVE_DIR}/HRCESM_${VAR}_timeavg.nc
done
