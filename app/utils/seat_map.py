def generate_seat_map(rows=10, seats_per_row=10):
    """
    Génère automatiquement un plan de salle.
    Exemple : A1-A10, B1-B10, ..., J1-J10

    rows = nombre de rangées (A, B, C...)
    seats_per_row = nombre de sièges par rangée
    """
    seat_map = []

    for row_index in range(rows):
        row_letter = chr(ord('A') + row_index)  # A, B, C...
        for seat_number in range(1, seats_per_row + 1):
            seat_map.append(f"{row_letter}{seat_number}")

    return seat_map
