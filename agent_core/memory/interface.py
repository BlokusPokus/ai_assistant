"""
Abstract MemoryInterface defining the contract for memory implementations.

📁 memory/interface.py
Abstract memory interface. Defines query() and add() methods. 
Can be implemented using any backend.
"""


class MemoryInterface:
    def query(self, query: str, k: int = 5):
        """
        Search memory for relevant context.

        Args:
            query (str): Input to search
            k (int): Number of top results to return

        Returns:
            List[Dict]: List of memory chunks
        """
        raise NotImplementedError

    def add(self, content: str, metadata: dict):
        """
        Add a new memory record.

        Args:
            content (str): Raw text to embed and store
            metadata (dict): Associated metadata
        """
        raise NotImplementedError
