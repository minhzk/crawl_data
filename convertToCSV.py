import csv
import json
import os
from datetime import datetime

def generate_unique_csv_filename(base_filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{base_filename}_{timestamp}.csv"
    counter = 1
    while os.path.exists(unique_filename):
        unique_filename = f"{base_filename}_{timestamp}_{counter}.csv"
        counter += 1
    return unique_filename

# Đọc dữ liệu từ file JSON
json_file = open("data.json", "r")
data = json.load(json_file)

# Tạo tên file CSV dựa trên thời gian hiện tại hoặc số thứ tự
csv_file_path = generate_unique_csv_filename("cleanData")

with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
    # Tạo đối tượng DictWriter để ghi dữ liệu vào file CSV
    csv_writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())

    # Viết header (tên cột) vào file CSV
    csv_writer.writeheader()

    # Viết dữ liệu từ danh sách JSON vào file CSV
    csv_writer.writerows(data)

print(f"Chuyển đổi thành công. Dữ liệu đã được lưu vào file: {csv_file_path}")
