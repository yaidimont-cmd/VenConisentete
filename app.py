from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)

RESERVAS_FILE = "reservas.json"
ADMIN_PASSWORD = "tucontraseña123"  # Cambia esto

# Cargar reservas
def cargar_reservas():
    try:
        with open(RESERVAS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Guardar reservas
def guardar_reservas(reservas):
    with open(RESERVAS_FILE, "w") as f:
        json.dump(reservas, f)

# Diccionario de productos y sus duraciones
productos = {
    "Depilación 1": 60,
    "Depilación 2": 45,
    "Depilación 3": 30,
    "Keratina 1": 90,
    "Keratina 5": "Contactar"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/productos")
def productos_page():
    return render_template("productos.html", productos=productos)

@app.route("/reservas", methods=["GET", "POST"])
def reservas_page():
    reservas = cargar_reservas()
    mensaje = ""
    if request.method == "POST":
        producto = request.form["producto"]
        fecha = request.form["fecha"]
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]

        if productos[producto] == "Contactar":
            mensaje = "Para este servicio debe contactarnos directamente."
            return render_template("reservas.html", productos=productos, mensaje=mensaje)

        duracion = productos[producto]

        # Comprobar fin de semana
        dia_semana = datetime.strptime(fecha, "%Y-%m-%d").weekday()
        if dia_semana >= 5:
            mensaje = "No se realizan reservas los fines de semana."
            return render_template("reservas.html", productos=productos, mensaje=mensaje)

        # Comprobar minutos totales del día
        reservas_dia = sum([r["duracion"] for r in reservas.get(fecha, [])])
        if reservas_dia + duracion > 400:
            mensaje = "Ese día ya no tiene disponibilidad."
            return render_template("reservas.html", productos=productos, mensaje=mensaje)

        # Guardar reserva
        nueva_reserva = {
            "producto": producto,
            "duracion": duracion,
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion
        }
        if fecha not in reservas:
            reservas[fecha] = []
        reservas[fecha].append(nueva_reserva)
        guardar_reservas(reservas)
        mensaje = "Reserva confirmada!"
        return render_template("reservas.html", productos=productos, mensaje=mensaje)

    return render_template("reservas.html", productos=productos, mensaje=mensaje)

@app.route("/admin", methods=["GET", "POST"])
def admin_page():
    reservas = cargar_reservas()
    acceso = False
    if request.method == "POST":
        password = request.form["password"]
        if password == ADMIN_PASSWORD:
            acceso = True
    return render_template("admin.html", reservas=reservas, acceso=acceso)

if __name__ == "__main__":
    app.run(debug=True)
