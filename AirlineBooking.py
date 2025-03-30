import sqlite3
import random
import string
from contextlib import closing

# Database name
DB_NAME = "airline.db"
STORAGE_SEATS = {"77D", "77E", "77F", "78D", "78E", "78F"}

#Initialize database with single table

def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (ref TEXT PRIMARY KEY,
                      first TEXT NOT NULL,
                      last TEXT NOT NULL,
                      passport TEXT NOT NULL,
                      seat TEXT NOT NULL UNIQUE,
                      meal TEXT)''')
        conn.commit()
        
#Validate seat format and return formatted seat ID
def get_valid_seat(seat_input):

    while True:
        seat = input(seat_input).strip().upper()
        if len(seat) < 2 or not seat[:-1].isdigit() or seat[-1] not in "ABCDEF":
            print("Invalid seat format (e.g., 1A or 80F)")
            continue
        row = int(seat[:-1])
        if 1 <= row <= 80:
            return f"{row}{seat[-1]}"
        print("Row must be 1-80")

# Database initialization, it creates a new db if there isn't one but doesn't replace the old one.
init_db()


#def used to generate unique 8-character booking reference

def generate_ref():
    chars = string.ascii_uppercase + string.digits
    with closing(sqlite3.connect(DB_NAME)) as conn:
        while True:
            ref = ''.join(random.choices(chars, k=8))
            cursor = conn.execute("SELECT ref FROM bookings WHERE ref=?", (ref,))
            if not cursor.fetchone():
                return ref


#Check if seat is available by querying the db
def check_availability():
    seat = get_valid_seat("Enter seat to check (e.g., 3A): ")
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.execute("SELECT 1 FROM bookings WHERE seat=?", (seat,))
        if cursor.fetchone():
            status = "Booked"
        elif seat in STORAGE_SEATS:
            status = "Storage Area"
        else:
            status = "Available"
    print(f"Seat {seat}: {status}")
    
#Book a seat with passenger details, and makes the change to the database
def book_seat():
    seat = get_valid_seat("Enter seat to reserve (e.g., 5C): ")

    if seat in STORAGE_SEATS:
        print("Cannot book storage seat")
        return
    
    with closing(sqlite3.connect(DB_NAME)) as conn:
        if conn.execute("SELECT seat FROM bookings WHERE seat=?", (seat,)).fetchone():
            print("Seat already booked")
            return
        
        print("Enter passenger details:")
        first = input("First name: ").strip().upper()
        last = input("Last name: ").strip().upper()
        passport = input("Passport: ").strip().upper()
        
        ref = generate_ref()
        conn.execute('''INSERT INTO bookings 
                     VALUES (?,?,?,?,?,NULL)''',
                  (ref, first, last, passport, seat))
        conn.commit()
        print(f"Booked {seat}! Reference: {ref}")


# Takes the user's last name for security, and checks that the seat is valid and frees the booking if these conditions are met.
def free_seat():
    seat = get_valid_seat("Enter seat to free (e.g., 15B): ")

    last = input("Enter last name for verification: ").strip().upper()
    
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.execute('''DELETE FROM bookings 
                              WHERE seat=? AND last=?
                              RETURNING ref''', (seat, last))
        if cursor.fetchone():
            conn.commit()
            print(f"Released seat {seat} and cleared meal preference")
        else:
            print("No matching booking found")

#Displays the passenger details given their last name and the seating map of the whole airplane.

def show_booking_status():
    try:
        with closing(sqlite3.connect(DB_NAME)) as conn:
            last_name = input("\nEnter last name to view details (or press Enter to skip): ").strip().upper()
            c = conn.cursor()

            if last_name:
                c.execute('''SELECT b.ref, b.first, b.last, b.seat, b.meal
                          FROM bookings b
                          WHERE b.last=?''', (last_name,))
                results = c.fetchall()
            
            c.execute("SELECT seat, ref FROM bookings")
            booked_seats = {row[0]: row[1] for row in c.fetchall()}
            

            if not results:
                print(f"No bookings found for {last_name}")
            else:
                print("\nPassenger Details:")
                for ref, first, last, seat, meal in results:
                    print(f"Booking Ref: {ref}")
                    print(f"Passenger: {first} {last}")
                    print(f"Seat: {seat}")
                    print(f"Meal: {meal if meal else 'Not selected'}")
                    print("-" * 30)
                
            print("\nFlight Seat Map:")
            print("Legend: [Seat#] Available, [R] Reserved, [S] Storage, [X] Aisle")
            
            for row in range(1, 81):
                borders = ("◢ ", " ◣") if row < 15 else \
                         ("‖ ", " ‖") if row <=65 else \
                         ("◥ ", " ◤")
                
              
                seats = []
                for col in "ABCXDEF":
                    seat_id = f"{row}{col}"
                    if col == "X":
                        seats.append(" X  ")  # Aisle
                    elif seat_id in STORAGE_SEATS:
                        seats.append(" S  ")  # Storage
                    elif seat_id in booked_seats:
                        seats.append(" R  ")  # Reserved 
                    else:
                        seats.append(f"{seat_id:<4}")  # Available seats
                
                # Assemble the complete row with borders
                formatted_row = f"{borders[0]}{''.join(seats)}{borders[1]}"
                print(formatted_row)
            
            print("\nFront of Aircraft".center(40))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
            

# Choose / Update meal choice for booking
def meal_selection():
    seat = get_valid_seat("Enter your reserved seat number (e.g., 15F): ")
    with closing(sqlite3.connect(DB_NAME)) as conn:
        # Get current meal choice
        cursor = conn.execute("SELECT meal FROM bookings WHERE seat=?", (seat,))
        result = cursor.fetchone()
        if not result:
            print("Seat not reserved. Please book first.")
            return
        
        print("\nMeal Selection Menu:")
        print("1. Standard\n2. Light\n3. Vegetarian\n4. Vegan")
        choice = input("Select meal (1-4) or 'X' to cancel: ").upper()
        
        if choice == "X":
            print("Meal selection cancelled.")
            return
        
        meals = {"1": "Standard", "2": "Light", 
                "3": "Vegetarian", "4": "Vegan"}
        meal = meals.get(choice, None)
        
        if meal:
            conn.execute("UPDATE bookings SET meal=? WHERE seat=?", (meal, seat))
            conn.commit()
            print(f"Meal updated to {meal}")
        else:
            print("Invalid choice. Please select 1-4")

def menu():
    print("\n=== Apache Airlines ===")
    print("1. Check seat availability")
    print("2. Book seat")
    print("3. Free seat")
    print("4. Show Booking Status")
    print("5. Meal selection")
    print("6. Exit")

# Main program loop
while True:
    menu()
    choice = input("Enter option (1-6): ")
    
    if choice == "1":
        check_availability()
    elif choice == "2":
        book_seat()
    elif choice == "3":
        free_seat()
    elif choice == "4":
        show_booking_status()
    elif choice == "5":
        meal_selection()
    elif choice == "6":
        print("Thank you for flying with Apache Airlines!")
        break
    else:
        print("Invalid choice. Please choose 1-6.")
