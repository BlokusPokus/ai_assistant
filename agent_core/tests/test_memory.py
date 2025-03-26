import unittest
from agent_core.memory.client import MockMemoryDBClient
from agent_core.memory.memory import Memory


class TestMemory(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.client = MockMemoryDBClient()
        self.memory = Memory(self.client)

    def test_add_record(self):
        """Test adding a record to the memory."""
        user_id = 1
        content = "This is a test content."
        metadata = {"key": "value"}

        self.memory.add(user_id, content, metadata)
        records = self.client.query_records(user_id, "test", 1)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["content"], content)
        self.assertEqual(records[0]["metadata"], metadata)

    def test_query_records(self):
        """Test querying records from the memory."""
        user_id = 1
        content1 = "First test content."
        content2 = "Second test content."
        metadata = {"key": "value"}

        self.memory.add(user_id, content1, metadata)
        self.memory.add(user_id, content2, metadata)

        results = self.memory.query(user_id, "Second", 1)
        self.assertEqual(len(results), 1)
        self.assertIn("Second", results[0]["content"])

        results = self.memory.query(user_id, "test", 2)
        self.assertEqual(len(results), 2)

    def test_no_results(self):
        """Test querying with no results."""
        user_id = 1
        results = self.memory.query(user_id, "nonexistent", 1)
        self.assertEqual(len(results), 0)


def main():
    # Initialize memory with a mock client
    client = MockMemoryDBClient()
    memory = Memory(client)

    # Add some records
    user_id = 1
    memory.add(user_id, "This is a test content.", {"key": "value"})
    memory.add(user_id, "Another piece of content.", {"key": "another_value"})

    # Query the memory
    results = memory.query(user_id, "test", 1)
    print("Query Results for 'test':", results)

    results = memory.query(user_id, "Another", 1)
    print("Query Results for 'Another':", results)

    # Query with no expected results
    results = memory.query(user_id, "nonexistent", 1)
    print("Query Results for 'nonexistent':", results)


if __name__ == '__main__':
    unittest.main()
