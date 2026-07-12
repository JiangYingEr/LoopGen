from scipy.stats import norm
import numpy as np
import math



x1 = (2*0.0000252 + 0.0007) / math.sqrt(2*pow(0.00000136,2) + 2*pow(0.0075,2) + pow(0.000039,2) )
cdf_1 = norm.cdf(x1)  
print(f"Standard normal distribution P(X ≤ {x1}) = {cdf_1:.4f}")  

