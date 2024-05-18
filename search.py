from rich.console import Console
from grocery import load_grocery_items

console = Console()
grocery_items = load_grocery_items()

def search_product(product_name):
    found = False
    for item in grocery_items:
        if item['Name'].lower() == product_name.lower():
            console.print("\n[bold]Product Found:[/bold]")
            console.print(f"[bold]Name:[/bold] {item['Name']}")
            console.print(f"[bold]Category:[/bold] {item['Category']}")
            console.print(f"[bold]Quantity:[/bold] {item['Quantity']}")
            console.print(f"[bold]Price:[/bold] ${item['Price']}")
            found = True
            break
    if not found:
        console.print("\nProduct not found.")
