#!/bin/bash
#SBATCH --job-name=pyfabric_%j
#SBATCH --output=logs/pyfabric_%j.out
#SBATCH --error=logs/pyfabric_%j.err
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=3:00:00

# Variables section: 
#export NUMEXPR_MAX_THREADS=10

export PYTHONUNBUFFERED=1
export LD_LIBRARY_PATH=/home/giiori/myterminus/software/elastix5.1/lib:$LD_LIBRARY_PATH

##################################################################################
# python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_isq_to_zarr_script.py
# python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_mhd_downsample.py
# python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_resample.py

python /home/giiori/myterminus/code/pyfabric/scripts/3Dregister_QCTdata.py
