import sqlite3
from sqlite3 import Error
import hashlib

DB_PATH = "camara_api_db.db"


def hash_password(password: str) -> str:
    """Hash plain password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def setup_database():
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        # Risk data table (stores KYC + SIM/Device swap info)
        mycursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
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
            sim_swap_date TEXT,
            device_swap_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
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
        
        # Add user_id column to existing risk_data table if it doesn't exist
        try:
            mycursor.execute("ALTER TABLE risk_data ADD COLUMN user_id INTEGER")
        except:
            pass  # Column already exists
        
        # Rename sim_swap/Device_swap columns to date columns if needed
        try:
            mycursor.execute("ALTER TABLE risk_data RENAME COLUMN sim_swap TO sim_swap_date")
        except:
            pass  # Column already renamed or doesn't exist
        
        try:
            mycursor.execute("ALTER TABLE risk_data RENAME COLUMN Device_swap TO device_swap_date")
        except:
            pass  # Column already renamed or doesn't exist
        
        mydb.commit()
        print("Database ready")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if 'mydb' in locals() and mydb:
            mycursor.close()
            mydb.close()



# MAIN FUNCTION: Store operator data

def save_operator_data(response_data, user_id=None):
    """
    Store operator API response data.
    
    Args:
        response_data: API response with KYC, SIM/Device swap info
        user_id: ID of the user this data belongs to (optional)
    
    Expected format:
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
        
        # Extract swap dates (store as text, or None if not provided)
        sim_swap_date = sim_swap_info.get("latestSimChange")
        device_swap_date = device_swap_info.get("deviceChanged")
        
        # Insert into database
        sql = """
        INSERT INTO risk_data (
            user_id, idDocumentMatch, nameMatch, givenNameMatch, familyNameMatch,
            middleNamesMatch, addressMatch, streetNameMatch, streetNumberMatch,
            postalCodeMatch, countryMatch, birthdateMatch, emailMatch,
            sim_swap_date, device_swap_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        mycursor.execute(sql, (user_id,) + kyc_values + (sim_swap_date, device_swap_date))
        mydb.commit()
        
        print(f"Data stored (ID: {mycursor.lastrowid})")
        
        mycursor.close()
        mydb.close()
        return True
        
    except Exception as e:
        print(f"Error storing data: {e}")
        return False


# ============================================================
# HELPER: View stored data
# ============================================================

def view_all_data():
    """Quick view of what's in the database"""
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        
        mycursor.execute("""
            SELECT r.id, r.user_id, u.username, r.idDocumentMatch, r.nameMatch, 
                   r.sim_swap_date, r.device_swap_date
            FROM risk_data r
            LEFT JOIN users u ON r.user_id = u.id
        """)
        results = mycursor.fetchall()
        
        print(f"\n--- Stored Records ({len(results)} total) ---")
        for row in results:
            user_info = f"User: {row[2]}" if row[2] else "User: None"
            sim_info = f"SIM: {row[5]}" if row[5] else "SIM: None"
            device_info = f"Device: {row[6]}" if row[6] else "Device: None"
            print(f"ID: {row[0]} | {user_info} (ID: {row[1]}) | idMatch: {row[3]} | nameMatch: {row[4]} | {sim_info} | {device_info}")
        
        mycursor.close()
        mydb.close()
        
    except Exception as e:
        print(f"Error: {e}")


