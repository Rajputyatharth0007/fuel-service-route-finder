import os
import mysql.connector


def _load_env_file():
    """Load key-value pairs from a local .env file if present, without external dependencies."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass


_load_env_file()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME") or os.getenv("DB_DATABASE", "fuel_service")
DB_PORT = os.getenv("DB_PORT", "3306")

if not DB_PASSWORD:
    raise ValueError(
        "Database configuration error: Missing required environment variable 'DB_PASSWORD' (or 'DB_PASS'). "
        "Please configure DB_PASSWORD in your environment or local .env file."
    )

try:
    port_num = int(DB_PORT)
except ValueError:
    port_num = 3306

connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    passwd=DB_PASSWORD,
    database=DB_NAME,
    port=port_num
)


def get_cursor(dictionary=True):
    return connection.cursor(dictionary=dictionary)


def insert_user(name, userid, password, phone):
    query = "INSERT INTO users (name, userid, password, phone) VALUES (%s, %s, %s, %s)"
    values = (name, userid, password, phone)
    cursor = get_cursor()
    cursor.execute(query, values)
    connection.commit()


def user_exists(userid, password):
    query = "SELECT 1 FROM users WHERE userid = %s AND password = %s"
    cursor = get_cursor()
    cursor.execute(query, (userid, password))
    result = cursor.fetchone()
    return result is not None


def get_node_by_code_or_name(value):
    query = """
        SELECT node_code, node_name, node_type, coord_x, coord_y
        FROM node_list
        WHERE node_code = %s OR node_name = %s
    """
    cursor = get_cursor()
    cursor.execute(query, (value, value))
    return cursor.fetchone()


def table_has_column(table, column):
    query = """
        SELECT COUNT(*) AS cnt
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
    """
    cursor = get_cursor()
    cursor.execute(query, (table, column))
    result = cursor.fetchone()
    return bool(result and result["cnt"] > 0)


def ensure_tables():
    cursor = get_cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            userid VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            phone VARCHAR(50) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS node_list (
            node_code VARCHAR(10) PRIMARY KEY,
            node_name VARCHAR(100) NOT NULL,
            node_type VARCHAR(20) NOT NULL,
            coord_x FLOAT DEFAULT NULL,
            coord_y FLOAT DEFAULT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS edge (
            source_node VARCHAR(10) NOT NULL,
            destination_node VARCHAR(10) NOT NULL,
            distance FLOAT NOT NULL,
            PRIMARY KEY (source_node, destination_node),
            FOREIGN KEY (source_node) REFERENCES node_list(node_code) ON DELETE CASCADE,
            FOREIGN KEY (destination_node) REFERENCES node_list(node_code) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS route_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            start_node VARCHAR(10) NOT NULL,
            destination_node VARCHAR(10) NOT NULL,
            path TEXT NOT NULL,
            total_distance FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()


def is_node_list_empty():
    cursor = get_cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM node_list")
    result = cursor.fetchone()
    return result and result["cnt"] == 0


def seed_default_route_data():
    if not is_node_list_empty():
        return

    nodes = [
        ("N001", "Stair 1", "STAIR", -12.0, 0.0),
        ("N002", "Room 309", "ROOM", -12.0, 5.0),
        ("N003", "Room 310", "ROOM", -12.0, 12.0),
        ("N004", "Room 311", "ROOM", -12.0, 20.0),
        ("N005", "Stair 2", "STAIR", -12.0, 28.0),
        ("N006", "Room 312", "ROOM", -12.0, 36.0),
        ("N007", "Room 313", "ROOM", -12.0, 44.0),
        ("N008", "Room 314", "ROOM", -12.0, 53.0),
        ("N009", "Room 316 Left", "ROOM", -12.0, 61.0),
        ("N010", "Stair 3", "STAIR", -12.0, 71.0),

        ("N011", "Room 315 Left", "ROOM", 8.0, 8.0),
        ("N012", "Entry Point / QR", "ENTRY", 8.0, 0.0),
        ("N013", "Boys Washroom", "WASHROOM", 12.0, 4.5),
        ("N014", "Office", "OFFICE", 16.0, 9.5),
        ("N015", "Room 315 Right", "ROOM", 20.0, 12.5),
        ("N016", "Room 316 Right", "ROOM", 24.0, 16.5),
        ("N017", "Main Stairs", "STAIR", 8.0, 12.0),
        ("N018", "Sitting Area", "AREA", 11.0, 14.5),
        ("N019", "Girls Washroom", "WASHROOM", 14.0, 17.5),
        ("N020", "Staff Room", "STAFF", 17.0, 20.5),
        ("N021", "Room 304", "ROOM", 17.0, 22.5),
        ("N022", "Room 305", "ROOM", 20.5, 22.5),
        ("N023", "Lab 300", "LAB", 14.0, 22.5),
        ("N024", "Lab 303", "LAB", 20.5, 24.5),
    ]

    edges = [
        ("N001", "N002", 5),
        ("N002", "N001", 5),
        ("N002", "N003", 7),
        ("N003", "N002", 7),
        ("N003", "N004", 8),
        ("N004", "N003", 8),
        ("N004", "N005", 8),
        ("N005", "N004", 8),
        ("N005", "N006", 8),
        ("N006", "N005", 8),
        ("N006", "N007", 8),
        ("N007", "N006", 8),
        ("N007", "N008", 9),
        ("N008", "N007", 9),
        ("N008", "N009", 8),
        ("N009", "N008", 8),
        ("N009", "N010", 10),
        ("N010", "N009", 10),
        ("N012", "N013", 5),
        ("N013", "N012", 5),
        ("N013", "N014", 5),
        ("N014", "N013", 5),
        ("N014", "N015", 3),
        ("N015", "N014", 3),
        ("N015", "N016", 4),
        ("N016", "N015", 4),
        ("N012", "N017", 12),
        ("N017", "N012", 12),
        ("N017", "N018", 2),
        ("N018", "N017", 2),
        ("N018", "N019", 3),
        ("N019", "N018", 3),
        ("N019", "N020", 3),
        ("N020", "N019", 3),
        ("N020", "N021", 2),
        ("N021", "N020", 2),
        ("N021", "N022", 3),
        ("N022", "N021", 3),
        ("N021", "N023", 2),
        ("N023", "N021", 2),
        ("N022", "N024", 2),
        ("N024", "N022", 2),
    ]

    insert_nodes(nodes)
    insert_edges(edges)


def insert_nodes(nodes):
    query = """
        INSERT INTO node_list (node_code, node_name, node_type, coord_x, coord_y)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            node_name = VALUES(node_name),
            node_type = VALUES(node_type),
            coord_x = VALUES(coord_x),
            coord_y = VALUES(coord_y)
    """
    cursor = get_cursor()
    cursor.executemany(query, nodes)
    connection.commit()


def insert_edges(edges):
    query = """
        INSERT INTO edge (source_node, destination_node, distance)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE distance = VALUES(distance)
    """
    cursor = get_cursor()
    cursor.executemany(query, edges)
    connection.commit()


def insert_route_history(user_id, start_node, destination_node, path, total_distance):
    query = """
        INSERT INTO route_history (user_id, start_node, destination_node, path, total_distance)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor = get_cursor()
    cursor.execute(query, (user_id, start_node, destination_node, path, total_distance))
    connection.commit()


def get_all_nodes():
    cursor = get_cursor()
    cursor.execute("SELECT node_code, node_name, node_type, coord_x, coord_y FROM node_list ORDER BY node_code")
    return cursor.fetchall()


def get_node_name(node_code):
    query = "SELECT node_name FROM node_list WHERE node_code = %s"
    cursor = get_cursor()
    cursor.execute(query, (node_code,))
    result = cursor.fetchone()
    return result["node_name"] if result else None


def get_node_coordinates(node_code):
    if not table_has_column("node_list", "coord_x") or not table_has_column("node_list", "coord_y"):
        return None

    query = "SELECT coord_x, coord_y FROM node_list WHERE node_code = %s"
    cursor = get_cursor()
    cursor.execute(query, (node_code,))
    result = cursor.fetchone()
    return result if result else None


def get_neighbors(node_code):
    query = """
        SELECT destination_node AS neighbor, distance
        FROM edge
        WHERE source_node = %s
        UNION
        SELECT source_node AS neighbor, distance
        FROM edge
        WHERE destination_node = %s
    """
    cursor = get_cursor()
    cursor.execute(query, (node_code, node_code))
    return cursor.fetchall()
