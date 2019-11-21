# Converts csv to parquet for more efficient processing
import dask.dataframe as dd

df = dd.read_csv("tweets.csv", engine="python", encoding="utf-8", error_bad_lines=False)
df.to_parquet("tweets.parquet", engine="pyarrow")
