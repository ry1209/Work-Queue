# Work-Queue
Python multi-threaded queue management system that contains custom work items which are passed out to consuming processes in order of priority. This can be used for any automation purposes including web automation.
It leverages the Python queue module, which implements three types of queues: 
1. FIFO (First In, First Out)
2. LIFO (Last In, First Out)
3. Priority Queue

User Guide
-----------

First steps to start using:

1. Configure threading parameters and add custom parameters to the setting.conf file

2. Define a processing method inside Process.py or use the default processing methods

3. Executing the main.py script will process the input data and generate output data in the "data" folder
