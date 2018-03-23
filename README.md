# Eventually Consistent Blackboard

## Task 1: Implement Eventual Consistency https://youtu.be/SRK7eEmT8iI

* Demonstrate that the Blackboard is eventually consistent

  * Inconsistent for a while
  
  * Then becomes consistent
  
  * Delete and Modify still work
  
* Briefly discuss pros and cons of this design

* Discuss the cost of your solution

## Measurements

The following graph represents the time taken for all the blackboard to reach consistency state, i.e. the longest time among all nodes. The final time is calculated measuring the time the first message has been received by one of the nodes of the system and the time the last message has been received by one of the other nodes using the time.time() function. The graph compares two different models: centralized ([Lab2](https://github.com/ddellagiacoma/distributedsystems-2017-assignment-2)) and eventually consistent (Lab3).



As we can see, the time taken to reach consistency is always longer in the centralized system. This is because every POST requests received by non-leader nodes has to be retransmitted to the leader which will propagate the message to all the other nodes. For this reason, the number of messages in the centralized system is higher than eventually consistent system. Moreover, incrementing the number of nodes in the system, the leader will have to handle a greater amount of data that could slow down the system.

On the other hand, every node of the eventually consistent system needs to maintain a logical clock and keeps it updated every time the node executes an event in order to determine which event happened first.

Both systems have been tested with 8, 16 and 32 nodes sending 40 POST messages to every blackboard at the same time. To send 40 POST messages on every node at (almost) the same time, the following bash script has been used:

```bash
for i in {1..40};
do
  curl -d 'entry=t1.' ${i} -X 'POST' 'http://10.1.0.1:80/board' &
  curl -d 'entry=t2.' ${i} -X 'POST' 'http://10.1.0.2:80/board' &
  curl -d 'entry=t3.' ${i} -X 'POST' 'http://10.1.0.3:80/board' &
  curl -d 'entry=t4.' ${i} -X 'POST' 'http://10.1.0.4:80/board' &
  [...]
done
```

When the system has been tested with more than 8 nodes, the corresponding POST messages has been added to the script (e.g. ``` curl -d 'entry=t9.' ${i} -X 'POST' 'http://10.1.0.9:80/board' ```)
