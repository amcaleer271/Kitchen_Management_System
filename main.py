#Purpose of this project is to create a system to easily manage a kitchen
#Features included should be tracking of expiration dates, recipie suggestions,
#  and shopping list generation.
#Ideally has a gui to interface with and is able to be saved between sessions

import datetime
import csv
import os
class Pantry():
    def __init__(self):
        self.items = []

    def add_items(self):
        done_adding = "n"
        while done_adding == "n":
            name = input("Enter item name: ")

            # Infer the unit from the item name, if it's not in the mapping prompt the user
            temp_item = Item(name, 0, "01/01/2100")  # Temporarily create item to get the unit
            unit = temp_item.unit

            # Prompt for the quantity, showing the inferred unit
            quantity = float(input(f"Enter item quantity (in {unit}): "))
            expiration_date = input("Enter expiration date (MM/DD/YYYY): ")

            # Create a new item with the entered quantity and expiration date
            item = Item(name, quantity, expiration_date)
            self.items.append(item)
            print(f"Added {item.quantity} {item.unit} of {item.name} to the pantry.")

            done_adding = input("Finished adding items (y/n)").lower()

    def view_items(self):
        if not self.items:
            print("The pantry is empty.")
        else:
            print("Pantry Contents: \n")
            for item in self.items:
                item.print_info()

    def remove_items(self):
        done_removing = 0
        while done_removing == 0:
            name = input("Enter item to remove")
            for item in self.items:
                if item.name == name:
                    self.items.remove(item)
                    print(f"Removed {item.name} from the pantry.")
                    return
            print(f"Item '{name}' not found in the pantry.")

    def save_to_file(self, filename="pantry.csv"):
        # Save pantry items to a CSV file
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Quantity', 'Expiration Date'])
            for item in self.items:
                writer.writerow([item.name, item.quantity, item.exp_date.strftime("%m/%d/%Y")])
        print(f"Pantry saved to {filename}")

    def load_from_file(self, filename="pantry.csv"):
        # Load pantry items from a CSV file
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header
                for row in reader:
                    name, quantity, exp_date = row
                    item = Item(name, float(quantity), exp_date)
                    self.items.append(item)
            print(f"Pantry loaded from {filename}")
        except FileNotFoundError:
            print(f"{filename} not found. Starting with an empty pantry.")

class Shopping_List():
    def __init__(self):
        self.list = []

    def add_item(self, item):
        added_to_list = 0
        for entry in list:
            if entry.name == item.name:

                #Check if the item trying to be added already exists in the list
                print(f"An entry with this name already exists, here is it's info:")
                print(f"{entry.print_info()}")

                #if duplicate is found, ask user if they want to re-add the item
                reentry_choice = input("Add this item again (y/n")
                if reentry_choice.lower() == "y":
                    self.list += item
                    added_to_list = 1

        #if item was found to not be a duplicate, add to the list
        if added_to_list == 0:
            self.list += item

    def save_to_file(self, filename="shopping_list.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Quantity'])
            for item in self.list:
                writer.writerow([item.name, item.quantity])
        print(f"Shopping list saved to {filename}")

    def load_from_file(self, filename="shopping_list.csv"):
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header
                for row in reader:
                    name, quantity = row
                    item = Item(name, float(quantity), "01/01/2100")  # Expiration date not needed here
                    self.list.append(item)
            print(f"Shopping list loaded from {filename}")
        except FileNotFoundError:
            print(f"{filename} not found. Starting with an empty shopping list.")


class Item():
    UNIT_MAPPING = {}

    @staticmethod
    def load_units(filename="units.csv"):
        """Load units from a file into UNIT_MAPPING."""
        if os.path.exists(filename):
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    name, unit = row
                    Item.UNIT_MAPPING[name] = unit
        else:
            print(f"{filename} not found, starting with an empty unit mapping.")

    @staticmethod
    def save_units(filename="units.csv"):
        """Save the UNIT_MAPPING to a file."""
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for name, unit in Item.UNIT_MAPPING.items():
                writer.writerow([name, unit])

    def __init__(self, name, quantity, exp_date):
        self.name = name
        self.quantity = quantity
        self.unit = self.infer_unit(name)
        self.exp_date = datetime.datetime.strptime(exp_date, "%m/%d/%Y").date()

    def infer_unit(self, name):
        cleaned_name = name.lower().strip()

        # If the unit is already known, return it
        if cleaned_name in Item.UNIT_MAPPING:
            return Item.UNIT_MAPPING[cleaned_name]

        # If not, ask the user to provide the unit and save it to the mapping
        unit = input(f"Enter the unit for {name}: ")
        Item.UNIT_MAPPING[cleaned_name] = unit

        # Save the updated UNIT_MAPPING to file
        Item.save_units()

        return unit

    def check_expired(self):
        today_date = datetime.datetime.now().date()
        if today_date > self.exp_date:
            return -1
        else:
            return (self.exp_date - today_date).days

    def print_info(self):
        if self.check_expired() == -1:
            print(f"{self.name}, Quantity: {self.quantity} {self.unit}, Item has expired")
        else:
            print(f"{self.name}, Quantity: {self.quantity} {self.unit}, expires in {self.check_expired()} days")

    def used_item(self, usage):
        self.quantity -= usage

def main():
    Item.load_units()
    pantry = Pantry()

    # Load pantry from file
    pantry.load_from_file()

    running = 1
    while running:
        print("\n=========================================\nWhat would you like to do?\n")
        print("1 - Add Items to Pantry")
        print("2 - Remove Items from Pantry")
        print("3 - View Pantry\n")

        user_choice = int(input("Enter option: "))
        print("\n=========================================\n")
        if user_choice == 1:
            # Add items through input
            pantry.add_items()

            # Save pantry to file
            pantry.save_to_file()
        if user_choice == 2:
            pantry.remove_items()
        if user_choice == 3:
            # View items in the pantry
            pantry.view_items()

if __name__ == "__main__":
    main()

