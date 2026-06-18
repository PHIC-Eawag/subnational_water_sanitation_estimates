# Mapping access to basic sanitation and open defecation across low- and middle-income countries


## Overview

This repository contains code for modelling access to basic sanitation and open defecation 
at subnational level in low- and middle-income coutries using survey and geospatial data. The project builds on methods 
developed in earlier work on subnational mapping of safely managed drinking water
services in low- and middle-income countries (Greenwood et al. 2024). 


## Getting started
## Setting up the project environment

This repository uses **`renv`** to manage R packages and **`venv`** to manage Python packages. 
Using both helps keep the computational environment reproducible across users and systems.

After cloning the repository, open the project from the repository root in **Positron** or **RStudio**. 
Restore the R environment with:

renv::restore()

Then create a Python virtual environment in the project directory:
python -m venv .venv

Activate the environment and install the required Python packages from the dependency file used in 
this repository by running pip install -r requirements.txt.

In Positron or RStudio, make sure the interpreter is set 
to the project-specific Python environment and that R uses the restored renv library.

## Project folder overview
