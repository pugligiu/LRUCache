import unittest
from threading import Thread
import time
from cacheThreads import LRUCache


class LRUCache_test_data(unittest.TestCase):
    '''
        Test Suite to verify the data config of the cache
    '''

    def setUp(self):
        self.c0 = LRUCache()
        self.c1 = LRUCache(10, 5)

    def tearDown(self):
        del self.c0
        del self.c1

    def test_dataLRUCache(self):
        self.assertEqual(self.c0.cache_capacity, 1)
        self.assertEqual(self.c0.cache_ttl, 1)
        self.assertEqual(self.c1.cache_capacity, 10)
        self.assertEqual(self.c1.cache_ttl, 5)

    def test_excpetionLRUCache(self):
        with self.assertRaisesRegex(ValueError, "The capacity has to be an integer bigger than 0"):
            LRUCache("1")
        with self.assertRaisesRegex(ValueError, "The time to live has to be an integer bigger than 0"):
            LRUCache(ttl="1")


class LRUCache_test_logic(unittest.TestCase):
    '''
        Test Suite to verify the cache logic
    '''

    def setUp(self):
        self.c0 = LRUCache()
        self.c1 = LRUCache(5, 3)

    def tearDown(self):
        del self.c0
        del self.c1

    def test_insertItems(self):
        '''
            Verify correct setting of the node and the LRU moves
        '''
        # Insert one node and verify all the fields
        self.c0.set(1, 10, 2)
        self.assertEqual(self.c0.cache_nodes, 1)
        self.assertEqual(self.c0.head, self.c0.linkdict[1])
        self.assertEqual(self.c0.head, self.c0.tail)
        self.assertEqual(self.c0.head.left, None)
        self.assertEqual(self.c0.head.right, None)
        self.assertEqual(self.c0.head.key, 1)
        self.assertEqual(self.c0.head.value, 10)
        self.assertEqual(self.c0.head.ttl, 2)

        # Insert first node and verify the ttl default
        self.c1.set(1, 10)
        first_node = self.c1.head
        self.assertEqual(self.c1.head, self.c1.linkdict[1])
        self.assertEqual(self.c1.head.ttl, self.c1.cache_ttl)
        self.assertEqual(self.c1.tail, first_node)

        # Insert second node and verify the ttl default and the correct link
        # list 2 -> 1
        self.c1.set(2, 20, 1)
        second_node = self.c1.head
        self.assertEqual(self.c1.head, self.c1.linkdict[2])
        self.assertEqual(self.c1.head.ttl, 1)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right, first_node)
        self.assertEqual(self.c1.tail, first_node)

        # Add third node
        # list 3 -> 2 -> 1
        self.c1.set(3, 30)
        self.assertEqual(self.c1.head, self.c1.linkdict[3])
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right, second_node)
        self.assertEqual(second_node.left, self.c1.head)
        self.assertEqual(second_node.right, first_node)
        self.assertEqual(first_node.left, second_node)
        self.assertEqual(first_node.right, None)

        self.assertEqual(self.c1.cache_nodes, 3)

    def test_updateItem(self):
        '''
            Adding same key causes update and move to head of the list
        '''
        self.c1.set(1, 10)
        first_node = self.c1.head
        self.c1.set(2, 20)
        second_node = self.c1.head
        self.c1.set(1, 30, 5)
        # list 1 -> 2
        self.assertEqual(self.c1.head, first_node)
        self.assertEqual(self.c1.head.key, 1)
        self.assertEqual(self.c1.head.value, 30)
        self.assertEqual(self.c1.head.ttl, 5)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right, second_node)
        self.assertEqual(second_node.left, first_node)
        self.assertEqual(second_node.right, None)

        self.assertEqual(self.c1.cache_nodes, 2)

    def test_getItems(self):
        '''
            Get an item causes the move to head of the list and change of ttl
        '''
        self.c0.set(1, 10, 2)
        n = self.c0.get(1)
        self.assertEqual(self.c0.head.key, 1)
        self.assertEqual(self.c0.head.ttl, 1)
        self.assertEqual(n, 10)
        n = self.c0.get(2)
        self.assertEqual(n, None)

        self.c1.set(1, 10)
        first_node = self.c1.head
        self.c1.set(2, 20, 5)
        second_node = self.c1.head
        self.c1.set(3, 30, 6)
        third_node = self.c1.head

        # pick from the tail 3 -> 2 -> 1
        n = self.c1.get(1)
        # list 1 -> 3 -> 2
        self.assertEqual(n, 10)
        self.assertEqual(self.c1.head, first_node)
        self.assertEqual(self.c1.tail, second_node)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right, third_node)
        self.assertEqual(self.c1.tail.right, None)

        # pick from the middle 1 -> 3 -> 2
        n = self.c1.get(3)
        # list 3 -> 1 -> 2
        self.assertEqual(n, 30)
        self.assertEqual(self.c1.head, third_node)
        self.assertEqual(self.c1.head.right, first_node)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.tail, second_node)
        self.assertEqual(self.c1.tail.right, None)
        self.assertEqual(self.c1.tail.left, first_node)
        self.assertEqual(first_node.right, second_node)
        self.assertEqual(first_node.left, third_node)

    def test_evictionLRU(self):
        '''
            If the cache is full, the tail has to be evicted
        '''
        for i in range(1, 7):
            self.c1.set(i, 10 * i)

        # list 6 -> 5 -> 4 -> 3 -> 2
        self.assertEqual(self.c1.tail.key, 2)
        n = self.c1.get(1)
        self.assertEqual(n, None)

    def test_evictionTTL(self):
        '''
            If one value is read over ttl times, it will be evicted
        '''

        self.c1.set(1, 10, 1)
        self.c1.set(2, 20, 1)
        for i in range(3, 6):
            self.c1.set(i, 10 * i)

        # list 5 -> 4 -> 3 -> 2 -> 1
        # eviction any node
        n = self.c1.get(2)
        self.assertEqual(self.c1.head.key, 5)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right.key, 4)
        self.assertEqual(self.c1.tail.key, 1)
        self.assertEqual(self.c1.tail.right, None)
        n = self.c1.get(2)
        self.assertEqual(n, None)

        # list 5 -> 4 -> 3 -> 1
        # eviction tail node
        n = self.c1.get(1)
        self.assertEqual(self.c1.head.key, 5)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.head.right.key, 4)
        self.assertEqual(self.c1.tail.key, 3)
        self.assertEqual(self.c1.tail.right, None)
        n = self.c1.get(1)
        self.assertEqual(n, None)

        # list 5 -> 4 -> 3
        for i in range(3):
            n = self.c1.get(4)
        self.assertEqual(n, 40)
        n = self.c1.get(4)
        self.assertEqual(n, None)
        self.assertEqual(self.c1.head.key, 5)
        self.assertEqual(self.c1.tail.key, 3)
        self.assertEqual(self.c1.head.right.key, 3)
        self.assertEqual(self.c1.head.left, None)
        self.assertEqual(self.c1.tail.left.key, 5)
        self.assertEqual(self.c1.tail.right, None)

        self.assertEqual(self.c1.cache_nodes, 2)


