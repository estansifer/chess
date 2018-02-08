#!/bin/bash

python state_setup.py build_ext --inplace
python legalmoves_setup.py build_ext --inplace
python evaluator_setup.py build_ext --inplace
