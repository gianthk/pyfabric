#!/bin/bash
#SBATCH --job-name=pyfabric_%j
#SBATCH --output=logs/pyfabric_%j.out
#SBATCH --error=logs/pyfabric_%j.err
#SBATCH --cpus-per-task=32
#SBATCH --mem=512G
#SBATCH --time=24:00:00

# Variables section: 
#export NUMEXPR_MAX_THREADS=10

##################################################################################
# python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_isq_to_zarr_script.py
# python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_mhd_downsample.py
python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_resample.py
