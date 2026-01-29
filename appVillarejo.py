# Estudiante: Luis Carlos Villarejo CC 94542302

from unittest.mock import patch
from flask import Flask, request, render_template_string, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt)
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "clave-super-secreta"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=15)
jwt = JWTManager(app)


host = "mongodb://localhost"
port = 27017
db_name = "vehiculos_flask"


users_collection = None
vehiculos_collection = None


def connect_db():        
    global vehiculos_collection, users_collection
    
    try:
        client = MongoClient(f"{host}:{port}/")
        db = client[db_name]
        client.admin.command("ping")
        users_collection = db.users
        vehiculos_collection = db.vehiculos
        print("Conexión exitosa a la base de datos")
    
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
    



vehiculos_burned = [{"marca": "Chevrolet","modelo": "Captiva","año": 2011,"tipo": "SUV","color": "gris"},
    { "marca": "Nissan","modelo": "March","año": 2018, "tipo": "Hatchback","color": "Azul"},    
    { "marca": "Mazda","modelo": "CX-5","año": 2020,"tipo": "SUV","color": "Blanco" },
    { "marca": "Kia", "modelo": "Sportage", "año": 2015,"tipo": "SUV", "color": "Negro"},
    { "marca": "Ford", "modelo": "Focus", "año": 2017, "tipo": "Hatchback", "color": "Rojo"}]

def migrate_vehiculos():
    global vehiculos_collection
    count = vehiculos_collection.count_documents({})
    if count == 0:
        vehiculos_collection.insert_many(vehiculos_burned)
        print("Datos migrados a la base de datos")
    else:
        print("La colección ya contiene datos, no se migraron")


"""vehiculos = { "1": {'marca': 'Chevrolet', 'modelo': 'Captiva', 'año': 2011, 'tipo': 'SUV', 'color': 'gris'}, 
             "2": {'marca': 'Nissan', 'modelo': 'march', 'año': 2018, 'tipo': 'hatchback', 'color': 'Azul'},
             "3": {'marca': 'Mazda', 'modelo': 'CX-5', 'año': 2020, 'tipo': 'SUV', 'color': 'blanco'},
             "4": {'marca': 'Kia', 'modelo': 'Sportage', 'año': 2015, 'tipo': 'SUV', 'color': 'negro'}, 
             "5": {'marca': 'Ford', 'modelo': 'Focus', 'año': 2017, 'tipo': 'hatchback', 'color': 'rojo'}}"""

def normalize_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def get_token_role():
    claims = get_jwt()
    return claims.get("role")

def manager_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        role = get_token_role()
        if role in ["manager", "admin"]:
            return fn(*args, **kwargs)
        return {"error": "No Autorizado", "message": "Rol no autorizado"}, 403
    return wrapper

def create_admin_if_not_exists():
    admin = users_collection.find_one({"role": "admin"})

    if not admin:
        users_collection.insert_one({"username": "admin", "password_hash": generate_password_hash("123456"), "role": "admin", "created_at": datetime.now()})
        print("Usuario admin creado! (admin / 123456)")
    else:
        print(" Usuario ya existe")

def get_token_role():
    claims = get_jwt()
    return claims.get("role")
    
@app.route("/api/signIn", methods=["POST"])
def sign_in():
    body = request.json
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return {"error": "Datos Incompletos "}, 400
    if users_collection.find_one({"username": username}):
        return {"error": "Usuario ya existe"}, 400
    user = {"username": username, "password_hash": generate_password_hash(password), "role" : "client", "created_at": datetime.now()}
    users_collection.insert_one(user)
    return {"message": "Usuario creado exitosamente", "role": "client"}, 201

@app.route("/api/login", methods=["POST"])
def login():
    body = request.json
    username = body.get("username")
    password = body.get("password")
    user = users_collection.find_one({"username": username})
    if not user:
        return {"error": "Usuario no encontrado"}, 400
    if not check_password_hash(user["password_hash"], password):
        return {"error": "Contraseña incorrecta"}, 401
    
    token = create_access_token(identity=username, additional_claims={"role": user["role"]})
    return {"access_token": token}, 200


@app.route("/api/admin/signin/manager", methods=["POST"])
@jwt_required()
def sign_in_manager():
    role = get_token_role()
    if role != "admin":
        return {"error": "No Autorizado", "message": "Rol no autorizado"}, 403
    
    body = request.json
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return {"error": "Datos Incompletos "}, 400
    if users_collection.find_one({"username": username}):
        return {"error": "Usuario ya existe"}, 400
    user = {"username": username, "password_hash": generate_password_hash(password), "role" : "manager", "created_at": datetime.now()}
    users_collection.insert_one(user)
    return {"message": "Usuario manager creado exitosamente", "role": "manager"}, 201


@app.route('/api/vehiculos/', methods=['GET'])
@jwt_required()
def get_vehiculos():
    resultado = list(vehiculos_collection.find())
    resultado = list(map(normalize_id, resultado))
    return resultado, 200

@app.route('/api/vehiculos/<string:id>/', methods=['GET'])
def get_vehiculo(id):
    vehiculo = vehiculos_collection.find_one({"_id": ObjectId(id)})
    if vehiculo:
        return normalize_id(vehiculo), 200
    return {"error": "Vehículo no encontrado"}, 404

@app.route('/api/vehiculos/', methods=['POST'])
@manager_required
def create_vehiculo():
    body = request.json
    result = vehiculos_collection.insert_one(body)
    body["_id"] = str(result.inserted_id)
    return body, 201

@app.route('/api/vehiculos/<string:id>/', methods = ['PATCH'])
def update_vehiculo(id):
    body = request.json
    result = vehiculos_collection.update_one({"_id": ObjectId(id)}, {"$set": body})
    if result.matched_count:
        vehiculo = vehiculos_collection.find_one({"_id": ObjectId(id)})
        return normalize_id(vehiculo), 200
    
@app.route('/api/vehiculos/<string:id>/', methods=['DELETE'])
def delete_vehiculo(id):
    vehiculo = vehiculos_collection.find_one({"_id": ObjectId(id)})
    if not vehiculo:
        return {"error": "Vehículo no encontrado"}, 404
    
    vehiculos_collection.delete_one({"_id": ObjectId(id)})
    return {"mensaje": "Vehículo eliminado"}, 200

@app.route("/dynamic-home")
def dynamic_home():
    total_vehiculos = vehiculos_collection.count_documents({})

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vehículos - Flask SSR</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #333;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 15px;
                width: 400px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                margin-bottom: 10px;
            }
            .badge {
                background: #667eea;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                display: inline-block;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚗 Vehículos App</h1>
            <p>Aplicación Flask con MongoDB</p>
            <div class="badge">Total vehículos: {{ total }}</div>
            <p>Fecha servidor:</p>
            <strong>{{ fecha }}</strong>
        </div>
    </body>
    </html>
    """

    return render_template_string(
        html,
        total=total_vehiculos,
        fecha=datetime.now()
    ) 


           

"""
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
    return {"error": "Vehículo no encontrado"}, 404"""

if __name__ == '__main__':
    connect_db()
    migrate_vehiculos()
    create_admin_if_not_exists()
    app.run(debug=True, port=8000)