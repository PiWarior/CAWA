import psycopg2
import xml.etree.ElementTree as ET
from connec import connec

def get_next_id(root):
    try:
        return max(int(car.get('id', 0)) for car in root.findall('car')) + 1
    except ValueError:
        return 1

def insert(info):
    try:
        conn, cursor = connec()

        # Charger le fichier XML existant
        try:
            tree = ET.parse('cars.xml')
            root = tree.getroot()
        except FileNotFoundError:
            # Si le fichier n'existe pas, créer un nouveau document XML
            root = ET.Element('cars')
            tree = ET.ElementTree(root)

        # Déterminer le prochain ID
        next_id = get_next_id(root)

        # Créer un nouvel élément voiture
        new_car = ET.Element('car')
        new_car.set('id', str(next_id))
        
        # Ajouter les sous-éléments
        year = ET.SubElement(new_car, 'year')
        year.text = info[0]
        make = ET.SubElement(new_car, 'make')
        make.text = info[1]
        model = ET.SubElement(new_car, 'model')
        model.text = info[2]
        body_styles = ET.SubElement(new_car, 'body_styles')  # Corrigé de 'price' à 'body_styles'
        body_styles.text = info[3]

        # Ajouter la nouvelle voiture à la racine
        root.append(new_car)

        # Enregistrer le fichier XML
        tree.write('cars.xml')

        # Insérer dans la base de données PostgreSQL
        cursor.execute("""
            INSERT INTO cars (data)
            VALUES (%s)
        """, (ET.tostring(new_car, encoding='unicode'),))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        raise Exception(f"Error adding car: {str(e)}")