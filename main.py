from WorkQueue import WorkQueue, FIFOItemManager, FILOItemManager, ConcurrentItemManager
from Process import DefaultProcessingMethod, GoScraperBackendProcessingMethod, GoScraperFrontendProcessingMethod

def main():
    work_queue = WorkQueue(
        item_manager=ConcurrentItemManager(processing_method=GoScraperBackendProcessingMethod())
    )
    work_queue.create_work_queue()
    work_queue.process()
    work_queue.output_processed_items()
    
if __name__ == "__main__":
    main()