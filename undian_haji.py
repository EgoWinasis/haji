import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import pygame
import mysql.connector
from mysql.connector import Error

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ego21041003!',
    'database': 'haji_db'
}

# Connect to MySQL database
try:
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Error connecting to database: {err}")
    db = None
    cursor = None

# Initialize pygame mixer for sound
pygame.mixer.init()

# List to keep track of winners
winners = []
names_list = []


def fetch_winners_from_db():
    global winners
    if cursor:
        cursor.execute("SELECT winner FROM winners")
        result = cursor.fetchall()
        # Add winners to the list in the order they appear in the database
        winners = [row[0] for row in result]  
        print("Winners loaded from database:")
    else:
        print("Database not connected. Starting with an empty winners list.")


# Fetch names from the database
def fetch_names_from_db():
    global names_list
    if cursor:
        cursor.execute("SELECT name FROM participant")  # Adjust to match your table structure
        result = cursor.fetchall()
        names_list = [row[0] for row in result]
        print("Names loaded from database:")
    else:
        print("Database not connected. Starting with an empty names list.")

# Save a winner to the database
def save_winner_to_db(winner_name):
    if cursor and db:
        try:
            cursor.execute("INSERT INTO winners (winner) VALUES (%s)", (winner_name,))
            db.commit()
        except mysql.connector.Error as err:
            print(f"Error saving winner to database: {err}")

# Initialize names and winners from database
fetch_names_from_db()
fetch_winners_from_db()

# Global shuffle time variable (in seconds)
shuffle_time = 0.05  # Default shuffle time

# Function to pick and animate a winner
# Function to pick and animate a winner
def start_doorprize():
    global shuffle_time  # Ensure to use the global shuffle_time

    # Disable the start button during the animation
    start_button.config(state=tk.DISABLED)

    # Total animation time in seconds
    total_animation_time = 10  

    # Calculate the number of shuffles
    number_of_shuffles = int(total_animation_time / shuffle_time)

    # Shuffle the names quickly for animation
    for _ in range(number_of_shuffles):  # Run the shuffle for the calculated number of iterations
        random_name = random.choice(names_list)
        name_var.set(random_name)
        play_counting_sound()
        root.update()
        time.sleep(shuffle_time)

    # Pick a final winner
    final_name = random.choice(names_list)

    # Ensure the final name is not already a winner
    while final_name in winners:
        final_name = random.choice(names_list)

    # Add to winners and save to database
    # winners.add(final_name)
    
    winners.append(final_name)
    save_winner_to_db(final_name)
    # Update the displayed name
    name_var.set(final_name)

    # Play winner sound
    play_winner_sound()

    # Highlight the final winner
    flicker_final_name()

    # Re-enable the start button
    start_button.config(state=tk.NORMAL)


# Function to play the counting sound
def play_counting_sound():
    try:
        pygame.mixer.music.load("sound/count.wav")
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing counting sound: {e}")

# Function to play the winner sound
def play_winner_sound():
    try:
        pygame.mixer.music.load("sound/winner.wav")
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound: {e}")

# Function to flicker the final name for emphasis
def flicker_final_name():
    for _ in range(10):  # Flicker 10 times
        name_label.config(fg="red")
        root.update()
        time.sleep(0.1)
        name_label.config(fg="black")
        root.update()
        time.sleep(0.1)

# Function to open a new window showing the winner history
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Winner History")
    history_window.geometry("300x400")

    history_label = tk.Label(history_window, text="History of Winners", font=("Helvetica", 18))
    history_label.pack(pady=10)

    history_listbox = tk.Listbox(history_window, font=("Helvetica", 14), fg="black", width=20, height=10, bg="white")
    history_listbox.pack(padx=10, pady=10)

    for winner in winners:
        history_listbox.insert(tk.END, winner)

# Function to close the application
def close_app():
    root.quit()

# Function to open the settings window and modify the max number and shuffle time
def open_settings():
    # Create a new settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x300")

    # Label for shuffle time input
    shuffle_time_label = tk.Label(settings_window, text="Shuffle Time (ms):", font=("Helvetica", 14))
    shuffle_time_label.pack(pady=10)

    # OptionMenu for selecting shuffle time
    shuffle_time_options = [50, 100, 150, 200]  # shuffle time options in milliseconds
    shuffle_time_var = tk.StringVar(settings_window)
    shuffle_time_var.set(str(int(shuffle_time * 1000)))  # Convert to milliseconds for the OptionMenu
    shuffle_time_menu = tk.OptionMenu(settings_window, shuffle_time_var, *shuffle_time_options)
    shuffle_time_menu.pack(pady=10)

    # Function to save the new settings
    def save_settings():
        global shuffle_time
        shuffle_time_ms = int(shuffle_time_var.get())  # Get shuffle time in ms
        shuffle_time = shuffle_time_ms / 1000.0  # Convert back to seconds for the main program
        settings_window.destroy()  # Close settings window

    # Save button
    save_button = tk.Button(settings_window, text="Save", font=("Helvetica", 14), command=save_settings)
    save_button.pack(pady=20)


# Create the main window
root = tk.Tk()
root.attributes("-fullscreen", True)

# Load the original background image
bg_image = Image.open("image/bg_center.png")
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create a StringVar for the winner name
name_var = tk.StringVar(value="NAME")  # Set initial value to "NAME"

# Create a label to display the winner name
name_label = tk.Label(root, textvariable=name_var, font=("Helvetica", 40), fg="black", bg="white")
name_label.place(relx=0.24, rely=0.5, anchor="center")

# Set up the start button
start_button = tk.Button(root, text="START", font=("Helvetica", 32), command=start_doorprize, bg="green", fg="white")
start_button.place(relx=0.24, rely=0.65, anchor="center")

# Exit button
exit_image = Image.open("image/close2.png")
exit_photo = ImageTk.PhotoImage(exit_image)
exit_button = tk.Button(root, image=exit_photo, command=close_app, borderwidth=0, relief="flat", highlightthickness=0)
exit_button.place(relx=0.95, rely=0.05, anchor="center")

# History button
history_image = Image.open("image/winner.png")
history_photo = ImageTk.PhotoImage(history_image)
history_button = tk.Button(root, image=history_photo, command=show_history, borderwidth=0, relief="flat", highlightthickness=0)
history_button.place(relx=0.91, rely=0.05, anchor="center")

# Add a new "Settings" button (with icon)
settings_image = Image.open("image/setting.png")
settings_photo = ImageTk.PhotoImage(settings_image)
settings_button = tk.Button(root, image=settings_photo, command=open_settings, borderwidth=0, relief="flat", highlightthickness=0)
settings_button.place(relx=0.87, rely=0.05, anchor="center")

# Run the main loop
root.mainloop()

# Close the database connection on exit
if cursor:
    cursor.close()
if db:
    db.close()
