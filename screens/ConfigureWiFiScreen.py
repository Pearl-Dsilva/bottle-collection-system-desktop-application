import tkinter as tk
from tkinter import Canvas, messagebox, ttk
from PIL import Image, ImageTk
from screens import SettingsScreen
import threading

from utility import list_available_wifi
from main import WIFI_STATE


is_disabled = False  # Fix: Boolean are not threadsafe, encapsulate in class


# This function updates the Listbox in the main thread
def insert_into_listbox(
    wifi_listbox: tk.Listbox, available_networks: list, window: tk.Tk
):

    def update_listbox(wifi_listbox: tk.Listbox, available_networks: list):
        wifi_listbox.delete(0, tk.END)  # Clear the listbox
        if not available_networks:
            wifi_listbox.insert(tk.END, "No Wi-Fi networks found.")
        else:
            print(f"Available Networks: {len(available_networks)}")
            for network in available_networks:
                print(f"Got Network: {network}")
                wifi_listbox.insert(tk.END, network)

    # Schedule the update to happen in the main thread
    window.after(
        100,
        update_listbox,
        wifi_listbox,
        available_networks,
    )


def on_wifi_selected(event, listbox: tk.Listbox):
    # Get the index of the clicked item
    selected_index: int = listbox.curselection()

    if selected_index:
        # Get the item at the selected index
        selected_item = listbox.get(selected_index)
        # Trigger an action based on the selected item (e.g., show a message)
        messagebox.showinfo("Item Clicked", f"You clicked: {selected_item}")


# This function shows the loading indicator while fetching the Wi-Fi networks
def show_loading_indicator(canvas: Canvas, window: tk.Tk, wifi_listbox: tk.Listbox):
    global is_disabled
    # Create and place a loading indicator (progress bar)
    loading_text = ttk.Progressbar(
        window, orient="horizontal", mode="indeterminate", length=280
    )
    loading_text.place(x=260, y=240)  # Place it on the canvas
    loading_text.start()  # Start the progress bar animation
    canvas.update()

    # Disable all user interactions except for the progress bar
    is_disabled = True
    wifi_listbox.config(state="disabled")

    return loading_text


# This function hides the loading indicator once Wi-Fi networks are loaded
def hide_loading_indicator(
    loading_text: ttk.Progressbar, window: tk.Tk, wifi_listbox: tk.Listbox
):
    global is_disabled
    # Stop the progress bar animation and hide it
    loading_text.stop()
    loading_text.place_forget()  # Remove the progress bar from the window

    # Re-enable all user interactions
    is_disabled = False
    wifi_listbox.config(state="normal")


# This function handles the Wi-Fi list reload when the refresh button is clicked
def reload_button_handler(wifi_listbox, canvas, window):
    if is_disabled:
        return

    loading_text = show_loading_indicator(canvas, window, wifi_listbox)

    # Load Wi-Fi networks in a separate thread
    def load_wifi_networks():
        try:
            available_networks = list_available_wifi(
                True
            )  # Fetch the available Wi-Fi networks
            # Once the networks are fetched, update the listbox
            window.after(
                0, insert_into_listbox, wifi_listbox, available_networks, window
            )
        finally:
            hide_loading_indicator(
                loading_text, window, wifi_listbox
            )  # Always hide the loading indicator

    # Start the loading in a separate thread
    threading.Thread(target=load_wifi_networks, daemon=True).start()


# This function is responsible for creating the Wi-Fi screen with the canvas, listbox, and buttons
def configureWIFIScreen(window: tk.Tk, application_state: dict):
    wifi_connected = Image.open("./assets/connected.png")
    wifi_disconnected = Image.open("./assets/not-connected.png")
    refresh = Image.open("./assets/reload.png")
    back = Image.open("./assets/back.png")

    connected_image = ImageTk.PhotoImage(wifi_connected)
    not_connected_image = ImageTk.PhotoImage(wifi_disconnected)

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=480,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge",
    )
    canvas.place(x=0, y=0)

    canvas.create_text(
        269.0,
        19.0,
        anchor="nw",
        text="Name | Logo",
        fill="#000000",
        font=("Kadwa Bold", 30),
    )

    canvas.create_text(
        250.0,
        70.0,
        anchor="nw",
        text="Select a Wi-Fi network",
        fill="#515050",
        font=("Kadwa Regular", 20),
    )

    canvas.create_text(
        701.0,
        15.0,
        anchor="nw",
        text=((application_state.get("WIFI")).value),
        fill="#515050",
        font=("Kadwa Regular", 10),
    )

    # Load Wi-Fi connection images
    canvas.create_image(
        677,
        10,
        anchor=tk.NW,
        image=(
            connected_image
            if application_state.get("WIFI") == WIFI_STATE.CONNECTED
            else not_connected_image
        ),
    )

    canvas.image2 = connected_image
    canvas.image3 = not_connected_image

    # Back button to go to Settings screen
    back_image = ImageTk.PhotoImage(back)
    back_button = tk.Label(
        window,
        image=back_image,
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        bg="#FFFFFF",
        padx=10,
        pady=10,
    )
    back_button.bind(
        "<Button-1>",
        lambda _: (
            SettingsScreen.SettingsScreen(window, application_state)
            if not is_disabled
            else None
        ),
    )
    back_button.image = back_image
    back_button.place(x=66, y=81)

    # Create a listbox to display the networks
    wifi_listbox = tk.Listbox(
        window, font=("Kadwa Regular", 18), width=50, height=10, selectmode=tk.SINGLE
    )

    # Refresh Button
    refresh_image = ImageTk.PhotoImage(refresh)
    refresh_button = tk.Label(
        window,
        image=refresh_image,
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        bg="#FFFFFF",
        padx=10,
        pady=10,
    )
    refresh_button.bind(
        "<Button-1>",
        lambda _: reload_button_handler(wifi_listbox, canvas, window),
    )
    refresh_button.image = refresh_image
    refresh_button.place(x=700, y=81)

    # Load initial Wi-Fi networks
    insert_into_listbox(wifi_listbox, list_available_wifi(False), window)

    wifi_listbox.bind(
        "<ButtonRelease-1>", lambda event: on_wifi_selected(event, wifi_listbox)
    )
    wifi_listbox.place(x=80, y=150)

    return canvas
