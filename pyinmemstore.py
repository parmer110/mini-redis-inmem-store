import sys
from typing import Dict, Optional
import threading
import time
from collections import defaultdict


class PyInMemStore:
    """
    A simplified in-memory key-value store similar to Redis.

    Attributes:
        key_value_pairs (Dict[str, str]): A dictionary to store key-value pairs.
        expiry (Dict[str, float]): A dictionary to store expiry time for keys.
        creation_times (Dict[str, float]): A dictionary to store creation time for keys.
        lock (threading.Lock): A lock for thread safety.
    """

    def __init__(self) -> None:
        """
        Initializes the PyInMemStore class.
        """
        self.key_value_pairs: Dict[str, str] = defaultdict(str)
        self.expiry: Dict[str, float] = defaultdict(lambda: float("inf"))
        self.creation_times: Dict[str, float] = defaultdict(float)
        self.lock = threading.Lock()
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self.cleanup_thread.start()

    def set(self, key: str, value: str) -> None:
        """
        Sets the value for a given key.

        Args:
            key (str): The key to set.
            value (str): The value to set for the key.
        """
        with self.lock:
            self.key_value_pairs[key] = value
            self.creation_times[key] = time.time()

    def get(self, key: str) -> Optional[str]:
        """
        Retrieves the value for a given key.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            str: The value associated with the key, or None if the key does not exist.
        """
        with self.lock:
            return self.key_value_pairs.get(key)

    def delete(self, key: str) -> None:
        """
        Deletes a key and its associated value.

        Args:
            key (str): The key to delete.
        """
        with self.lock:
            if key in self.key_value_pairs:
                del self.key_value_pairs[key]
                del self.expiry[key]
                del self.creation_times[key]

    def expire(self, key: str, seconds: int) -> None:
        """
        Sets the expiry time for a given key.

        Args:
            key (str): The key to set expiry time for.
            seconds (int): The number of seconds until the key expires.
        """
        with self.lock:
            if key in self.key_value_pairs:
                if seconds > 0:
                    self.expiry[key] = time.time() + seconds
                else:
                    self.expiry[key] = -1  # Set expiry to -1 for non-positive seconds

    def ttl(self, key: str) -> int:
        """
        Returns the remaining time to live (TTL) for a given key.

        Args:
            key (str): The key to check TTL for.

        Returns:
            int: The remaining time to live in seconds, or -1 if the key exists but does not have a timeout,
                or -2 if the key does not exist.
        """
        with self.lock:
            if key in self.key_value_pairs:
                remaining_time = self.expiry[key] - time.time()
                return max(0, int(remaining_time))
            else:
                return -2

    def _cleanup_expired_keys(self) -> None:
        """
        Removes expired keys from the store.
        """
        while True:
            now = time.time()
            with self.lock:
                expired_keys = [key for key, expiry_time in self.expiry.items() if expiry_time < now]
                for key in expired_keys:
                    del self.key_value_pairs[key]
                    del self.expiry[key]
                    del self.creation_times[key]
            time.sleep(1)

    def get_all_keys(self) -> list[str]:
        """
        Returns a list of all keys in the store.

        Returns:
            list: A list of all keys in the store.
        """
        with self.lock:
            return list(self.key_value_pairs.keys())
