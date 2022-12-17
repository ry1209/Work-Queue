from enum import Enum
from abc import ABC, abstractmethod
from better_abc import abstract_attribute
import threading
from func_timeout import func_timeout, FunctionTimedOut
from queue import PriorityQueue, Queue, LifoQueue
from typing import List, Union, Tuple
from datetime import datetime
import os
import json
from Config import config
from Process import ProcessingMethod, WorkItem

class State(Enum):
    """Work item state."""

    DONE = "COMPLETED"
    FAILED = "FAILED"

class Error(Enum):
    """Failed work item error type."""

    BUSINESS = "BUSINESS"  
    APPLICATION = "APPLICATION" 

class ItemManager(ABC):
    
    def __init__(self, processing_method : ProcessingMethod):
        self.processing_method = processing_method
        self.processed_items = dict()
        self.configs = config

    def update_work_item(self, id : int, state : State, exception_type : Error = None, exception_message : str = None):
        new_status = {
            'state' : state.value,
            'exception_type' : exception_type.value if exception_type else None,
            'exception_message' : exception_message
        }
        self.processed_items[id].item_status.update(new_status)

    def add_items_to_queue(self, items : List[WorkItem]) -> None:
        for item in items:
            self.queue.put(item)

    def mark_item_as_complete(self, id:int, output:dict):
        self.processed_items[id].payload.update(output)
        self.update_work_item(id=id,state = State.DONE)
    
    def mark_item_as_exception(self, id : int, exception_type : Error, exception_reason : str):
        self.update_work_item(id=id,state=State.FAILED,exception_type=exception_type,exception_message=str(exception_reason))
    
    def get_next_pending_item(self):
        id,item = self.queue.get()
        self.processed_items[id] = item
        return item

    @abstract_attribute
    def queue(self):
        raise NotImplementedError

    @abstractmethod
    def process(self):
        raise NotImplementedError

class ConcurrentItemManager(ItemManager):

    def __init__(self, processing_method : ProcessingMethod):
        super().__init__(processing_method)
        self.threading_config = self.configs['THREADING']
        self.queue = PriorityQueue()
        self.lock = threading.Lock()

    def work(self):
        while True:
            if self.queue.empty():
                break
            item = self.get_next_pending_item()
            try:
                id,output = func_timeout(self.threading_config['thread_time_out'], self.processing_method.process_work_item, args=[item])
                self.lock.acquire()
                self.mark_item_as_complete(id,output)
                self.lock.release()
            except FunctionTimedOut:
                self.mark_item_as_exception(item.id,Error.APPLICATION,'Timeout Error!')
            except Exception as e:
                self.lock.acquire()
                self.mark_item_as_exception(item.id,Error.APPLICATION,str(e))
                self.lock.release()

    def process(self):
        threads=[]
        for _ in range(self.threading_config['number_of_threads']):
            worker = threading.Thread(target=self.work, daemon=True)
            worker.start()
            threads.append(worker)
        for thread in threads:
            thread.join()

class FIFOItemManager(ItemManager):
    def __init__(self, processing_method : ProcessingMethod):
        super().__init__(processing_method)
        self.queue = Queue()
    
    def process(self):
        while not self.queue.empty():
            try:
                item = self.get_next_pending_item()
                id,output = self.processing_method.process_work_item(item)
                self.mark_item_as_complete(id,output)
            except Exception as e:
                self.mark_item_as_exception(item.id, Error.APPLICATION, str(e))

class FILOItemManager(ItemManager):
    def __init__(self, processing_method : ProcessingMethod):
        super().__init__(processing_method)
        self.queue = LifoQueue()
    
    def process(self):
        while not self.queue.empty():
            try:
                item = self.get_next_pending_item()
                id,output = self.processing_method.process_work_item(item)
                self.mark_item_as_complete(id,output)
            except Exception as e:
                self.mark_item_as_exception(item.id, Error.APPLICATION, str(e))


class WorkQueue:
    def __init__(self, item_manager : ItemManager, work_item_folder: str = f"data/{str(datetime.now()).replace(' ','_').replace('.','_').replace(':','-')}"):
        self.index = 0
        self.item_manager = item_manager
        self.input_path = f'./{work_item_folder}/input.json'
        self.output_path = f'./{work_item_folder}/output.json'
        if not os.path.exists(work_item_folder):
            os.mkdir(work_item_folder)
            
    def create_work_item(self, data:dict) -> WorkItem:
        work_item = WorkItem(id=self.index,payload=data)
        self.index+=1
        return work_item

    def create_work_items(self) -> List[WorkItem]:
        work_items = []
        for data in self.item_manager.processing_method.create_payload():
            work_item = WorkItem(id=self.index,payload=data)
            work_items.append((self.index, work_item))
            self.index+=1
        return work_items

    def export_items(self, items : List[WorkItem], path : str) -> None:
        json_file = []
        for item in items:
            if type(item) == tuple:
                item = item[-1]
            json_file.append(
                {
                    'id':item.id,
                    'payload':item.payload,
                    'item_status':item.item_status
                }
            )
        with open(path, 'w') as f:
            json.dump(json_file,f,indent=4)

    def add_items_to_queue(self, items : List[Union[WorkItem, Tuple[int,WorkItem]]], save : bool = True):
        if save:
            self.export_items(items, self.input_path)
        self.item_manager.add_items_to_queue(items)

    def create_work_queue(self):
        self.add_items_to_queue(self.create_work_items())

    def output_processed_items(self):
        self.export_items(self.item_manager.processed_items.values(), self.output_path)

    def process(self):
        self.item_manager.process()
    

