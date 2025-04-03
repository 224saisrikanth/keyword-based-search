import os
import json
import pandas as pd

class DataStorage:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        
    def save_to_json(self, data, filename="extracted_text.json"):
        """Save extracted data to a JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return file_path
    
    def save_to_parquet(self, data, filename="extracted_text.parquet"):
        """Convert data to a DataFrame and save as Parquet."""
        # Flatten the data for DataFrame storage
        flattened_data = []
        for doc in data:
            for page_num, page_text in doc["pages"].items():
                flattened_data.append({
                    "filename": doc["filename"],
                    "page_num": int(page_num),
                    "text": page_text
                })
        
        df = pd.DataFrame(flattened_data)
        file_path = os.path.join(self.data_dir, filename)
        df.to_parquet(file_path, compression='zstd')
        return file_path
    
    def load_from_json(self, filename="extracted_text.json"):
        """Load data from a JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def load_from_parquet(self, filename="extracted_text.parquet"):
        """Load data from a Parquet file."""
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            return pd.read_parquet(file_path)
        return None 