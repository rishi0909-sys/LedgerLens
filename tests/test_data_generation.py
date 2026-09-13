import os
import shutil
import pytest
from backend.data_generation.generator import generate_synthetic_data
import pandas as pd

def test_reproducibility():
    dir1 = "data/test_run_1"
    dir2 = "data/test_run_2"
    
    generate_synthetic_data(42, 5, 20, 10, 100, 20, 10, dir1)
    generate_synthetic_data(42, 5, 20, 10, 100, 20, 10, dir2)
    
    df1 = pd.read_parquet(os.path.join(dir1, "transactions.parquet"))
    df2 = pd.read_parquet(os.path.join(dir2, "transactions.parquet"))
    
    # Check if dataframes are exactly equal
    pd.testing.assert_frame_equal(df1, df2)
    
    # Cleanup
    shutil.rmtree(dir1)
    shutil.rmtree(dir2)
