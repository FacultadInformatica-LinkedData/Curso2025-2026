import pandas as pd
from pyproj import Proj, Transformer

# Cambia esta ruta a la de tu archivo CSV
filename = "accidentes-updated-with-links-pids.csv"

# Leer CSV
df = pd.read_csv(filename)

# Suponiendo que tus columnas UTM se llaman 'utm_x' y 'utm_y'
utm_x_col = 'utmXcoord'
utm_y_col = 'utmYcoord'

# Definir proyección UTM (zona y hemisferio)
# Por ejemplo, UTM zona 30N, cambiar según tu caso
utm_zone = 30
utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=False)
transformer = Transformer.from_proj(utm_proj, 'epsg:4326', always_xy=True)

# Crear columnas lat y long
df['long'], df['lat'] = transformer.transform(df[utm_x_col].values, df[utm_y_col].values)

# Guardar CSV con nuevas columnas
output_filename = filename.replace('.csv', '-with-latlong.csv')
df.to_csv(output_filename, index=False)

print(f"Archivo guardado en: {output_filename}")
