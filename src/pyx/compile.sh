#!/bin/bash

python setup_state.py build_ext --inplace
python setup_legalmoves.py build_ext --inplace
python setup_evaluator.py build_ext --inplace

mv *.so ../py
