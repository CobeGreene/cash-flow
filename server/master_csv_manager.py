import csv
import os
import threading
from typing import Any, Union


FIELDNAMES = [
    'Date', 'Transaction', 'Name',
    'Memo', 'Amount', 'Category', 'Sub Category'
]

TransactionRows = list[dict[Union[str, Any], Union[str, Any]]]


class MasterCSVManager:
    def __init__(self, data_folder: str):
        self.master_file_path = os.path.join(
            data_folder, 'master_transactions.csv')
        self.lock = threading.Lock()

    
    def get_master_file_path(self):
        return self.master_file_path
    
    def read_master_csv_dict(self) -> TransactionRows:
        """Read all rows and columns from the master CSV file."""
        with self.lock:
            if os.path.exists(self.master_file_path):
                with open(self.master_file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    return rows
            return []
        
    def read_master_csv_list(self):
        """Read all rows and columns from the master CSV file."""
        with self.lock:
            if os.path.exists(self.master_file_path):
                with open(self.master_file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    columns = next(reader, [])
                    rows = list(reader)
                    return {'columns': columns, 'rows': rows}
            return {'columns': [], 'rows': []}

    def update_rows_with_categories(self, updated_rows: TransactionRows):
        """Update rows with categories"""
        with self.lock:
            existing_rows = []
            if os.path.exists(self.master_file_path):
                with open(self.master_file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_rows = list(reader)

            for row in updated_rows:
                for existing_row in existing_rows:
                    if (
                        row['Date'] == existing_row['Date'] and
                        row['Transaction'] == existing_row['Transaction'] and
                        row['Name'] == existing_row['Name'] and
                        row['Memo'] == existing_row['Memo'] and
                        row['Amount'] == existing_row['Amount']
                    ):
                        existing_row['Category'] = row['Category']
                        existing_row['Sub Category'] = row['Sub Category']
                        break

            with open(self.master_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(existing_rows)
        return True

    def add_rows_to_master_csv(self, new_rows: TransactionRows):
        """Update master CSV file with new rows, deduplicating based on all columns."""
        with self.lock:
            existing_rows = []
            if os.path.exists(self.master_file_path):
                with open(self.master_file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_rows = list(reader)

            existing_row_tuples = set()
            for row in existing_rows:
                existing_row_copy = row.copy()
                del existing_row_copy["Category"]
                del existing_row_copy["Sub Category"]
                row_tuple = tuple(existing_row_copy.values())
                existing_row_tuples.add(row_tuple)

            added_rows = []
            for row in new_rows:
                row_tuple = tuple(row.values())
                if row_tuple not in existing_row_tuples:
                    row['Category'] = ''
                    row['Sub Category'] = ''
                    existing_rows.append(row)
                    existing_row_tuples.add(row_tuple)
                    added_rows.append(row)

            if existing_rows:
                with open(self.master_file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    writer.writeheader()
                    writer.writerows(existing_rows)

        return {
            'total_rows': len(existing_rows),
            'added_rows': added_rows,
            'duplicate_rows': len(new_rows) - len(added_rows)
        }
