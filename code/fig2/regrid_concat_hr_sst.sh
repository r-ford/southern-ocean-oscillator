#!/bin/bash -l
#PBS -N rc_sst
#PBS -A XXXX####
#PBS -l select=1:ncpus=1:mem=10GB
#PBS -l walltime=4:00:00
#PBS -q casper
#PBS -j oe

module load nco
module load esmf

INPUT_DIR="/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1"
TEMP_DIR="/glade/derecho/scratch/rford2/tmp"
REGRID_DIR="/glade/derecho/scratch/rford2/ihesp-regrid/HR-SST/monthly"
OUTPUT_FILE="/glade/derecho/scratch/rford2/ihesp-regrid/HR-SST/iHESP-HR.PICTRL.SST.1x1.150-520.nc"
GRID_MAP="/glade/u/home/rford2/ihesp/regridding_files_scripts/map_t12_to_1x1_conserve.nc"  # Precomputed regridding map

mkdir -p "$TEMP_DIR" "$REGRID_DIR"

for file in "$INPUT_DIR"/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.TEMP.*.nc; do
    filename=$(basename "$file" .nc)

    echo "Selecting surface level of $filename"
    surface_file="$TEMP_DIR/${filename}_surface.nc"
    ncks -v TEMP -d z_t,0 "$file" "$surface_file"

    echo "Regridding $filename"
    regrid_file="$REGRID_DIR/${filename}_surface_1x1.nc"
    ncremap -m "$GRID_MAP" -i "$surface_file" -o "$regrid_file"

    echo "Removing original surface file $surface_file"
    rm -f "$surface_file"
done

echo "Done regridding. Concatenating regridded files..."
ncrcat "$REGRID_DIR"/*.nc "$OUTPUT_FILE"

# rm -rf "$REGRID_DIR"

echo "Done. Output file: $OUTPUT_FILE"
