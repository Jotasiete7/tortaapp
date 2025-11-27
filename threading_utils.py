"""
Threading Utils - Async Data Loader
====================================
Handles heavy operations outside the GUI thread
"""

import threading
import queue
from typing import Callable


class AsyncDataLoader:
    """Async data loader using threading and queue."""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.is_loading = False
        
    def load_async(self, operation: Callable, callback: Callable, *args, **kwargs):
        """Execute operation in background thread."""
        def worker():
            try:
                result = operation(*args, **kwargs)
                self.queue.put(('success', result))
            except Exception as e:
                self.queue.put(('error', e))
                
        self.is_loading = True
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
        return lambda: self._check_queue(callback)
    
    def _check_queue(self, callback):
        """Check queue for results"""
        try:
            status, data = self.queue.get_nowait()
            self.is_loading = False
            callback(status, data)
            return True
        except queue.Empty:
            return False
