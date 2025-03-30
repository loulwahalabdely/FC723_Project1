# Initialize storage area seats
storage_areas = {"77D", "77E", "77F", "78D", "78E", "78F"}

# Set to track reserved seats
reserved_seats = set()

#Validate and parse seat input into row and column components

def get_valid_seat(seat_input):
    seat_input = seat_input.strip().upper()
    if 2 <= len(seat_input) <= 3:
        if len(seat_input) == 2:
            row_str, col = seat_input[0], seat_input[1]
        else:
            row_str, col = seat_input[:2], seat_input[2]
        
        if row_str.isdigit() and col in "ABCDEF":
            row = int(row_str)
            if 1 <= row <= 80:
                return row, col
    return None, None

meal_options = {
    "1": "Standard Meal",
    "2": "Light Meal", 
    "3": "Vegetarian Meal",
    "4": "Vegan Meal"
}

passenger_meals = {}  # Stores seat meal choice

#Handle meal selection process for reserved seats.

def meal_selection():
    while True:
        seat_code = input("\nEnter your reserved seat number (e.g., 15F): ").strip().upper()
        row, col = get_valid_seat(seat_code)
        
        if row is None:
            print("Invalid seat format! Use format like 1A or 80F")
            continue
            
        seat_id = f"{row}{col}"
        
        if seat_id not in reserved_seats:
            print("Seat not reserved. Please book first.")
            return
            
        print("\nMeal Selection Menu")
        print("1. Standard\n2. Light\n3. Vegetarian\n4. Vegan")
        choice = input("Choose meal (1-4) or 'X' to cancel: ").upper()
        
        if choice == "X":
            print("Meal selection cancelled.")
            return
            
        selected = meal_options.get(choice)
        if selected:
            passenger_meals[seat_id] = selected
            print(f"{selected} confirmed for seat {seat_id}")
            break
            
        print("Invalid choice. Please select 1-4")

#Check and display the status of a specified seat.
def check_availability():
    while True:
        seat_code = input("\nEnter seat to check (e.g., 3A): ")
        row, col = get_valid_seat(seat_code)
        
        if row is None:
            print("Invalid format. Use format like 1A or 80F.")
            break
            
        seat_id = f"{row}{col}"
        
        if seat_id in reserved_seats:
            status = "Booked"
        elif seat_id in storage_areas:
            status = "Storage Area"
        else:
            status = "Available"
        
        print(f"Seat {seat_id}: {status}")
        break

#Handle seat reservation process.

def book_seat():
    while True:
        seat_code = input("\nEnter seat to reserve (e.g., 5C): ")
        row, col = get_valid_seat(seat_code)
        
        if row is None:
            print("Invalid seat code.")
            return
            
        seat_id = f"{row}{col}"
        
        if seat_id in storage_areas:
            print("Cannot book storage seat.")
            continue
            
        if seat_id in reserved_seats:
            print("Seat already booked.")
            continue
            
        reserved_seats.add(seat_id)
        print(f"Successfully reserved seat {seat_id}!")
        break

# checks that the seat is valid and frees the booking if these conditions are met.

def free_seat():
    while True:
        seat_code = input("\nEnter seat to free (e.g., 15B): ")
        row, col = get_valid_seat(seat_code)
        
        if row is None:
            print("Invalid seat code.")
            break
            
        seat_id = f"{row}{col}"
        
        if seat_id not in reserved_seats:
            print("No matching booking found.")
            continue
            
        reserved_seats.remove(seat_id)
        if seat_id in passenger_meals:
            del passenger_meals[seat_id]
        print(f"Released seat {seat_id} and cleared meal preference.")
        break
    
#Displays the seating map of the whole airplane.

def show_booking_status():
    print("\n Flight Seat Map ")
    print("Legend: [Seat#] Available, [R] Reserved, [S] Storage, [X] Aisle\n")
    
    for row_num in range(1, 81):
        # Determine fuselage shape based on row position
        if row_num < 15:
            left_border = "◢ "
            right_border = " ◣"
        elif 15 <= row_num <= 65:
            left_border = "‖ "
            right_border = " ‖"
        else:
            left_border = "◥ "
            right_border = " ◤"

        seat_row = []
        for col in "ABCXDEF":
            seat_id = f"{row_num}{col}"
            
            # Determine seat status
            if col == "X":
                seat_status = "X"
            elif seat_id in reserved_seats:
                seat_status = "R"
            elif seat_id in storage_areas:
                seat_status = "S"
            else:
                seat_status = seat_id

            seat_row.append(f"{seat_status:<4}")

        # Assemble the complete row with borders
        formatted_row = f"{left_border}{''.join(seat_row)}{right_border}"
        print(formatted_row)
        
    print("\nFront of Aircraft".center(38))
    
#Display system menu options

def show_menu():
    print("\n==== Apache Airlines ====")
    print("1. Check seat availability")
    print("2. Book seat")
    print("3. Free seat") 
    print("4. Show Booking Status")
    print("5. Meal Selection")
    print("6. Exit System")

# Main program loop
while True:
    show_menu()
    action = input("Enter option (1-6): ")
    
    if action == "1":
        check_availability()
    elif action == "2":
        book_seat()
    elif action == "3":
        free_seat()
    elif action == "4":
        show_booking_status()
    elif action == "5":
        meal_selection()
    elif action == "6":
        print("Thank you for flying with Apache Airlines!")
        break
    else:
        print("Invalid option. Please choose 1-6.")
