import getpass
from model import A as route_model
import database


database.ensure_tables()
database.seed_default_route_data()


def login():
    print("\n--- Existing User Login ---")
    userid = input("Enter your user ID: ").strip()
    password = getpass.getpass("Enter your password: ").strip()
    if database.user_exists(userid, password):
        print(f"Welcome back, {userid}!")
        return userid
    print("Invalid user ID or password.")
    return None


def newuser():
    print("\n--- New User Registration ---")
    name = input("Enter your name: ").strip()
    userid = input("Create a user ID: ").strip()
    password = getpass.getpass("Create a password: ").strip()
    phone = input("Enter your phone number: ").strip()

    database.insert_user(name, userid, password, phone)
    print(f"Thank you for registering, {name}!")
    return userid


def route_search(user_id):
    print("\n--- A* Shortest Route Finder ---")
    start_input = input("Enter starting node code or name: ").strip()
    destination_input = input("Enter destination node code or name: ").strip()

    route = route_model.find_route(start_input, destination_input)
    if route is None:
        print("No route found. Please check the start and destination values.")
        return

    print("\nShortest route found:")
    for index, node in enumerate(route["path"], start=1):
        print(f"{index}. {node['code']} - {node['name']}")
    print(f"Total distance: {route['total_distance']}")

    path_text = " -> ".join(node["code"] for node in route["path"])
    database.insert_route_history(user_id, route["path"][0]["code"], route["path"][-1]["code"], path_text, route["total_distance"])
    print("Route has been saved to history.")


def view_saved_routes(user_id):
    print("\n--- Your Saved Routes ---")
    cursor = database.get_cursor()
    cursor.execute(
        "SELECT id, start_node, destination_node, path, total_distance, created_at FROM route_history WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    routes = cursor.fetchall()
    if not routes:
        print("No saved routes found.")
        return

    for route in routes:
        print(f"[{route['id']}] {route['start_node']} -> {route['destination_node']} | {route['total_distance']} | {route['created_at']}")
        print(f"    Path: {route['path']}")


def show_node_coordinates():
    print("\n--- Node Coordinates ---")
    nodes = database.get_all_nodes()
    if not nodes:
        print("No nodes available.")
        return

    print(f"{'Code':<6} {'Name':<25} {'Type':<10} {'X':>6} {'Y':>6}")
    print("-" * 55)
    for node in nodes:
        print(f"{node['node_code']:<6} {node['node_name']:<25} {node['node_type']:<10} {node['coord_x']:>6.1f} {node['coord_y']:>6.1f}")


def main_menu(user_id):
    while True:
        print("\n--- Main Menu ---")
        print("1. Find shortest route")
        print("2. View saved routes")
        print("3. Show node coordinates")
        print("4. Logout")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            route_search(user_id)
        elif choice == "2":
            view_saved_routes(user_id)
        elif choice == "3":
            show_node_coordinates()
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, or 4.")


while True:
    print("\n🚗 Welcome to Fuel Service")
    print("1. Login (L)")
    print("2. New User (N)")
    choice = input("Enter your choice: ").upper()

    if choice == "L":
        user_id = login()
        if user_id:
            main_menu(user_id)
            break

    elif choice == "N":
        new_user_id = newuser()
        if new_user_id:
            print("You can now log in with your new account.")

    else:
        print("❌ Invalid choice. Please select L or N.")

