import queue
from typing import Any, Union, cast
import threading

class CategorizedTask:
    def __init__(self, rows: list[dict[Union[str, Any], Union[str, Any]]], classifer, constants, master_csv_manager):
        self.rows = rows
        self.classifer = classifer
        self.constants = constants
        self.master_csv_manager = master_csv_manager

    def doWork(self):
        print("Start work on categorizing")
        for row in self.rows:
            type_result = self.classifer(row['Name'])
            type_label = None
            if type_result and isinstance(type_result, list):
                first_result = type_result[0]
                if isinstance(first_result, dict) and 'label' in first_result:
                    type_label = first_result['label']
            category = self.constants.type_to_category.get(type_label, "Unknown")
            row['Category'] = category
            row['Sub Category'] = type_label if type_label else "Unknown"
        self.master_csv_manager.update_rows_with_categories(updated_rows=self.rows)
        print("Finish work on categorizing")

class CategorizerManager:
    def __init__(self, classifer, constants, master_csv_manager):
        self.queue = queue.Queue()
        self.classifer = classifer
        self.constants = constants
        self.master_csv_manager = master_csv_manager
        self.consumer_thread = threading.Thread(target=self.categorized_consumer, args=(self.queue,))
        self.consumer_thread.daemon = True
        self.consumer_thread.start()

    def add_task(self, rows):
        task = CategorizedTask(rows, self.classifer, self.constants, self.master_csv_manager)
        self.queue.put(task)

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
        self.queue.put(None)
        self.consumer_thread.join()
