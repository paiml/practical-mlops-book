from os import path
import sys
import pandas as pd

argument = sys.argv[-1]

try:
    df = pd.read_csv(argument)
    print(df.describe())
except Exception as error:
    print(f"Had a problem trying to read the CSV file: {error}")
