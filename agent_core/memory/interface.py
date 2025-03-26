"""
Abstract MemoryInterface defining the contract for memory implementations.

📁 memory/interface.py
Abstract memory interface. Defines query() and add() methods. 
Can be implemented using any backend.
"""


class MemoryInterface:
    def query(self, user_id: int, query: str, k: int = 5):
        """
        Search memory for relevant context.

        Args:
            user_id (int): ID of the user
            query (str): Input to search
            k (int): Number of top results to return

        Returns:
            List[Dict]: List of memory chunks
        """
        raise NotImplementedError

    def add(self, user_id: int, content: str, metadata: dict):
        """
        Add a new memory record.

        Args:
            user_id (int): ID of the user
            content (str): Raw text to store
            metadata (dict): Associated metadata
        """
        raise NotImplementedError
