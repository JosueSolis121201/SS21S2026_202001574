import pandas as pd
import numpy as np
import warnings


# ==========================================
# CONFIGURACION DE ARCHIVOS
# ==========================================
INPUT_CSV_PATH = "dataset_vuelos_crudo.csv"
OUTPUT_CSV_PATH = "dataset_vuelos_limpio.csv"


def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA})
        .str.upper()
    )


def parse_mixed_datetime(series: pd.Series) -> pd.Series:
    base = series.astype("string").str.strip()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        dt_dayfirst = pd.to_datetime(base, errors="coerce", dayfirst=True)
        dt_monthfirst = pd.to_datetime(base, errors="coerce", dayfirst=False)
    return dt_dayfirst.fillna(dt_monthfirst)


def parse_number(series: pd.Series) -> pd.Series:
    def _normalize_numeric_string(value: str) -> str:
        s = str(value).strip()
        s = "".join(ch for ch in s if ch in "0123456789,.-")

        has_dot = "." in s
        has_comma = "," in s

        if has_dot and has_comma:
            if s.rfind(",") > s.rfind("."):
                # Formato tipo 1.234,56 -> 1234.56
                s = s.replace(".", "").replace(",", ".")
            else:
                # Formato tipo 1,234.56 -> 1234.56
                s = s.replace(",", "")
        elif has_comma:
            # Formato tipo 77,60 -> 77.60
            s = s.replace(",", ".")

        return s

    cleaned = series.astype("string").map(_normalize_numeric_string)
    return pd.to_numeric(cleaned, errors="coerce")


print("1. Extraccion: cargando CSV...")
df = pd.read_csv(INPUT_CSV_PATH, dtype=str)

# ==========================================
# VALIDACION DE COLUMNAS MINIMAS
# ==========================================
required_cols = {
    "airline_code",
    "airline_name",
    "flight_number",
    "origin_airport",
    "destination_airport",
    "departure_datetime",
    "duration_min",
    "status",
    "delay_min",
    "cabin_class",
    "passenger_id",
    "passenger_gender",
    "passenger_age",
    "passenger_nationality",
    "sales_channel",
    "payment_method",
    "ticket_price_usd_est",
    "bags_total",
    "bags_checked",
}

missing_cols = sorted(required_cols - set(df.columns))
if missing_cols:
    raise ValueError(f"Columnas faltantes en CSV: {missing_cols}")


print("2. Transformacion: limpieza, estandarizacion y deduplicacion...")

# Estandariza texto
text_cols = [
    "airline_code",
    "airline_name",
    "flight_number",
    "origin_airport",
    "destination_airport",
    "status",
    "cabin_class",
    "sales_channel",
    "payment_method",
    "passenger_id",
    "passenger_gender",
    "passenger_nationality",
]

for col in text_cols:
    df[col] = normalize_text(df[col])

# Normaliza genero
df["passenger_gender"] = df["passenger_gender"].replace(
    {
        "MASCULINO": "M",
        "HOMBRE": "M",
        "FEMENINO": "F",
        "MUJER": "F",
        "MALE": "M",
        "FEMALE": "F",
    }
)
df.loc[~df["passenger_gender"].isin(["M", "F", "X"]), "passenger_gender"] = "X"

# Normaliza estado
df["status"] = df["status"].replace(
    {
        "ON TIME": "ON_TIME",
        "ONTIME": "ON_TIME",
        "DELAY": "DELAYED",
    }
)

# Fechas mixtas
df["departure_datetime"] = parse_mixed_datetime(df["departure_datetime"])
if "arrival_datetime" in df.columns:
    df["arrival_datetime"] = parse_mixed_datetime(df["arrival_datetime"])
if "booking_datetime" in df.columns:
    df["booking_datetime"] = parse_mixed_datetime(df["booking_datetime"])

df["fecha_dt"] = df["departure_datetime"].dt.date

# Convierte numericos robustamente
numeric_cols = [
    "duration_min",
    "delay_min",
    "ticket_price_usd_est",
    "passenger_age",
    "bags_total",
    "bags_checked",
]
for col in numeric_cols:
    df[col] = parse_number(df[col])

# Rango y consistencia de datos
df["delay_min"] = df["delay_min"].fillna(0).clip(lower=0)
df["duration_min"] = df["duration_min"].clip(lower=1)
df["passenger_age"] = df["passenger_age"].clip(lower=0, upper=120)
df["bags_total"] = df["bags_total"].fillna(0).clip(lower=0)
df["bags_checked"] = df["bags_checked"].fillna(0).clip(lower=0)
df["bags_checked"] = np.minimum(df["bags_checked"], df["bags_total"])
df["ticket_price_usd_est"] = df["ticket_price_usd_est"].clip(lower=0)

# Filtra registros invalidos para el hecho
df = df.dropna(
    subset=[
        "passenger_id",
        "airline_code",
        "origin_airport",
        "destination_airport",
        "departure_datetime",
        "flight_number",
    ]
)

# Solo codigos IATA de 3 letras
df = df[
    df["origin_airport"].str.fullmatch(r"[A-Z]{3}", na=False)
    & df["destination_airport"].str.fullmatch(r"[A-Z]{3}", na=False)
]

# Deduplicacion de eventos de vuelo
dedupe_keys = ["passenger_id", "flight_number", "departure_datetime", "origin_airport", "destination_airport"]
df = df.sort_values(by=["departure_datetime"]).drop_duplicates(subset=dedupe_keys, keep="last")

for col in ["duration_min", "delay_min", "passenger_age", "bags_total", "bags_checked"]:
    if col in df.columns:
        df[col] = df[col].round().astype("Int64")

if "ticket_price_usd_est" in df.columns:
    df["ticket_price_usd_est"] = df["ticket_price_usd_est"].round(2)

# Ordena para mejor lectura del archivo limpio
preferred_order = [
    "record_id",
    "airline_code",
    "airline_name",
    "flight_number",
    "origin_airport",
    "destination_airport",
    "departure_datetime",
    "arrival_datetime",
    "duration_min",
    "status",
    "delay_min",
    "aircraft_type",
    "cabin_class",
    "seat",
    "passenger_id",
    "passenger_gender",
    "passenger_age",
    "passenger_nationality",
    "booking_datetime",
    "sales_channel",
    "payment_method",
    "ticket_price",
    "currency",
    "ticket_price_usd_est",
    "bags_total",
    "bags_checked",
    "fecha_dt",
]

ordered_cols = [c for c in preferred_order if c in df.columns] + [c for c in df.columns if c not in preferred_order]
df = df[ordered_cols]

print("3. Carga: generando CSV limpio...")
df.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8")

print("Resumen limpieza:")
print(f"- Registros limpios generados: {len(df)}")
print(f"- Archivo de salida: {OUTPUT_CSV_PATH}")
print("ETL completado correctamente.")