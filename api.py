# api.py
# Ejecutar con: uvicorn api:app --reload

from fastapi import FastAPI, HTTPException
import pyodbc
import pandas as pd

app = FastAPI(title="API Contoso Big Data")

# --- 1. CONFIGURACIÓN DE CONEXIÓN CORREGIDA ---
# OJO AQUÍ: He puesto 'localhost\\SQLEXPRESS' (con DOBLE barra)
# Si usas una sola barra, Python falla.
STR_CONN = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;' 
    'DATABASE=Contoso 100K;'
    'Trusted_Connection=yes;'
)

def get_data_from_sql(query):
    try:
        conn = pyodbc.connect(STR_CONN)
        df = pd.read_sql(query, conn)
        conn.close()
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"❌ Error SQL: {e}")
        # Esto enviará el error exacto al frontend para que lo leas
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "online", "db": "Contoso 100K"}

# --- 2. ENDPOINTS ADAPTADOS A TUS IMÁGENES ---

@app.get("/kpis")
def obtener_kpis():
    # CORRECCIÓN: Usamos [Unit Price] con corchetes y OrderKey junto
    sql = """
    SELECT 
        SUM(R.Quantity * R.[Unit Price]) AS TotalVentas,
        COUNT(DISTINCT R.OrderKey) AS TotalPedidos,
        AVG(R.Quantity * R.[Unit Price]) AS TicketPromedio
    FROM [Data].[OrderRows] R
    """
    # Retornamos solo el primer resultado (el diccionario)
    data = get_data_from_sql(sql)
    return data[0] if data else {}

@app.get("/tendencia")
def obtener_tendencia():
    # CORRECCIÓN: Join usando OrderKey (sin espacios)
    # Asumo que en la tabla Orders la fecha es [Order Date]
    sql = """
    SELECT 
        FORMAT(O.[Order Date], 'yyyy-MM') as Mes, 
        SUM(R.Quantity * R.[Unit Price]) as Ventas
    FROM [Data].[OrderRows] R
    JOIN [Data].[Orders] O ON R.OrderKey = O.OrderKey
    GROUP BY FORMAT(O.[Order Date], 'yyyy-MM')
    ORDER BY Mes
    """
    return get_data_from_sql(sql)

@app.get("/top-productos")
def obtener_top_productos():
    # CORRECCIÓN: Usamos [Product Name] con espacio (visto en tu imagen anterior)
    sql = """
    SELECT TOP 10 
        P.[Product Name] as Producto, 
        SUM(R.Quantity * R.[Unit Price]) as Ventas
    FROM [Data].[OrderRows] R
    JOIN [Data].[Product] P ON R.ProductKey = P.ProductKey
    GROUP BY P.[Product Name]
    ORDER BY Ventas DESC
    """
    return get_data_from_sql(sql)