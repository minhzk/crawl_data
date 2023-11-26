import pandas as pd
import json

# Đọc dữ liệu từ file JSON
with open("cleanData.json", "r") as json_file:
    data = json.load(json_file)

# Tạo DataFrame từ danh sách JSON
df = pd.DataFrame(data)

# Tạo tên file Excel
excel_file_path = "cleanData.xlsx"

# Ghi DataFrame vào file Excel
df.to_excel(excel_file_path, index=False)

print(f"Chuyển đổi thành công. Dữ liệu đã được lưu vào file Excel: {excel_file_path}")
