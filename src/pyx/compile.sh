#!/bin/bash

python state_state.py build_ext --inplace
python state_legalmoves.py build_ext --inplace
python state_evaluator.py build_ext --inplace
