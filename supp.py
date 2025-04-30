import psycopg2
import xml.etree.ElementTree as ET
from connec import connec

# def supp():
#     try:
#         conn, cursor = connec()

#         tree = ET.parse('cars.xml')
#         root = tree.getroot()

#         for car in root.findall('car'):
#             if car.find('make').text == 'Toyota' and car.find('model').text == 'Corolla':
#                 root.remove(car)
#                 break

#         tree.write('cars.xml')

#         cursor.execute("""
#             DELETE FROM cars
#             WHERE data::text LIKE '%Toyota%'
#         """)

#         conn.commit()
#         cursor.close()
#         conn.close()

#     except Exception as e:
#         raise Exception(f"Error deleting car: {str(e)}")

# import psycopg2
# import xml.etree.ElementTree as ET
# from connec import connec

def supp(car_id):
    try:
        conn, cursor = connec()

        tree = ET.parse('cars.xml')
        root = tree.getroot()

        # Trouver et supprimer la voiture par ID
        car_to_remove = None
        for car in root.findall('car'):
            if car.get('id') == str(car_id):
                car_to_remove = car
                break

        if car_to_remove is not None:
            root.remove(car_to_remove)
            tree.write('cars.xml')

            # # Suppression dans PostgreSQL
            # cursor.execute("""
            #     DELETE FROM cars 
            #     WHERE xpath_exists('/car[@id=%s]', data::xml)
            # """, (car_id,))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            raise Exception("Car not found")

    except Exception as e:
        raise Exception(f"Error deleting car: {str(e)}")
