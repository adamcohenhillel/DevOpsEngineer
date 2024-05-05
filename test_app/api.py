import csv
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)
csv_file_path = 'items.csv'


def init_csv():
    if not Path(csv_file_path).exists():
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'name', 'description'])


@app.route('/')
def index():
    return "Welcome to the Flask API using CSV!"


@app.route('/items', methods=['POST'])
def create_item():
    new_item = request.json
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([new_item.get('id'), new_item.get(
            'name'), new_item.get('description')])
    return jsonify({'message': 'Item added successfully!'}), 201


@app.route('/items', methods=['GET'])
def read_items():
    items = []
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            items.append(row)
    return jsonify(items)


@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    updated = False
    temp_items = []
    new_data = request.json
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['id']) == item_id:
                row['name'], row['description'] = new_data.get(
                    'name'), new_data.get('description')
                updated = True
            temp_items.append(row)

    if updated:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(
                file, fieldnames=['id', 'name', 'description'])
            writer.writeheader()
            writer.writerows(temp_items)
        return jsonify({'message': 'Item updated successfully!'})
    else:
        return jsonify({'message': 'Item not found'}), 404


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    items_exist = False
    temp_items = []
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['id']) != item_id:
                temp_items.append(row)
            else:
                items_exist = True

    if items_exist:
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(
                file, fieldnames=['id', 'name', 'description'])
            writer.writeheader()
            writer.writerows(temp_items)
        return jsonify({'message': 'Item deleted successfully!'})
    else:
        return jsonify({'message': 'Item not found'}), 404


if __name__ == '__main__':
    init_csv()
    app.run(debug=True)
