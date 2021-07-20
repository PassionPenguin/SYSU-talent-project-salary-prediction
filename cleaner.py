import pandas as pd

df = pd.read_csv('jobs.csv')
print("Duplicated Count:"+str(df.duplicated().sum()))
df.drop_duplicates().to_csv("jobs.csv")