from itertools import chain
import queue
from typing import Union, cast
import threading
from categorizer_constants import default_categories, CategoriesDict
from master_csv_manager import MasterCSVManager, TransactionRows
from datasets import load_dataset
import os
import json
import evaluate
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer, DataCollatorWithPadding
from datasets import load_dataset
from transformers import pipeline, Pipeline


class CategorizedTask:
    def __init__(self, rows: TransactionRows, categorizer_manager: 'CategorizerManager', master_csv_manager: MasterCSVManager):
        self.rows = rows
        self.categorizer_manager = categorizer_manager
        self.master_csv_manager = master_csv_manager

    def doWork(self):
        print("Start work on categorizing")
        for row in self.rows:
            type_result = self.categorizer_manager.get_classifier()(
                row['Name'])
            type_label = None
            if type_result and isinstance(type_result, list):
                first_result = type_result[0]
                if isinstance(first_result, dict) and 'label' in first_result:
                    type_label = first_result['label']
            category = "unknown"
            if (type_label):
                category = self.categorizer_manager.get_category_from_subcategory(
                    type_label)
            row['Category'] = category
            row['Sub Category'] = type_label if type_label else "Unknown"
        self.master_csv_manager.update_rows_with_categories(
            updated_rows=self.rows)
        print("Finish work on categorizing")


class UpdateCategoriesTask:
    def __init__(self, new_categories_updates: list[dict], category_file_path: str, lock: threading.Lock, master_csv_manager: MasterCSVManager, categorizer_manager: 'CategorizerManager'):
        self.new_categories_updates = new_categories_updates
        self.category_file_path = category_file_path
        self.master_csv_manager = master_csv_manager
        self.lock = lock
        self.categorizer_manager = categorizer_manager

    def doWork(self):
        print("Start updating categories", self.new_categories_updates)
        transactions = self.master_csv_manager.read_master_csv_dict()
        updated_rows: TransactionRows = []
        for edit in self.new_categories_updates:
            for row in transactions:
                if (edit["type"] == 'update' and
                        edit["change"]["subCategory"] == row["Sub Category"]):
                    row['Sub Category'] = edit["change"]["newName"]
                    updated_rows.append(row)
                elif (edit["type"] == 'delete' and
                      edit["change"]["subCategory"] == row["Sub Category"]):
                    row['Category'] = ""
                    row['Sub Category'] = ""
                    updated_rows.append(row)

        self.master_csv_manager.update_rows_with_categories(
            updated_rows=updated_rows)

        with self.lock:
            # Read existing categories from file
            categories = default_categories.copy()
            if os.path.exists(self.category_file_path):
                with open(self.category_file_path, 'r', encoding='utf-8') as f:
                    categories = json.load(f)

            # Apply edits to categories
            for edit in self.new_categories_updates:
                if (edit["type"] == 'update'):
                    sub_cat = edit["change"]["subCategory"]
                    new_name = edit["change"]["newName"]
                    # Update subcategory name
                    for _cat, sub_categories in categories.items():
                        if sub_cat in sub_categories:
                            sub_categories[sub_categories.index(
                                sub_cat)] = new_name
                elif (edit["type"] == 'delete'):
                    sub_cat = edit["change"]["subCategory"]
                    # Remove subcategory
                    for _cat, sub_categories in categories.items():
                        if sub_cat in sub_categories:
                            sub_categories.remove(sub_cat)
                elif edit["type"] == 'add':
                    # Add new subcategory under main category
                    sub_cat = edit["change"]["subCategory"]
                    main_cat = edit["change"]["category"]
                    categories.setdefault(main_cat, [])
                    if sub_cat not in categories[main_cat]:
                        categories[main_cat].append(sub_cat)

            # Write updated categories back to file
            with open(self.category_file_path, 'w', encoding='utf-8') as f:
                json.dump(categories, f, indent=4)
                self.categorizer_manager.set_categories(categories)
        print("Finish updating categories")


class TrainTask:
    def __init__(self, categorizer_manager: 'CategorizerManager', master_csv_manager: MasterCSVManager, lock: threading.Lock):
        self.categorizer_manager = categorizer_manager
        self.master_csv_manager = master_csv_manager
        self.lock = lock

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

        tokenizer = AutoTokenizer.from_pretrained(
            "distilbert/distilbert-base-uncased")

        def preprocess_function(examples):
            return tokenizer(examples["text"], truncation=True)

        tokenized_imdb = dataset.map(preprocess_function, batched=True)

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        accuracy = evaluate.load("accuracy")

        label_to_id = self.categorizer_manager.get_label_to_id()
        id_to_label = self.categorizer_manager.get_id_to_label()
        all_sub_categories = self.categorizer_manager.get_all_sub_categories()

        def encode_labels(example):
            example['label'] = label_to_id[example['label']]
            return example

        tokenized_imdb = tokenized_imdb.map(encode_labels)

        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            return accuracy.compute(predictions=predictions, references=labels)

        small_train_dataset = tokenized_imdb["train"].shuffle(seed=42)
        small_eval_dataset = tokenized_imdb["train"].shuffle(
            seed=42).select(range(min(100, len(tokenized_imdb["train"]))))

        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert/distilbert-base-uncased", num_labels=len(all_sub_categories), id2label=id_to_label, label2id=label_to_id
        )

        with self.lock:
            training_args = TrainingArguments(
                output_dir=self.categorizer_manager.get_training_file_path(),
                learning_rate=2e-5,
                per_device_train_batch_size=16,
                per_device_eval_batch_size=16,
                num_train_epochs=15,
                weight_decay=0.01,
                eval_strategy="epoch",
                save_strategy="epoch",
            )

            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=small_train_dataset,
                eval_dataset=small_eval_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                compute_metrics=compute_metrics,
            )

            trainer.train()
            trainer.save_model(self.categorizer_manager.get_model_file_path())

            classifier = pipeline("text-classification",
                                      model=self.categorizer_manager.get_model_file_path())
            self.categorizer_manager.set_classifier(classifier)            

        print("Finish work on training")


