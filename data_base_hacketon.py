import sqlite3
from sqlite3 import Error
import hashlib

DB_PATH = "camara_api_db.db"


def setup_database():
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        # Risk data table (stores KYC + SIM/Device swap info)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idDocumentMatch TEXT,
            nameMatch TEXT,
            givenNameMatch TEXT,
            familyNameMatch TEXT,
            middleNamesMatch TEXT,
            addressMatch TEXT,
            streetNameMatch TEXT,
            streetNumberMatch TEXT,
            postalCodeMatch TEXT,
            countryMatch TEXT,
            birthdateMatch TEXT,
            emailMatch TEXT,
            sim_swap REAL,
            Device_swap REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Users table for login
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            credits INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        mydb.commit()
        print("✓ Database ready")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if 'mydb' in locals() and mydb:
            mycursor.close()
            mydb.close()



# MAIN FUNCTION: Store operator data

def save_operator_data(response_data):
    """
    ONLY function you need!
    
    Receives data from colleague's endpoint and stores it.
    
    Expected format from colleague:
    {
        "kyc": {
            "idDocumentMatch": "true",
            "nameMatch": "false",
            ...
        },
        "sim_swap": {...},
        "device_swap": {...}
    }
    """
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        
        kyc = response_data.get("kyc", {})
        sim_swap_info = response_data.get("sim_swap", {})
        device_swap_info = response_data.get("device_swap", {})
        
        # Extract values, or use "not_available" if missing
        kyc_values = (
            kyc.get("idDocumentMatch", "not_available"),
            kyc.get("nameMatch", "not_available"),
            kyc.get("givenNameMatch", "not_available"),
            kyc.get("familyNameMatch", "not_available"),
            kyc.get("middleNamesMatch", "not_available"),
            kyc.get("addressMatch", "not_available"),
            kyc.get("streetNameMatch", "not_available"),
            kyc.get("streetNumberMatch", "not_available"),
            kyc.get("postalCodeMatch", "not_available"),
            kyc.get("countryMatch", "not_available"),
            kyc.get("birthdateMatch", "not_available"),
            kyc.get("emailMatch", "not_available"),
        )
        
        # Convert swap data to scores (1.0 if happened, 0.0 if not)
        sim_swap_score = 1.0 if sim_swap_info.get("latestSimChange") else 0.0
        device_swap_score = 1.0 if device_swap_info.get("deviceChanged") else 0.0
        
        # Insert into database
        sql = """
        INSERT INTO risk_data (
            idDocumentMatch, nameMatch, givenNameMatch, familyNameMatch,
            middleNamesMatch, addressMatch, streetNameMatch, streetNumberMatch,
            postalCodeMatch, countryMatch, birthdateMatch, emailMatch,
            sim_swap, Device_swap
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        mycursor.execute(sql, kyc_values + (sim_swap_score, device_swap_score))
        mydb.commit()
        
        print(f"✓ Data stored (ID: {mycursor.lastrowid})")
        
        mycursor.close()
        mydb.close()
        return True
        
    except Exception as e:
        print(f"✗ Error storing data: {e}")
        return False


# ============================================================
# HELPER: View stored data
# ============================================================

def view_all_data():
    """Quick view of what's in the database"""
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        
        mycursor.execute("SELECT * FROM risk_data ORDER BY created_at DESC")
        results = mycursor.fetchall()
        
        print(f"\n--- Stored Records ({len(results)} total) ---")
        for row in results:
            print(f"ID: {row[0]} | idMatch: {row[1]} | nameMatch: {row[2]} | SIM: {row[13]} | Device: {row[14]}")
        
        mycursor.close()
        mydb.close()
        
    except Exception as e:
        print(f"Error: {e}")


# ============================================================
# Initialize database on startup
# ============================================================
setup_database()