class LRUCache_test_multithreading_behaviour(unittest.TestCase):
    '''
        Test Suite to verify the multithread working
    '''

    def setUp(self):
        def thread_1(c):
            c.lock.acquire()
            time.sleep(0.01)
            c.lock.release()

        def thread_2(c):
            c.set(1, 10)

        def thread_3(c):
            c.get(1)

        self.c = LRUCache(10, 5)
        self.t1 = Thread(target=thread_1, args=[self.c])
        self.t2 = Thread(target=thread_2, args=[self.c])
        self.t3 = Thread(target=thread_3, args=[self.c])

    def tearDown(self):
        del self.c
        del self.t1
        del self.t2
        del self.t3

    def test_lockSet(self):
        '''
            Lock on LRUCache.set method
        '''
        self.t1.start()
        self.t2.start()
        self.assertEqual(self.t2.is_alive(), True)
        self.assertEqual(self.t1.is_alive(), True)
        self.t2.join()
        self.assertEqual(self.c.head.value, 10)

    def test_lockGet(self):
        '''
            Lock on LRUCache.get method
        '''
        self.c.set(1, 10)
        self.t1.start()
        self.t3.start()
        self.assertEqual(self.t3.is_alive(), True)
        self.assertEqual(self.t1.is_alive(), True)
        self.assertEqual(self.c.head.ttl, 5)
        self.t3.join()
        self.assertEqual(self.c.head.ttl, 4)
