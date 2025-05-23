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
python /usr/terminus/data-xrm-01/stamplab/users/mwahlin/2025/trab_master/CT_pipeline/pyfabric/scripts/supertrab_isq_load.py