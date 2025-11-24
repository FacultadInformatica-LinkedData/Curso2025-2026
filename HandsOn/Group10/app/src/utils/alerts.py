def classify_alert(magnitud, valor):
    if magnitud == "8":  # NO2
        if valor >= 200:
            return "🔴 MUY ALTO"
        elif valor >= 100:
            return "🟠 ALTO"
        else:
            return "🟢 BUENO"

    if magnitud == "12":  # O3
        if valor >= 180:
            return "🔴 MUY ALTO"
        elif valor >= 120:
            return "🟠 PRECAUCIÓN"
        else:
            return "🟢 BUENO"

    if magnitud == "9":  # PM10
        if valor >= 50:
            return "🔴 MALO"
        else:
            return "🟢 BUENO"

    return "⚪ SIN DATOS"
