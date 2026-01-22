# Estudiante: Luis Carlos Villarejo CC 94542302

from flask import Flask, request

vehiculos = { "1": {'marca': 'Chevrolet', 'modelo': 'Captiva', 'año': 2011, 'tipo': 'SUV', 'color': 'gris'}, 
             "2": {'marca': 'Nissan', 'modelo': 'march', 'año': 2018, 'tipo': 'hatchback', 'color': 'Azul'},
             "3": {'marca': 'Mazda', 'modelo': 'CX-5', 'año': 2020, 'tipo': 'SUV', 'color': 'blanco'},
             "4": {'marca': 'Kia', 'modelo': 'Sportage', 'año': 2015, 'tipo': 'SUV', 'color': 'negro'}, 
             "5": {'marca': 'Ford', 'modelo': 'Focus', 'año': 2017, 'tipo': 'hatchback', 'color': 'rojo'}}

app = Flask(__name__)
@app.route('/')
def home():
    return "Flask funcionando"


@app.route('/api/vehiculos/<string:id>/', methods=['GET'])
def obtener_vehiculo(id):
    if id in vehiculos:
        return vehiculos[id], 200
    return {"error": "Vehículo no encontrado"}, 404


@app.route('/api/vehiculos/', methods=['GET'])
def obtener_vehiculos():
    tipo = request.args.get("tipo")
    anio = request.args.get("anio")

    resultado = list(vehiculos.values())

    if tipo:
        resultado = list(filter(lambda v: v["tipo"].lower() == tipo.lower(), resultado))
    
    if anio:
        resultado = list(filter(lambda v: v["año"] >= int(anio), resultado))

    return resultado, 200

@app.route('/api/vehiculos/', methods=['POST'])
def crear_vehiculo():
    body = request.json

    if not body or "id" not in body:
        return {"error": "Datos inválidos"}, 400
    
    nuevo_id = body["id"]
    if nuevo_id in vehiculos:
        return {"error": "El vehículo ya existe"}, 400
    
    nuevo_vehiculo = body.copy()
    del nuevo_vehiculo["id"]

    vehiculos[nuevo_id] = nuevo_vehiculo
    return vehiculos[nuevo_id], 201

@app.route('/api/vehiculos/<string:id>/', methods=['DELETE'])
def eliminar_vehiculo(id):
    if id in vehiculos:
        eliminado = vehiculos[id]
        del vehiculos[id]
        return {"mensaje": "Vehículo eliminado"}, 200
    return {"error": "Vehículo no encontrado"}, 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)