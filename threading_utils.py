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
        
    def load_async(self, operation: Callable, callback: Callable, error_callback: Callable = None, *args, **kwargs):
        """
        Execute operation in background thread.
        
        Args:
            operation: Function to run in background
            callback: Function to call on success (receives result)
            error_callback: Function to call on error (receives exception)
            *args, **kwargs: Arguments for operation
            
        Returns:
            Callable: A checker function to be called periodically (e.g. via root.after)
        """
        def worker():
            try:
                result = operation(*args, **kwargs)
                self.queue.put(('success', result))
            except Exception as e:
                self.queue.put(('error', e))
                
        self.is_loading = True
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
        return lambda: self._check_queue(callback, error_callback)
    
    def _check_queue(self, callback, error_callback):
        """Check queue for results. Returns True if finished, False if still running."""
        try:
            status, data = self.queue.get_nowait()
            self.is_loading = False
            
            if status == 'success':
                if callback:
                    callback(data)
            elif status == 'error':
                if error_callback:
                    error_callback(data)
                else:
                    # Fallback if no error callback provided
                    print(f"Async Error: {data}")
            return True
        except queue.Empty:
            return False
