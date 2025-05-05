import sqlite3
from datetime import datetime

conn = sqlite3.connect('parking.db')
cursor = conn.cursor()

cursor.execute('PRAGMA foreign_keys = ON;')


cursor.execute('''DELETE FROM parking_status WHERE registration_number IS NOT NULL''')
cursor.execute('DROP TABLE IF EXISTS car_permission;')
cursor.execute('DROP TABLE IF EXISTS car_allowance;')
cursor.execute('DROP TABLE IF EXISTS events;')
cursor.execute('DROP TABLE IF EXISTS parking_status;')

cursor.execute('''
CREATE TABLE IF NOT EXISTS car_permission (
    car_id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT UNIQUE NOT NULL,
    allowance BOOLEAN NOT NULL CHECK (allowance IN (0, 1)), -- 0: Not Allowed, 1: Allowed
    image_path TEXT NOT NULL  -- Path to the cropped plate image
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS parking_status (
    parking_spot TEXT PRIMARY KEY, 
    registration_number TEXT UNIQUE,
    FOREIGN KEY (registration_number) REFERENCES car_permission (registration_number)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,         
    description TEXT NOT NULL,        
    timestamp TEXT NOT NULL           
)
''')

conn.commit()
#print("Database schema updated successfully.")

cursor.executemany('''
INSERT INTO car_permission (registration_number, allowance, image_path) 
VALUES (?, ?, ?)
''', [
    ("EL 6666S",1, r"D:\SEMESTR 5\PRZETWARZANIE OBRAZOW\projekt_parking_PSIO\registration\EL 6666S.png"),
    ("EL 2222S",1, r"D:\SEMESTR 5\PRZETWARZANIE OBRAZOW\projekt_parking_PSIO\registration\EL 2222S.png"),
    ("EL 4444S",0, r"D:\SEMESTR 5\PRZETWARZANIE OBRAZOW\projekt_parking_PSIO\registration\EL 4444S.png"),
    ("EL 5555S",1, r"D:\SEMESTR 5\PRZETWARZANIE OBRAZOW\projekt_parking_PSIO\registration\EL 5555S.png"),
    ("EL 1111S",1, r"D:\SEMESTR 5\PRZETWARZANIE OBRAZOW\projekt_parking_PSIO\registration\EL 1111S.png"),
])

conn.commit()
#print("Sample data inserted.")

parking_spots = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
for spot in parking_spots:
    cursor.execute('''INSERT OR IGNORE INTO parking_status (parking_spot, registration_number)VALUES (?, ?)''', (spot, None))

conn.commit()

def get_car_image_dict():
    cursor.execute("SELECT registration_number, image_path FROM car_permission")
    plates_dict = {reg_number: image_path for reg_number, image_path in cursor.fetchall()}
    return plates_dict

plates_dict = get_car_image_dict()
#print(plates_dict)


def is_car_allowed(registration_number):

    cursor.execute("SELECT allowance FROM car_permission WHERE registration_number = ?", (registration_number,))
    result = cursor.fetchone()

    if result is not None:
        return bool(result[0]) 
    
    return False

def log_event(event_type, description):
    """Logs an event into the database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO events (event_type, description, timestamp) VALUES (?, ?, ?)",
                   (event_type, description, timestamp))
    
    conn.commit()
    
def update_parking_status_for_spot(spot_label, current_car):
    """Updates the registration number for a specific parking spot."""
    cursor.execute('''UPDATE parking_status 
                      SET registration_number = ? 
                      WHERE parking_spot = ?''', (current_car, spot_label))
    conn.commit()