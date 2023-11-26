import json

file = open("data.json", "r")
arr = json.load(file)
file.close()

new_data = []

for item in arr:
    for size in item['sizes']:
        new_entry = {
            "brand": item["brand"],
            "category": item["category"],
            "style": item["style"],
            "release_date": item["release_date"],
            "colorway": item["colorway"],
            "retail_price": item["retail_price"],
            "size": size["size"],
            "price": size["price"]
        }
        new_data.append(new_entry)

# Ghi dữ liệu mới vào cleanData.json
with open("cleanData.json", "w+") as file:
    json.dump(new_data, file)

