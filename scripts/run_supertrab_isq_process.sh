#!/bin/bash
#SBATCH --job-name=pyfabric_%j
#SBATCH --output=logs\pyfabric_%j.out
#SBATCH --error=logs\pyfabric_%j.err
#SBATCH --cpus-per-task=32
#SBATCH --mem=700G
#SBATCH --time=1:00:00

# Variables section: 
#export NUMEXPR_MAX_THREADS=10

##################################################################################
python /home/giiori/myterminus/code/pyfabric/scripts/supertrab_isq_load.py