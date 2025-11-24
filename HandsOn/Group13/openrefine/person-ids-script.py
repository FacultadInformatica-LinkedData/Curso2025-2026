# Group13. Code to create person ids for each accident, this way we can create a better URI. We executed this in google colab after json changes. 
# So the route to create the final csv is: accidentes-updated.csv -> apply accidents-with-links.json -> execute accidents-with-links-script.py (this script) -> we got accidentes-updated-with-links
import pandas as pd

filename = "/content/accidentes-updated-with-links.csv"
df = pd.read_csv(filename)

df = df.sort_values(['expID', 'date'])
df['person_id'] = df.groupby('expID').cumcount() + 1

output_filename = filename.replace('.csv', '-pids.csv')
df.to_csv(output_filename, index=False)