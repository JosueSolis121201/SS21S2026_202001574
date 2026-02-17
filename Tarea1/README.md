# Tarea 1 - Limpieza y Analisis de Datos

## Dataset utilizado
- Nombre del archivo: `dataset_sucio.csv`
- Fuente: Proporcionado para la tarea

## Proceso de limpieza 
1. Carga de datos y copia del dataset original.
2. Eliminacion de duplicados.
3. Estandarizacion de columnas de texto (nombre, genero, ciudad, categoria):
   - Relleno de valores faltantes con "Desconocido".
   - Limpieza de espacios y formato en titulo.
4. Normalizacion de genero en tres categorias: Masculino, Femenino, Desconocido.
5. Limpieza de gasto:
   - Correccion de separador decimal.
   - Conversion a numerico e imputacion con la mediana.
6. Estandarizacion de fechas con formatos mixtos.
7. Exportacion del dataset limpio a `dataset_limpio.csv`.

## Capturas de pantalla
- Graficas con pandas
  - Histograma de gasto
![alt text](<img/fecuencia de gasto.png>)
  - Gasto total por ciudad
![alt text](<img/Gasto por ciudad.png>)
  - Conteo por categoria
![alt text](<img/Conteo por categoria.png>)


## Interpretacion de resultados (resumen)
- La estandarizacion reduce variaciones en texto (mayusculas/minusculas y espacios) y consolida categorias.
- El gasto queda en formato numerico consistente, permitiendo comparaciones y agregaciones.
- Las graficas permiten identificar la distribucion del gasto, las ciudades con mayor gasto total y la frecuencia por categoria.
