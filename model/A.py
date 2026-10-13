import heapq
import database


def heuristic(node_code, goal_code):
    start = database.get_node_coordinates(node_code)
    goal = database.get_node_coordinates(goal_code)

    if not start or not goal:
        return 0

    dx = start["coord_x"] - goal["coord_x"]
    dy = start["coord_y"] - goal["coord_y"]
    return (dx * dx + dy * dy) ** 0.5


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))


def find_route(start_input, destination_input):
    start_node = database.get_node_by_code_or_name(start_input)
    goal_node = database.get_node_by_code_or_name(destination_input)

    if not start_node or not goal_node:
        return None

    start_code = start_node["node_code"]
    goal_code = goal_node["node_code"]

    open_set = []
    heapq.heappush(open_set, (0, start_code))

    came_from = {}
    g_score = {start_code: 0}
    f_score = {start_code: heuristic(start_code, goal_code)}

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == goal_code:
            path_codes = reconstruct_path(came_from, current)
            path = []
            for code in path_codes:
                name = database.get_node_name(code)
                path.append({"code": code, "name": name})
            return {"path": path, "total_distance": g_score[current]}

        neighbors = database.get_neighbors(current)
        for neighbor in neighbors:
            neighbor_code = neighbor["neighbor"]
            distance = neighbor["distance"]
            tentative_g = g_score[current] + distance

            if tentative_g < g_score.get(neighbor_code, float("inf")):
                came_from[neighbor_code] = current
                g_score[neighbor_code] = tentative_g
                f_score[neighbor_code] = tentative_g + heuristic(neighbor_code, goal_code)
                heapq.heappush(open_set, (f_score[neighbor_code], neighbor_code))

    return None
