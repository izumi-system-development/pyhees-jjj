import json
import os
import pandas as pd
import numpy as np

from jjjexperiment.main import calc


def test_arai():
    prefix = 'PHs046_VAV_input_CO_adjust_20250325'

    if not os.path.exists(prefix + '_output1.csv'):
        inputs = json.load(open('PHs046_VAV_input_CO_adjust_20250325_input.json', 'r'))
        result = calc(inputs, test_mode=True)


    assert 10, 10