# Mapping access to basic sanitation and open defecation across low- and middle-income countries


## Overview

This repository contains code for modelling access to basic sanitation and open defecation 
at subnational level in low- and middle-income coutries using survey and geospatial data. The project builds on methods 
developed in earlier work on subnational mapping of safely managed drinking water
services in low- and middle-income countries (Greenwood et al. 2024). 

## Scope

The repository currently includes:

- project setup files
- data cleaning scripts
- reusable helper functions


Later stages of the workflow, such as feature selection, modelling, prediction, 
and additional analysis, will be added in future.

## Repository structure

```text
project/
├── README.md
├── LICENSE
├── .gitignore
│
├── project.Rproj
├── renv.lock
├── config/
│   ├── data_sources.yml
│   ├── paths.yml
│
├── data/
│   ├── processed/
│   └── reference/
│
├── scripts/
│   └── 01_data_cleaning/
│       ├── 01_compile_survey_data.R
│       ├── 02_create_service_indicators.R
│       ├── 03_describe_training_and_test_sets.R
│       ├── 04_match_survey_regions_to_boundaries.R
│       └── 05_sampling_geospatial_data.ipynb
│
│   ├── 02_feature_selection/
│   ├── 03_model_training/
│   ├── 04_prediction/
│   └── 05_additional_analysis/
│
├── functions/
│   ├── R/
│   │   ├── extract_mics_variables.R
│   │   ├── label_mics_variables.R
│   │   ├── join_and_structure_dataframes.R
│   │   └── create_service_indicators.R
│   └── python/
│       └── aggregate_environmental_samples.py
│
└── outputs/
    └── data_cleaning/

## Getting started

Create virtual environment
Then run:

pip install -r requirements.txt