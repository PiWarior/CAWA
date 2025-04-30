import psycopg2
import xml.etree.ElementTree as ET
from connec import connec

def misajour():
    try:
        conn, cursor = connec()

        tree = ET.parse('cars.xml')
        root = tree.getroot()

        for car in root.findall('car'):
            if car.find('make').text == 'Toyota' and car.find('model').text == 'Corolla':
                car.find('price').text = '22000.00'
                break

        tree.write('cars.xml')

        cursor.execute("""
            UPDATE cars
            SET data = %s
            WHERE data::text LIKE '%Toyota%'
        """, (ET.tostring(car, encoding='unicode'),))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        raise Exception(f"Error updating car: {str(e)}")
