from flask import Flask, render_template, request, redirect, url_for
import datetime
import csv
import os

app = Flask(__name__)


class Pantry():
    def __init__(self):
        self.items = []

    def save_to_file(self, filename="pantry.csv"):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Quantity', 'Expiration Date', 'Unit'])
            for item in self.items:
                writer.writerow([item.name, item.quantity, item.exp_date.strftime("%m/%d/%Y"), item.unit])
        print(f"Pantry saved to {filename}")

    def load_from_file(self, filename="pantry.csv"):
        try:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header
                for row in reader:
                    name, quantity, exp_date, unit = row
                    item = Item(name, float(quantity), exp_date, unit)
                    self.items.append(item)
            print(f"Pantry loaded from {filename}")
        except FileNotFoundError:
            print(f"{filename} not found. Starting with an empty pantry.")


class Item():
    UNIT_MAPPING = {}

    @staticmethod
    def load_units(filename="units.csv"):
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
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for name, unit in Item.UNIT_MAPPING.items():
                writer.writerow([name, unit])

    def __init__(self, name, quantity, exp_date, unit=None):
        self.name = name
        self.quantity = quantity
        self.unit = unit if unit else self.infer_unit(name)
        self.exp_date = datetime.datetime.strptime(exp_date, "%m/%d/%Y").date()

    def infer_unit(self, name):
        cleaned_name = name.lower().strip()
        if cleaned_name in Item.UNIT_MAPPING:
            return Item.UNIT_MAPPING[cleaned_name]
        return None  # Indicate the unit is not known

    def set_unit(self, unit):
        cleaned_name = self.name.lower().strip()
        Item.UNIT_MAPPING[cleaned_name] = unit
        Item.save_units()
        self.unit = unit

    def check_expired(self):
        today_date = datetime.datetime.now().date()
        if today_date > self.exp_date:
            return -1
        else:
            return (self.exp_date - today_date).days


# Initialize the pantry and load data from file
pantry = Pantry()
pantry.load_from_file()


@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['name']
    quantity = float(request.form['quantity'])
    exp_date = request.form['exp_date']

    # Create a temporary item to check the unit
    new_item = Item(name=name, quantity=quantity, exp_date=exp_date)

    # Check if the unit is known
    if new_item.unit is None:  # If the unit is not known
        return redirect(url_for('get_unit', name=name, quantity=quantity, exp_date=exp_date))

    # If the unit is known, add the item directly
    pantry.items.append(new_item)
    pantry.save_to_file()

    return redirect(url_for('view_pantry'))


@app.route('/edit_item', methods=['POST'])
def edit_item():
    name = request.form['name']
    quantity = request.form['quantity'].strip()  # Get the new quantity
    exp_date = request.form['exp_date'].strip()  # Get the new expiration date

    # Find the item in the pantry
    for item in pantry.items:
        if item.name.lower() == name.lower():
            # Update the quantity only if a new one is provided
            if quantity:
                item.quantity = float(quantity)

            # Update the expiration date only if a new one is provided
            if exp_date:
                item.exp_date = datetime.datetime.strptime(exp_date, "%m/%d/%Y").date()

            pantry.save_to_file()
            break  # Exit the loop after updating

    return redirect(url_for('view_pantry'))


@app.route('/remove_item', methods=['POST'])
def remove_item():
    name_remove = request.form['name'].strip()  # Use strip() to handle extra spaces

    # Check if the name_remove key exists to avoid KeyError
    if name_remove:
        # Find the item by name and remove it if found
        pantry.items = [item for item in pantry.items if item.name.lower() != name_remove.lower()]

        # Save the updated pantry to file
        pantry.save_to_file()

    return redirect(url_for('view_pantry'))


@app.route('/search', methods=['GET', 'POST'])
def search_pantry():
    if request.method == 'POST':
        search_term = request.form['search'].strip().lower()
        # If no search term is provided, just return the full pantry
        if not search_term:
            return redirect(url_for('view_pantry'))

        # Filter the pantry items based on the search term
        filtered_items = [item for item in pantry.items if search_term in item.name.lower()]
        return render_template('pantry.html', pantry=filtered_items, search_term=search_term)

    return redirect(url_for('view_pantry'))


@app.route('/')
def view_pantry():
    return render_template('pantry.html', pantry=pantry.items)


@app.route('/unit', methods=['GET', 'POST'])
def get_unit():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        exp_date = request.form['exp_date']
        unit = request.form['unit']

        # Create the item with the provided unit
        new_item = Item(name, float(quantity), exp_date, unit)
        new_item.set_unit(unit)
        pantry.items.append(new_item)
        pantry.save_to_file()
        return redirect(url_for('view_pantry'))

    # Render a form asking for the unit
    name = request.args.get('name')
    quantity = request.args.get('quantity')
    exp_date = request.args.get('exp_date')
    return render_template('get_unit.html', name=name, quantity=quantity, exp_date=exp_date)

if __name__ == '__main__':
    app.run(debug=True)
