# Work-Queue
Python multi-threaded queue management system which can be used for a variety of purposes including web automation.

User Guide
-----------

First steps to start using:

1. Configure threading parameters in the setting.conf file
   
.. code:: shell
   [THREADING]
   number_of_threads = 50
   thread_time_out = 30

2. Define processing method inside Process.py or use the default processing methods

3. Run main.py