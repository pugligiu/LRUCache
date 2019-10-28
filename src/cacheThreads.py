from threading import Lock


class Node:
    '''
        Simple node of the doubly linked dictionary. The key is the
        same used in the dictionary.
    '''

    def __init__(self, key, value, left, right, ttl):
        '''
            Node Constructor
                @param key, immutable data type
                @param value, any type
                @param left, a Node or None
                @param right, a Node or None
                @param ttl, an integer
        '''
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.ttl = max(ttl, 1)


class LRUCache:

    # config items
    cache_capacity = 1
    cache_ttl = 1

    # @param capacity, an integer
    def __init__(self, capacity=None, ttl=None):
        '''
            Cache Constructor
                @param capacity, an integer, num of Nodes, minimum is 1
                @param ttl, an integer, default time to live, minimum is 1
                @param pool, an integer, num of threads, minimum is 1
        '''
        if capacity is None:
            capacity = self.cache_capacity
        elif type(capacity) is not int or capacity < 1:
            raise ValueError("The capacity has to be an integer bigger than 0")

        if ttl is None:
            ttl = self.cache_ttl
        elif type(ttl) is not int or ttl < 1:
            raise ValueError("The time to live has to be an integer bigger than 0")

        self.cache_capacity = capacity
        self.cache_ttl = ttl
        # internal counter
        self.cache_nodes = 0
        # key, value data structure
        self.linkdict = dict()
        # head and tail reference
        self.head = None
        self.tail = None
        self.lock = Lock()

    def _remove_node_fromList(self, node):
        '''
            Remove node from the doubly linked list
                @param node, a data Node
        '''
        if node.right is not None:
            node.right.left = node.left
        else:
            self.tail = node.left
        if node.left is not None:
            node.left.right = node.right
        else:
            self.head = node.right

    def _remove_node(self, node):
        '''
            Remove a node from the Cache
                @param node, a data Node
        '''
        self._remove_node_fromList(node)
        del self.linkdict[node.key]
        self.cache_nodes -= 1

    def _update_head(self, node):
        '''
            Update the head node
                @param node, a data Node
        '''
        if self.head is not None:
            self.head.left = node
        else:
            self.tail = node
        node.right = self.head
        self.head = node

    def _move_to_head(self, node):
        '''
            Move the node to the head of the list
                @param node, a data Node
        '''
        self._remove_node_fromList(node)
        node.left = None
        self._update_head(node)

    def _add_node(self, key, value, ttl):
        '''
            Add a node associated to a new key
                @param key, immutable data type
                @param value, any type
                @param ttl, an integer
        '''
        if self.cache_capacity <= self.cache_nodes:
            self._remove_node(self.tail)
        node = Node(key, value, None, None, ttl)
        self._update_head(node)
        self.linkdict[key] = node
        self.cache_nodes += 1

    def get(self, key):
        '''
            Read the value from the cache. This causes the ttl update
            and the eviction based on ttl policy
                @param key, immutable data type
                @return the value or None
        '''
        value = None
        with self.lock:
            if key in self.linkdict:
                node = self.linkdict[key]
                if node.ttl > 1:
                    node.ttl -= 1
                    self._move_to_head(node)
                else:
                    self._remove_node(node)
                value = node.value
        return value

    def set(self, key, value, ttl=None):
        '''
            Write the value to the cache. If the associated key exists,
            the method causes an update of the value and ttl.
            Eviction policy in place based on LRU policy in case the
            cache is full.
                @param key, immutable data type
                @param value, any type
                @param ttl, an integer
                @return nothing
        '''
        if ttl is None or ttl <= 0:
            ttl = self.cache_ttl
        with self.lock:
            if key in self.linkdict:
                node = self.linkdict[key]
                node.value = value
                node.ttl = ttl
                self._move_to_head(node)
            else:
                self._add_node(key, value, ttl)
