from flask import Flask, jsonify, request, render_template
from misajour import misajour
from supp import supp
from insert import insert
import xml.etree.ElementTree as ET
from lxml import etree
import sys
from outils import *

app = Flask(__name__)


@app.route('/')
@app.route('/search_page')
def search_page():
    return render_template('search.html')


# Routes pour l'API Flask
@app.route('/update_car', methods=['POST'])
def update_car():
    try:
        misajour()  # Appel de la fonction misajour pour mettre à jour le fichier XML et la base de données
        return jsonify({"message": "Car updated successfully!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/delete_car/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    try:
        supp(car_id)  # Pass the car_id parameter to the supp function
        return jsonify({"message": "Car deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/add_car', methods=['POST'])
def add_car():
    try:
        # Récupérer les données du JSON envoyé
        data = request.json
        if not data:
            return jsonify({"message": "Aucune donnée reçue"}), 400
            
        # Préparer les données pour la fonction insert
        info = [
            data.get('year', ''),
            data.get('make', ''),
            data.get('model', ''),
            data.get('body_styles', '')
        ]
        
        insert(info)  # Appel de la fonction insert avec les données
        return jsonify({"message": "Car added successfully!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/get_model_description', methods=['GET'])
def get_model_description():
    print("Requête reçue sur /get_model_description")
    
    # Récupération des paramètres
    car_id = request.args.get('car_id')
    
    if not car_id:
        return jsonify({"error": "ID de voiture non fourni"}), 400
    
    try:
        # Charger le fichier XML
        xml_tree = load_xml_file('cars.xml')
        if not xml_tree:
            return jsonify({"error": "Impossible de charger le fichier XML"}), 500
            
        results = search_cars_by_id(xml_tree, car_id)
        
        if not results:
            return jsonify({"error": f"Voiture avec ID {car_id} non trouvée"}), 404
            
        car = results[0]
        
        # Extraction des détails de la voiture
        car_details = {
            "marque": car.findtext('make', 'Inconnu'),
            "modele": car.findtext('model', 'Inconnu'),
            "annee": car.findtext('year', 'Inconnu'),
            "style": car.findtext('body_styles', 'Inconnu'),
            "carburant": car.findtext('fuel', 'Inconnu') if car.find('fuel') is not None else 'Inconnu',
            "kilometrage": car.findtext('mileage', 'Inconnu') if car.find('mileage') is not None else 'Inconnu'
        }
        
        # Génération de la description (si la fonction est disponible)
        try:
            description = generate_car_description(car_details)
        except:
            description = f"Description générique pour {car_details['marque']} {car_details['modele']} de {car_details['annee']}. Style de carrosserie: {car_details['style']}."
        
        # Retour des détails et de la description
        return jsonify({
            "car_details": car_details,
            "description": description
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500


@app.route('/search_data', methods=['GET'])
def search_car():
    print("Requête reçue sur /search_data")  # Log d'entrée

    try:
        # Récupération des paramètres de recherche
        make = request.args.get('marque', '').strip()
        model = request.args.get('modele', '').strip()
        year = request.args.get('annee', '').strip()
        body_style = request.args.get('body_style', '').strip()
        car_id = request.args.get('car_id')
        newest = request.args.get('newest') == 'true'

        print(f"Paramètres: marque='{make}', année='{year}', modèle='{model}', style='{body_style}'")

        # NE PAS RECHERCHER si tous les champs sont vides
        if not any([make, year, model, body_style, car_id, newest]):
            print("Aucun filtre spécifié. Requête ignorée.")
            return jsonify({"voitures": [], "count": 0}), 200
        
        # Charger le fichier XML
        xml_tree = load_xml_file('cars.xml')
        if not xml_tree:
            return jsonify({"error": "Impossible de charger le fichier XML"}), 500
        
        # Vérification optionnelle avec XSD
        xsd_file = 'cars.xsd'
        try:
            if not validate_xml(xml_tree, xsd_file):
                return jsonify({"error": "Le document XML n'est pas valide selon le schéma XSD!"}), 400
        except:
            pass  
        
        results = []
        
        # Recherche selon les critères fournis
        if car_id is not None:
            results = search_cars_by_id(xml_tree, car_id)
        elif newest:
            results = get_newest_cars(xml_tree)
        elif make is None and model is None and year is None and body_style is None:
            # Récupération de toutes les marques
            makes = get_all_makes(xml_tree)
            return jsonify({"makes": sorted(set(makes))}), 200
        else:
            # Recherche avec critères
            results = search_cars_by_criteria(
                xml_tree,
                make=make,
                model=model,
                year=year,
                body_style=body_style
            )
        
        # Convertir les résultats XML en dictionnaires pour JSON
        cars_list = []
        for car in results:
            car_dict = {
                "id": car.get("id"),
                "marque": car.findtext("make", "Inconnu"),
                "modele": car.findtext("model", "Inconnu"),
                "annee": car.findtext("year", "Inconnu"),
                "style": car.findtext("body_styles", "Inconnu")
            }
            cars_list.append(car_dict)
        
        return jsonify({
            "count": len(cars_list),
            "voitures": cars_list
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)