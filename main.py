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
        print("Adding Items\n")
        while done_adding == "n":
            name = input("Enter item name: ")

            is_new_item = 1
            for item in self.items:
                if item.name.lower() == name.lower():
                    is_new_item = 0
                    print(f"Already have {item.quantity} of {item.name}")
                    new_amount = float(input("Enter new additional amount of item: "))
                    item.quantity += new_amount
                    print(f"Updated quantity: {item.quantity} {item.unit} of {item.name}")

            if is_new_item:
                # Infer the unit from the item name, if it's not in the mapping prompt the user
                temp_item = Item(name, 0, "01/01/2100")  # Temporarily create item to get the unit
                unit = temp_item.unit

                # Prompt for the quantity, showing the inferred unit
                try:
                    quantity = float(input(f"Enter item quantity (in {unit}): "))
                except ValueError:
                    print("\nERROR: Quantity must be a number!")
                    quantity = float(input(f"Enter item quantity (in {unit}): "))
                expiration_date = input("Enter expiration date (MM/DD/YYYY): ")

                # Create a new item with the entered quantity and expiration date
                item = Item(name, quantity, expiration_date)
                self.items.append(item)
                print(f"Added {item.quantity} {item.unit} of {item.name} to the pantry.\n")

            done_adding = input("Finished adding items? (y/n): ").lower()

    def view_items(self):
        if not self.items:
            print("The pantry is empty.")
        else:
            print("Pantry Contents: \n")
            for item in self.items:
                item.print_info()

    def remove_items(self):
        done_removing = 0
        print("Removing Items\n")
        while done_removing == 0:
            name = input("Enter item to remove: ")
            found_item = 0
            for item in self.items:
                if item.name.lower() == name.lower():
                    found_item = 1
                    self.items.remove(item)
                    print(f"Removed {item.name} from the pantry.")
                    break
            if not found_item:
                print(f"Item '{name}' not found in the pantry.")
            done_removing = input("Finished removing items? (y/n): ").lower()

    def used_items(self):
        done_using = 0
        print("Entering partially used items\n")
        while done_using == 0:
            name = input("Enter item you used: ")
            found_item = 0
            for item in self.items:
                if item.name.lower() == name.lower():
                    found_item = 1
                    print(f"Remaining amount of {item.name}: {item.quantity} {item.unit}\n")
                    used_amount = float(input(f"Enter the amount of the item used (in {item.unit}: "))
                    item.used_item(used_amount)
                    print(f"{item.quantity} {item.unit} of {item.name} remaining")
                    break
            done_using = input("Finished using items? (y/n): ").lower()
            if not found_item:
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

        #Create spaces based on text length so it prints aligned
        space1 = ""
        space2 = ""
        space3 = "     "
        for i in range(16 - len(self.name)):
            space1 += " "
        for j in range(16 - len(self.unit)):
            space2 += " "
        if self.quantity % 10 > 0:
            space2 += " "
        if self.check_expired() > 9:
            space3 = space3[:-1]
        if self.check_expired() > 99:
            space3 = space3[:-1]

        if self.check_expired() == -1:
            print(
                f"{self.name}{space1}  {round(self.quantity, 1)} {self.unit} {space2}ITEM HAS EXPIRED {space3} EXPIRED")
        elif (self.check_expired() <= 5):
            print(
                f"{self.name}{space1}  {round(self.quantity, 1)} {self.unit} {space2}expires in {self.check_expired()} days {space3}EXPIRES SOON")
        else:
            print(
                f"{self.name}{space1}  {round(self.quantity, 1)} {self.unit} {space2}expires in {self.check_expired()} days")

    def used_item(self, usage):
        self.quantity -= usage


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


def main():
    Item.load_units()
    pantry = Pantry()

    # Load pantry from file
    pantry.load_from_file()
    print("=========================================\n")
    pantry.view_items()
    running = 1
    while running:
        print("\n=========================================\n\nWhat would you like to do?\n")
        print("1 - View Pantry")
        print("2 - Add Items to Pantry")
        print("3 - Remove Items From Pantry")
        print("4 - Enter Amount of Item Used")
        print("0 - Exit\n")

        user_choice = int(input("Enter option: "))
        print("\n=========================================\n")
        if user_choice == 1:
            # View items in the pantry
            pantry.view_items()
        if user_choice == 2:
            # Add items through input
            pantry.add_items()
            pantry.save_to_file()
        if user_choice == 3:
            pantry.remove_items()
            pantry.save_to_file()
        if user_choice == 4:
            pantry.used_items()
            pantry.save_to_file()
        if user_choice == 0:
            running = 0


if __name__ == "__main__":
    main()
