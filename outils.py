import argparse
import xml.etree.ElementTree as ET
from lxml import etree
from groq import Groq
import sys
import os

# Fonctions de parsing XML intégrées directement depuis s.py
def load_xml_file(file_path='cars.xml'):
    try:
        return etree.parse(file_path)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier XML: {e}", file=sys.stderr)
        return None

def validate_xml(xml_tree, xsd_file='cars.xsd'):
    """
    Valide un document XML par rapport à un schéma XSD.
    """
    xml_tree=load_xml_file()
    try:
        xsd_doc = etree.parse(xsd_file)
        schema = etree.XMLSchema(xsd_doc)
        return schema.validate(xml_tree)
    except Exception as e:
        print(f"Erreur lors de la validation XSD: {e}", file=sys.stderr)
        return False

def search_cars_by_make(xml_tree, make):
    return xml_tree.xpath(f"//car[make = '{make}']")

def search_cars_by_year(xml_tree, year):
    return xml_tree.xpath(f"//car[year = {year}]")

def search_cars_by_model(xml_tree, model):
    return xml_tree.xpath(f"//car[model = '{model}']")

def search_cars_by_body_style(xml_tree, body_style):
    return xml_tree.xpath(f"//car[contains(body_styles, '{body_style}')]")

def search_cars_by_id(xml_tree, car_id):
    return xml_tree.xpath(f"//car[@id = '{car_id}']")

def search_cars_by_criteria(xml_tree, make=None, model=None, year=None, body_style=None):
    # Recherche des voitures selon plusieurs critères combinés.
    query_parts = []
    
    if make:
        query_parts.append(f"make = '{make}'")
    if model:
        query_parts.append(f"model = '{model}'")
    if year:
        query_parts.append(f"year = {year}")
    if body_style:
        query_parts.append(f"contains(body_styles, '{body_style}')")
    
    if not query_parts:
        return []
    
    xpath_query = "//car[" + " and ".join(query_parts) + "]"
    return xml_tree.xpath(xpath_query)

def get_all_cars(xml_tree):
    return xml_tree.xpath("//car")

def get_all_makes(xml_tree):
    return xml_tree.xpath("//make/text()")

def get_newest_cars(xml_tree, limit=5):
    all_cars = xml_tree.xpath("//car")
    # Trier les voitures par année (décroissant)
    sorted_cars = sorted(all_cars, key=lambda car: int(car.find("year").text), reverse=True)
    return sorted_cars[:limit]

def car_to_dict(car):
    """Convertit un élément XML car en dictionnaire"""
    car_dict = {
        "id": car.get("id"),
        "year": car.find("year").text,
        "make": car.find("make").text,
        "model": car.find("model").text,
        "body_styles": car.find("body_styles").text
    }
    return car_dict



# Configuration de l'API Groq
api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

# Prompt système pour guider l'IA
system_prompt = """
Tu es un assistant expert en vente automobile. Ton rôle est de créer des descriptions attractives pour des voitures à vendre. Les descriptions doivent :
1. Être claires et bien structurées
2. Mettre en valeur les points forts du véhicule
3. Inclure des informations techniques importantes
4. Utiliser un langage persuasif mais honnête
5. Adapter le style en fonction du type de véhicule (luxe, sport, familial, etc.)
6. N'ecris jamais ca "Merci pour les informations !"
7. Ne pose pas de questions 
8. Ne demande rien a l'utilisateur 
9. dans le cas ou tu a besoin de plus de description propose juste une description de base  

Demande toujours des détails sur la voiture si nécessaire pour fournir la meilleure description possible.
"""

# Fonction pour générer une description de voiture
def generate_car_description(car_details):
    """Génère une description de voiture à partir des détails donnés en utilisant l'API Groq."""
    try:
        # Préparation des détails de voiture pour l'IA
        details_str = f"Marque: {car_details.get('marque', 'Inconnu')}, "
        details_str += f"Modèle: {car_details.get('modele', 'Inconnu')}, "
        details_str += f"Année: {car_details.get('annee', 'Inconnu')}, "
        details_str += f"Style de carrosserie: {car_details.get('style', 'Inconnu')}"
        
        # Autres attributs disponibles
        for key, value in car_details.items():
            if key not in ['marque', 'modele', 'annee', 'style', 'id']:
                details_str += f", {key}: {value}"
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": details_str}
            ],
            temperature=0.7,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erreur lors de la génération de description: {str(e)}")
        return f"Erreur lors de la génération de la description: {str(e)}"