class InitializedCategorizerManager:
    def __init__(self, categorizer_manager: 'CategorizerManager', data_folder: str, lock: threading.Lock):
        self.categorizer_manager = categorizer_manager
        self.data_folder = data_folder
        self.lock = lock

    def doWork(self):
        print("Initializing categorizer manager...")
        model_folder = self.categorizer_manager.get_model_file_path()
        categories: CategoriesDict = {}
        with self.lock:
            if os.path.exists(self.categorizer_manager.get_category_file_path()):
                with open(self.categorizer_manager.get_category_file_path(), 'r', encoding='utf-8') as f:
                    categories = json.load(f)
            else:
                categories = default_categories

            self.categorizer_manager.set_categories(categories)
            if not os.path.exists(self.categorizer_manager.get_model_file_path()):
                all_categories = list(chain.from_iterable(
                    [category_types for _category, category_types in categories.items()]))
                label_to_id = {label: i for i,
                               label in enumerate(all_categories)}
                id_to_label = {i: label for i,
                               label in enumerate(all_categories)}
                model = AutoModelForSequenceClassification.from_pretrained(
                    "distilbert/distilbert-base-uncased", num_labels=len(all_categories), id2label=id_to_label, label2id=label_to_id
                )
                classifier = pipeline("text-classification",
                                      model=model, tokenizer="distilbert/distilbert-base-uncased")
                self.categorizer_manager.set_classifier(classifier)
            else:
                classifier = pipeline("text-classification",
                                      model=model_folder)
                self.categorizer_manager.set_classifier(classifier)
        print("Categorizer Manager is initialized and ready to use.")


class CategorizerManager:
    def __init__(self, master_csv_manager: MasterCSVManager, data_folder: str):
        self.queue = queue.Queue()

        self.master_csv_manager = master_csv_manager
        self.consumer_thread = threading.Thread(
            target=self.categorized_consumer, args=(self.queue,))
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        self.data_folder = data_folder
        self.category_file_path = os.path.join(
            data_folder, 'category_data.json')
        self.model_file_path = os.path.join(
            data_folder, 'classifier_model')
        self.training_file_path = os.path.join(
            data_folder, 'training_file_path')
        self.categories: Union[CategoriesDict, None] = None
        self.classifier: Union[Pipeline, None] = None
        self.lock = threading.Lock()
        self.has_queue_initialized_task = False

    def add_categorized_task(self, rows: TransactionRows):
        task = CategorizedTask(rows, self, self.master_csv_manager)
        self.queue.put(task, block=False)

    def add_train_task(self):
        task = TrainTask(self,
                         self.master_csv_manager, self.lock)
        self.queue.put(task, block=False)

    def add_initialized_task(self):
        if (self.has_queue_initialized_task):
            return
        task = InitializedCategorizerManager(
            self, self.data_folder, self.lock)
        self.queue.put(task, block=False)
        self.has_queue_initialized_task = True

    def get_category_file_path(self) -> str:
        return self.category_file_path

    def get_model_file_path(self) -> str:
        return self.model_file_path

    def get_training_file_path(self) -> str:
        return self.training_file_path

    def get_categories(self):
        return self.categories

    def set_categories(self, categories: CategoriesDict):
        self.categories = categories

    def get_classifier(self) -> Pipeline:
        if self.classifier is None:
            raise ValueError("Classifier not set")
        return self.classifier

    def get_category_from_subcategory(self, sub_category: str) -> str:
        if self.categories is None:
            raise ValueError("Categories not set")
        type_to_category = {
            value: key for key, values in self.categories.items() for value in values
        }
        return type_to_category.get(sub_category, "Unknown")

    def get_label_to_id(self) -> dict[str, int]:
        if self.categories is None:
            raise ValueError("Categories not set")
        all_categories = list(chain.from_iterable(
            [category_types for _category, category_types in self.categories.items()]))
        return {label: i for i, label in enumerate(all_categories)}

    def get_id_to_label(self) -> dict[int, str]:
        if self.categories is None:
            raise ValueError("Categories not set")
        all_categories = list(chain.from_iterable(
            [category_types for _category, category_types in self.categories.items()]))
        return {i: label for i, label in enumerate(all_categories)}

    def get_all_sub_categories(self) -> list[str]:
        if self.categories is None:
            raise ValueError("Categories not set")
        all_sub_categories = list(chain.from_iterable(
            [category_types for _category, category_types in self.categories.items()]))
        return all_sub_categories

    def set_classifier(self, classifier: Pipeline):
        self.classifier = classifier

    def update_categories(self, new_categories):
        self.queue.put(UpdateCategoriesTask(
            new_categories, self.category_file_path, self.lock, self.master_csv_manager, self), block=False)
        return True

    def categorized_consumer(self, queue):
        print('Consumer: Running')
        while True:
            item = queue.get()
            if item is None:
                queue.task_done()
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
