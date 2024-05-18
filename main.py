import datetime
from rich.console import Console
from grocery import load_grocery_items, display_current_stock, adjust_groceries, write_grocery_items
from search import search_product
import csv
from rich.table import Table
import os

# directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

marketplace1 = os.path.join(script_dir, "Marketplace-1.csv")
marketplace2 = os.path.join(script_dir, "Marketplace-2.csv")
marketplace3 = os.path.join(script_dir, "Marketplace-3.csv")

console = Console()

def track_expiring_soon():
    today = datetime.date.today()
    six_months_from_now = today + datetime.timedelta(days=30 * 6)

    # Load grocery items
    grocery_items = load_grocery_items()

    expiring_items = []
    for item in grocery_items:
        if 'Expiration Date' in item:
            expiration_date = datetime.datetime.strptime(item['Expiration Date'], "%d/%m/%Y").date()
            if today <= expiration_date <= six_months_from_now:
                expiring_items.append(item)

    if expiring_items:
        console.print("\nItems Expiring in the Next 6 Months:")
        for item in expiring_items:
            console.print(f"{item['Name']} - Expires on {item['Expiration Date']}")
    else:
        console.print("No items are expiring in the next 6 months.")


def compare_prices_for_product():
    global grocery_items
    grocery_items = load_grocery_items()
    product_name = input("Enter the name of the product to compare prices: ")

    marketplace_prices1 = {}
    marketplace_prices2 = {}
    marketplace_prices3 = {}

    with open(marketplace1, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            marketplace_prices1[row['Name']] = float(row['Price'])

    with open(marketplace2, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            marketplace_prices2[row['Name']] = float(row['Price'])

    with open(marketplace3, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            marketplace_prices3[row['Name']] = float(row['Price'])

    console.print(f"\nPrice Comparison for '{product_name}' with Marketplaces:")
    for item in grocery_items:
        if item['Name'].lower() == product_name.lower():
            price1 = marketplace_prices1.get(item['Name'], "Not Available")
            price2 = marketplace_prices2.get(item['Name'], "Not Available")
            price3 = marketplace_prices3.get(item['Name'], "Not Available")

            console.print(f"{item['Name']}: Our Price - ${item['Price']} | Marketplace 1 Price - ${price1} | Marketplace 2 Price - ${price2} | Marketplace 3 Price - ${price3}")
            return

    console.print(f"No product named '{product_name}' found in the current stock.")

def display_items_by_category():
    grocery_items = load_grocery_items()  # Load grocery items here
    category = input("Enter the category to display items: ").strip().capitalize()
    table = Table(title=f"Grocery Items in the Category '{category}'")
    table.add_column("Name")
    table.add_column("Quantity")
    table.add_column("Price")

    category_items = [item for item in grocery_items if item['Category'].capitalize() == category]
    if category_items:
        for item in category_items:
            table.add_row(item['Name'], item['Quantity'], f"${item['Price']}")
    else:
        console.print("No items found in the specified category.")

    console.print(table)
# Place_Order 

def place_order():
    total_cost = 0
    console.print("\nPlace an Order:")
    marketplace_number = input("Enter the marketplace number to order from: ")
    marketplace_file = os.path.join(script_dir, f"Marketplace-{marketplace_number}.csv")

    try:
        # Load grocery items from the selected marketplace CSV file
        with open(marketplace_file, mode='r') as file:
            reader = csv.DictReader(file)
            marketplace_items = list(reader)
    except FileNotFoundError:
        console.print(f"Error: Marketplace {marketplace_number} not found.")
        return

    num_items = int(input("Enter the number of items: "))
    ordered_items = []
    for i in range(num_items):
        item_name = input(f"Enter the name of item {i + 1}: ")
        quantity = int(input(f"Enter the quantity of {item_name}: "))

        # Check if the requested quantity is greater than the available quantity
        for item in marketplace_items:
            if item['Name'].lower() == item_name.lower():
                available_quantity = int(item['Quantity'])
                if quantity > available_quantity:
                    console.print(f"Error: The requested quantity ({quantity}) for '{item_name}' exceeds the available quantity ({available_quantity}).")
                    return

                total_cost += float(item['Price']) * quantity
                ordered_items.append({
                    'Name': item['Name'],
                    'Category': item['Category'],  
                    'Price': item['Price'],
                    'Quantity': str(quantity),  
                })
                break
        else:
            console.print(f"Error: '{item_name}' not found in the marketplace.")
            return

    console.print(f"\nTotal cost of the order from Marketplace {marketplace_number}: ${total_cost:.2f}")
    console.print("Order successfully placed.")

    # Write order details to ordered_items.csv
    ordered_items_file = os.path.join(script_dir, "ordered_items.csv")
    with open(ordered_items_file, mode='w', newline='') as file:
        fieldnames = ['Name', 'Category', 'Price', 'Quantity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for item in ordered_items:
            writer.writerow(item)

    console.print("Order details saved to ordered_items.csv.")
    display_ordered_items(ordered_items)

def display_ordered_items(ordered_items):
    console.print("Ordered Items:")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Price")
    table.add_column("Quantity")

    for item in ordered_items:
        table.add_row(item['Name'], item['Category'], item['Price'], item['Quantity'])

    console.print(table)

def copy_ordered_items_to_grocery():
    ordered_items = []
    ordered_items_file = os.path.join(script_dir, "ordered_items.csv")  
    try:
        with open(ordered_items_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ordered_items.append(row)
    except FileNotFoundError:
        console.print("No ordered items found.")
        return

    grocery_items = load_grocery_items()
    for ordered_item in ordered_items:
        found = False
        for grocery_item in grocery_items:
            if ordered_item['Name'] == grocery_item['Name']:
                # Update the quantity of existing item
                grocery_item['Quantity'] = str(int(grocery_item['Quantity']) + int(ordered_item['Quantity']))
                found = True
                break
        if not found:
            # Append the ordered item as a new entry
            grocery_items.append({
                'Name': ordered_item['Name'],
                'Category': ordered_item['Category'],
                'Quantity': ordered_item['Quantity'],
                'Price': ordered_item['Price']
            })

    write_grocery_items(grocery_items)
    console.print("Ordered items copied to grocery inventory.")

    # Refresh grocery_items.csv
    display_current_stock() 

def main():
    load_grocery_items()
    while True:
        console.print("\n")
        console.print("[bold green]Welcome to the Grocery Tracker App![/bold green]")
        console.print("Menu Options:")
        console.print("1. Display Current Stock")
        console.print("2. Search for a Product")
        console.print("3. Update Groceries")
        console.print("4. Track Expired Perishable Food Items")
        console.print("5. Price Comparison")
        console.print("6. Display Items by Category")
        console.print("7. Place Order")
        console.print("8. Exit")
        choice = input("Enter your choice: ")
        try:
            choice = int(choice)
            if choice == 1:
                display_current_stock()
            elif choice == 2:
                product_name = input("Enter the name of the product to search: ")
                search_product(product_name)
            elif choice == 3:
                adjust_groceries()
            elif choice == 4:
                track_expiring_soon()
            elif choice == 5:
                compare_prices_for_product()
            elif choice == 6:
                display_items_by_category()
            elif choice == 7:
                place_order()
                copy_ordered_items_to_grocery()
            elif choice == 8:
                console.print("\nThank you for using the Grocery Tracker App. Goodbye!")
                
                break
            else:
                console.print("Invalid choice. Please try again.")
        except ValueError:
            console.print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
