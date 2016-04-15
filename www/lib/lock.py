import threading
import redis

__author__ = "Mateusz Kobos"

class RedisRWLock:
    """
    Original code in http://code.activestate.com/recipes/577803-reader-writer-lock-with-priority-for-writers/
    Adapted for using with Redis/distributed locking.

    Synchronization object used in a solution of so-called distributed second
    readers-writers problem. In this problem, many readers can simultaneously
    access a share, and a writer has an exclusive access to this share.
    Additionally, the following constraints should be met:
    1) no reader should be kept waiting if the share is currently opened for
                    reading unless a writer is also waiting for the share,
    2) no writer should be kept waiting for the share longer than absolutely
                    necessary.

    The implementation is based on [1, secs. 4.2.2, 4.2.6, 4.2.7]
    with a modification -- adding an additional lock (C{self.__readers_queue})
    -- in accordance with [2].

    Sources:
    [1] A.B. Downey: "The little book of semaphores", Version 2.1.5, 2008
    [2] P.J. Courtois, F. Heymans, D.L. Parnas:
                    "Concurrent Control with 'Readers' and 'Writers'",
                    Communications of the ACM, 1971 (via [3])
    [3] http://en.wikipedia.org/wiki/Readers-writers_problem
    """
    def __init__(self, redis_obj, key_prefix):
        self.__redis = redis_obj
        self.__key = key_prefix
        self.__read_switch = _LightSwitch(self.__redis, self.__key + '_read_switch')
        self.__write_switch = _LightSwitch(self.__redis, self.__key + '_write_switch')
        self.__no_readers = self.__redis.lock(self.__key + '_no_readers')
        self.__no_writers = self.__redis.lock(self.__key + '_no_readers')
        self.__readers_queue = self.__redis.lock(self.__key + '_readers_queue')
        """A lock giving an even higher priority to the writer in certain
        cases (see [2] for a discussion)"""

    def reader_acquire(self):
        self.__readers_queue.acquire()
        self.__no_readers.acquire()
        self.__read_switch.acquire(self.__no_writers)
        self.__no_readers.release()
        self.__readers_queue.release()

    def reader_release(self):
        self.__read_switch.release(self.__no_writers)

    def writer_acquire(self):
        self.__write_switch.acquire(self.__no_readers)
        self.__no_writers.acquire()

    def writer_release(self):
        self.__no_writers.release()
        self.__write_switch.release(self.__no_readers)

class _LightSwitch:
    """An auxiliary "light switch"-like object. The first thread turns on the
    "switch", the last one turns it off (see [1, sec. 4.2.2] for details)."""
    def __init__(self, redis_obj, key_prefix):
        self.__redis = redis_obj
        self.__key = key_prefix
        self.__counter_key = self.__key + '_counter'
        self.__mutex_key = self.__key + '_mutex'
        self.__mutex = self.__redis.lock(self.__mutex_key)

    def acquire(self, lock):
        self.__mutex.acquire()
        self.__redis.incr(self.__counter_key, 1)
        if self.__redis.getset(self.__counter_key, 0) == 1:
            lock.acquire()
        self.__mutex.release()

    def release(self, lock):
        self.__mutex.acquire()
        self.__redis.decr(self.__counter_key, 1)
        if self.__redis.getset(self.__counter_key, 0) == 0:
            lock.release()
        self.__mutex.release()

class RedisReaderLock:
    def __init__(self, redis_obj, key_prefix):
        self.__lock = RedisRWLock(redis_obj, key_prefix)

    def __enter__(self):
        self.__lock.reader_acquire()

    def __exit__(self, type, value, traceback):
        self.__lock.reader_release()

class RedisWriterLock:
    def __init__(self, redis_obj, key_prefix):
        self.__lock = RedisRWLock(redis_obj, key_prefix)

    def __enter__(self):
        self.__lock.writer_acquire()

    def __exit__(self, type, value, traceback):
        self.__lock.writer_release()