def get_risk_data_with_user(risk_data_id=None):
    """
    View risk data records with associated user information.
    
    Args:
        risk_data_id: Optional - specific record ID to view. If None, shows all records.
    
    Returns detailed information about risk data and the user it belongs to.
    """
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()
        
        if risk_data_id:
            mycursor.execute("""
                SELECT r.id, r.user_id, u.username, u.credits,
                       r.idDocumentMatch, r.nameMatch, r.givenNameMatch, 
                       r.familyNameMatch, r.sim_swap_date, r.device_swap_date
                FROM risk_data r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.id = ?
            """, (risk_data_id,))
            results = [mycursor.fetchone()]
        else:
            mycursor.execute("""
                SELECT r.id, r.user_id, u.username, u.credits,
                       r.idDocumentMatch, r.nameMatch, r.givenNameMatch, 
                       r.familyNameMatch, r.sim_swap_date, r.device_swap_date
                FROM risk_data r
                LEFT JOIN users u ON r.user_id = u.id
            """)
            results = mycursor.fetchall()
        
        print("\n" + "="*60)
        print("RISK DATA WITH USER INFORMATION")
        print("="*60)
        
        for row in results:
            if row:
                print(f"\nRisk Data Record ID: {row[0]}")
                print("-" * 60)
                if row[1]:  # Has user_id
                    print(f"Belongs to User ID: {row[1]}")
                    print(f"Username: {row[2]}")
                    print(f"User Credits: {row[3]}")
                    print("\nNote: Password is hashed for security.")
                    print("      Only the user knows their password.")
                else:
                    print("User: Not assigned to any user")
                
                print(f"\nKYC Match Results:")
                print(f"  - ID Document Match: {row[4]}")
                print(f"  - Name Match: {row[5]}")
                print(f"  - Given Name Match: {row[6]}")
                print(f"  - Family Name Match: {row[7]}")
                print(f"\nFraud Indicators:")
                print(f"  - SIM Swap Date: {row[8] if row[8] else 'None'}")
                print(f"  - Device Swap Date: {row[9] if row[9] else 'None'}")
                print("-" * 60)
        
        mycursor.close()
        mydb.close()
        
    except Exception as e:
        print(f"Error: {e}")


# ============================================================
# Initialize database on startup
# ============================================================
setup_database()


def create_user(username: str, password: str, credits: int = 100):
    """
    Create a user account.
    Returns: (success: bool, user_id: int | None, message: str)
    """
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()

        password_hash = hash_password(password)
        mycursor.execute(
            "INSERT INTO users (username, password_hash, credits) VALUES (?, ?, ?)",
            (username, password_hash, credits),
        )
        mydb.commit()

        user_id = mycursor.lastrowid
        mycursor.close()
        mydb.close()
        return True, user_id, "User created"

    except sqlite3.IntegrityError:
        return False, None, "Username already exists"
    except Exception as e:
        return False, None, f"Error creating user: {e}"


def validate_login_get_user_id(username: str, password: str):
    """
    Validate credentials and return user id.
    Returns: (is_valid: bool, user_id: int | None)
    """
    try:
        mydb = sqlite3.connect(DB_PATH)
        mycursor = mydb.cursor()

        password_hash = hash_password(password)
        mycursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
        )
        row = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        if row:
            return True, row[0]
        return False, None

    except Exception as e:
        print(f"Error validating login: {e}")
        return False, None


def has_database_access(username: str, password: str):
    """
    Helper for API usage.
    Returns: (granted: bool, user_id: int | None, message: str)
    """
    is_valid, user_id = validate_login_get_user_id(username, password)
    if not is_valid:
        return False, None, "Invalid username or password"
    return True, user_id, "Access granted"


def test_login_flow():
    """
    Test the complete login flow.
    Run this to verify everything works.
    """
    from datetime import datetime
    
    print("\n=== Testing Login System ===\n")
    
    # Test 1: Create user
    test_username = f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_password = "SecurePass123!"
    
    print("1. Creating test user...")
    success, user_id, msg = create_user(test_username, test_password)
    print(f"   Result: {msg} (User ID: {user_id})")
    
    if not success:
        print("   FAILED: Could not create user")
        return
    
    # Test 2: Valid login
    print("\n2. Testing valid login...")
    granted, returned_id, msg = has_database_access(test_username, test_password)
    print(f"   Result: {msg} (User ID: {returned_id})")
    
    if not granted or returned_id != user_id:
        print("   FAILED: Valid login did not work")
        return
    
    # Test 3: Invalid password
    print("\n3. Testing invalid password...")
    granted, returned_id, msg = has_database_access(test_username, "WrongPassword")
    print(f"   Result: {msg}")
    
    if granted:
        print("   FAILED: Invalid password was accepted")
        return
    
    # Test 4: Non-existent user
    print("\n4. Testing non-existent user...")
    granted, returned_id, msg = has_database_access("nonexistent_user", "anypass")
    print(f"   Result: {msg}")
    
    if granted:
        print("   FAILED: Non-existent user was accepted")
        return
    
    print("\n=== All Tests Passed! ===\n")
