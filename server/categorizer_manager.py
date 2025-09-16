import queue
from typing import Any, Union, cast
import threading
from categorizer_constants import type_to_category, default_categories
from master_csv_manager import MasterCSVManager
from datasets import load_dataset
import os
import json

class CategorizedTask:
    def __init__(self, rows: list[dict[Union[str, Any], Union[str, Any]]], classifier, master_csv_manager: MasterCSVManager):
        self.rows = rows
        self.classifier = classifier
        self.master_csv_manager = master_csv_manager

    def doWork(self):
        print("Start work on categorizing")
        for row in self.rows:
            type_result = self.classifier(row['Name'])
            type_label = None
            if type_result and isinstance(type_result, list):
                first_result = type_result[0]
                if isinstance(first_result, dict) and 'label' in first_result:
                    type_label = first_result['label']
            category = type_to_category.get(type_label or "Unknown")
            row['Category'] = category
            row['Sub Category'] = type_label if type_label else "Unknown"
        self.master_csv_manager.update_rows_with_categories(
            updated_rows=self.rows)
        print("Finish work on categorizing")


class TrainTask:
    def __init__(self, classifier, data_folder: str, master_csv_manager: MasterCSVManager):
        self.classifier = classifier
        self.data_folder = data_folder
        self.master_csv_manager = master_csv_manager

    def doWork(self):
        print("Start work on training")
        dataset = load_dataset("csv", data_files={
                               "train": self.master_csv_manager.get_master_file_path()}, keep_in_memory=True)
        dataset = dataset.rename_column("Name", "text")
        dataset = dataset.rename_column("Sub Category", "label")
        dataset = dataset.map(remove_columns=[
            'Date', 'Transaction',
            'Memo', 'Amount', 'Category',
        ])

        print("Finish work on training")


class CategorizerManager:
    def __init__(self, classifier, master_csv_manager: MasterCSVManager, data_folder: str):
        self.queue = queue.Queue()
        self.classifier = classifier
        self.master_csv_manager = master_csv_manager
        self.consumer_thread = threading.Thread(
            target=self.categorized_consumer, args=(self.queue,))
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        self.data_folder = data_folder
        self.category_file_path = os.path.join(
            data_folder, 'category_data.json')
        self.lock = threading.Lock()
        self.categories = self._get_category_from_file()

    def add_categorized_task(self, rows):
        task = CategorizedTask(rows, self.classifier, self.master_csv_manager)
        self.queue.put(task, block=False)

    def add_train_task(self):
        task = TrainTask(self.classifier, self.data_folder,
                         self.master_csv_manager)
        self.queue.put(task, block=False)

    def get_categories(self):
        return self.categories

    def categorized_consumer(self, queue):
        print('Consumer: Running')
        while True:
            item = queue.get()
            if item is None:
                break
            categorized_task = cast(CategorizedTask, item)
            categorized_task.doWork()
            queue.task_done()
        print('Consumer: Done')

    def stop(self):
        self.queue.join()
        self.queue.put(None)
        self.consumer_thread.join()
        self.queue.join()

    def _get_category_from_file(self):
        with self.lock:
            if os.path.exists(self.category_file_path):
                with open(self.category_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_categories