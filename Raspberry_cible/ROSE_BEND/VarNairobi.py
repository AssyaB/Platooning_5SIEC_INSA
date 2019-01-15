# coding: utf-8

from threading import *

global conn
global addr
global COM_TURN
COM_TURN = 'p'
global semaphore_TURN
semaphore_TURN = BoundedSemaphore(1)
global IPPLAT
global stop_all
stop_all = Event()
stop_all.clear()