import csv
import os
import datetime
from rich.console import Console
from rich.table import Table

console = Console()

grocery_items = []

def load_grocery_items():
    grocery_items = []
    with open("C:/Users/NAOMI NADDYB/3D Objects/Tracker/Tracker/Tracker/grocery_items.csv", mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['Expiration Date'] = datetime.datetime.strptime(row['Expiration Date'], "%d/%m/%Y").strftime("%d/%m/%Y")
            grocery_items.append(row)
    return grocery_items

def write_grocery_items(grocery_items):
    with open("grocery_items.csv", mode='w', newline='') as file:
        fieldnames = ["Name", "Category", "Price", "Quantity", "Expiration Date"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in grocery_items:
            writer.writerow(item)

def display_current_stock():
    # Reload grocery items from the updated file
    grocery_items = load_grocery_items()

    if grocery_items:
        table = Table(title="Current Stock of Grocery Items")
        table.add_column("Name", justify="left", style="cyan")
        table.add_column("Category", style="magenta")
        table.add_column("Quantity", style="green")
        table.add_column("Price", style="blue")

        for item in grocery_items:
            table.add_row(
                item["Name"],
                item["Category"],
                str(item["Quantity"]),
                f"${item['Price']}"
            )

        console.print(table)
    else:
        console.print("No items found in the grocery inventory.")


def adjust_groceries():
    global grocery_items
    
    # Load grocery items
    grocery_items = load_grocery_items()
    
    console.print("\nUpdate Groceries:")
    product_name = input("Enter the name of the product: ").strip().capitalize()
    quantity_change = int(input("Enter the quantity to add (positive) or remove (negative): "))

    found = False
    for item in grocery_items:
        if item['Name'].capitalize() == product_name:
            current_quantity = int(item['Quantity'])
            new_quantity = current_quantity + quantity_change
            if new_quantity < 0:
                console.print("Error: Cannot remove more items than available.")
                return
            item['Quantity'] = str(new_quantity)
            console.print(f"Quantity of {product_name} updated. New Quantity: {new_quantity}")
            found = True
            break
    if not found:
        console.print("Product not found.")

    # Write grocery items back to file
    write_grocery_items(grocery_items)  # Pass grocery_items as an argument

load_grocery_items()

