# LRUCache
It is a cache where the nodes can be evicted by least recently used and time to live logic.
The time to live is a counter not a time.

## Execution

### Python Version                                
It is suggested to use any version 3.x

### Unit Tests

There are unit tests covering the code.
They cover the expectations on data, logic and threading locking.
To verify the unit tests, just run in the terminal the command

- `python3 -m unittest discover -p "*_test.py"`

or execute the *main_test.py*.

## Diagrams

### Set Diagram
![Diagram of set method](img/Set_Diagram.jpg?raw=true "Diagram of set method")

### Get Diagram
![Diagram of get method](img/Get_Diagram.jpg?raw=true "Diagram of get method")
