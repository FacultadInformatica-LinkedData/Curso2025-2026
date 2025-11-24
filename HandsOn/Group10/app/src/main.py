from queries.internal import get_measurements, get_measurements_by_station_and_date, get_ozone_episodes, get_measurements_with_linked_data, get_aggregated_statistics

def main():
    # print("=" * 80)
    # print("PRUEBA 1: Mediciones básicas (primeras 10)")
    # print("=" * 80)
    # data = get_measurements()
    # for d in data[:10]:
    #     print(d)
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 2: Filtrar por estación '11'")
    # print("=" * 80)
    # data_by_station = get_measurements_by_station_and_date(estacion="11")
    # print(f"Total de mediciones encontradas: {len(data_by_station)}")
    # for d in data_by_station[:3]:
    #     print(f"\nEstación: {d['estacion']}, Fecha: {d['fecha']}, Magnitud: {d['magnitud']}")
    #     print(f"  Punto Muestreo: {d['puntoMuestreo']}")
    #     # Mostrar solo primeras 6 horas para no saturar
    #     print(f"  H01-H06: {d['H01']}, {d['H02']}, {d['H03']}, {d['H04']}, {d['H05']}, {d['H06']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 3: Filtrar por fecha específica") #Si no esta la fecha dentro del dataset devuelve 0
    # print("=" * 80)
    # data_by_date = get_measurements_by_station_and_date(fecha="2025-05-08T00:00:00Z")
    # print(f"Total de mediciones encontradas: {len(data_by_date)}")
    # for d in data_by_date[:3]:
    #     print(f"\nEstación: {d['estacion']}, Fecha: {d['fecha']}, Magnitud: {d['magnitud']}")
    #     print(f"  H01-H06: {d['H01']}, {d['H02']}, {d['H03']}, {d['H04']}, {d['H05']}, {d['H06']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 4: Filtrar por estación Y fecha")
    # print("=" * 80)
    # data_combined = get_measurements_by_station_and_date(estacion="8", fecha="2025-05-08T00:00:00Z") # Si fecha o estación no estan en el dataset devuelve 0
    # print(f"Total de mediciones encontradas: {len(data_combined)}")
    # for d in data_combined:
    #     print(f"\nEstación: {d['estacion']}, Fecha: {d['fecha']}, Magnitud: {d['magnitud']}")
    #     print(f"  Todas las horas disponibles:")
    #     horas = [f"H{i:02d}: {d[f'H{i:02d}']}" for i in range(1, 25) if d[f'H{i:02d}'] is not None]
    #     print(f"  {', '.join(horas[:12])}")  # Primera mitad del día
    #     print(f"  {', '.join(horas[12:])}")  # Segunda mitad del día
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 5: Episodios de ozono (todos)")
    # print("=" * 80)
    # ozone_episodes = get_ozone_episodes()
    # print(f"Total de episodios encontrados: {len(ozone_episodes)}")
    # for ep in ozone_episodes:
    #     print(f"\n Fecha inicio: {ep['fecha_inicio']}")
    #     print(f" Fecha fin: {ep['fecha_fin']}")
    #     print(f"  Escenario: {ep['escenario']}")
    #     print(f"  Medida población: {ep['medida_poblacion']}")
    #     print(f"  URI: {ep['episodio_uri']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 6: Episodios de ozono filtrados por fecha")
    # print("=" * 80)
    # ozone_filtered = get_ozone_episodes(fecha_inicio="2025-05-08T00:00:00Z")
    # print(f"Total de episodios desde 2025-05-08: {len(ozone_filtered)}")
    # for ep in ozone_filtered:
    #     print(f"\n {ep['fecha_inicio']} → {ep['fecha_fin']}")
    #     print(f"  {ep['escenario']}")
    #     print(f"  {ep['medida_poblacion']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 7: Mediciones con Linked Data (owl:sameAs) - Primeras 10")
    # print("=" * 80)
    # ## Salen datos con la misma URI para Wikidata, habria que mirar reconcilacion con otra propiedad
    # ## Magnitud 12 (NO₂) → debería enlazar a Wikidata de dióxido de nitrógeno
    # ## Magnitud 20 (SO₂) → debería enlazar a Wikidata de dióxido de azufre
    # ## Magnitud 7 (O₃) → debería enlazar a Wikidata de ozono
    # ## Magnitud 10 (partículas) → debería enlazar a Wikidata de material particulado
    # ## etc.
    # linked_data = get_measurements_with_linked_data(limit=10)
    # print(f"Total de mediciones con enlaces: {len(linked_data)}")
    # for ld in linked_data:
    #     print(f"\nEstación: {ld['estacion']}, Fecha: {ld['fecha']}, Magnitud: {ld['magnitud']}")
    #     print(f"  Punto Muestreo: {ld['punto_muestreo']}")
    #     print(f"  Enlace Wikidata: {ld['enlace_wikidata']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 8: Linked Data filtrado por estación '36'")
    # print("=" * 80)
    # linked_station = get_measurements_with_linked_data(estacion="36", limit=5)
    # print(f"Total de mediciones de estación 36 con enlaces: {len(linked_station)}")
    # for ld in linked_station:
    #     print(f"\nFecha: {ld['fecha']}, Magnitud: {ld['magnitud']}")
    #     print(f"  URI local: {ld['medicion_uri']}")
    #     print(f"  URI Wikidata: {ld['enlace_wikidata']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 9: Estadísticas Agregadas (todas)")
    # print("=" * 80)
    # stats = get_aggregated_statistics()
    # print(f"Total de agrupaciones: {len(stats)}")
    # for s in stats[:10]:  # Mostrar primeras 10
    #     print(f"\nEstación: {s['estacion']}, Magnitud: {s['magnitud']}")
    #     print(f"  Total mediciones: {s['total_mediciones']}")
    #     print(f"  Promedio: {s['promedio']}")
    #     print(f"  Máximo: {s['maximo']}")
    #     print(f"  Mínimo: {s['minimo']}")
    
    # print("\n" + "=" * 80)
    # print("PRUEBA 10: Estadísticas Agregadas por estación '11'")
    # print("=" * 80)
    # stats_11 = get_aggregated_statistics(estacion="11")
    # print(f"Total de magnitudes en estación 11: {len(stats_11)}")
    # for s in stats_11:
    #     print(f"\nMagnitud: {s['magnitud']}")
    #     print(f"  Total mediciones: {s['total_mediciones']}")
    #     print(f"  Promedio: {s['promedio']}")
    #     print(f"  Máximo: {s['maximo']}")
    #     print(f"  Mínimo: {s['minimo']}")

# Si se descomenta alguna de las pruebas hay que quitar el tab de la siguiente línea, si no da error
    if __name__ == "__main__":
        main()
