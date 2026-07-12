import numpy as np
import scipy.stats as stats
import pandas as pd
import warnings
import re
from distfit import distfit
import matplotlib.pyplot as plt
import statistics


warnings.filterwarnings('ignore')


def read_float_file(file_path):

    float_data = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            clean_line = line.strip()
            if not clean_line:
                continue
            try:
                num = float(clean_line)
                float_data.append(num)
            except ValueError:
                print(f"{line_num} '{clean_line}' wrong")
    mean_1d = np.mean(float_data)  
    std_sample_1d = np.std(float_data, ddof=1)  
    print(f"{mean_1d}")
    print(f"{std_sample_1d}")
    return float_data
    
def clean_data(raw_data, iqr_threshold=1.5):

    log = []
    raw_len = len(raw_data)
    log.append(f"{raw_len}")

    data = np.array(raw_data, dtype=np.float64)
    data = data[np.isfinite(data)]  
    log.append(f" {len(data)}")

    data = data[data >= 0]
    log.append(f" {len(data)}")


    if len(data) >= 4:  
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - iqr_threshold * IQR
        upper_bound = Q3 + iqr_threshold * IQR
        data = data[(data >= lower_bound) & (data <= upper_bound)]
        log.append(f" {len(data)}")
        log.append(f"[{lower_bound:.2f}, {upper_bound:.2f}]")
    else:
        log.append("wrong")

    clean_len = len(data)
    mean_1d = np.mean(data)  
    std_sample_1d = np.std(data, ddof=1)  
    print(f"mean: {mean_1d}")
    print(f"std: {std_sample_1d}")
    log.append(f"{clean_len}，{clean_len/raw_len:.2%}")
    log.append("="*50)

    return data, log


def main(file_path):

    cleaned_data = read_float_file(file_path)

    X = np.array(cleaned_data)
    dfit = distfit(distr=['norm', 't', 'genextreme', 'gamma', 'lognorm', 'beta', 'loggamma'], n_boots=100, stats='ks')

    dfit.fit_transform(X)
    print("The best distribution :")
    print(dfit.model)



if __name__ == "__main__":
    FILE_PATH = "th.txt"
    main(FILE_PATH)
    