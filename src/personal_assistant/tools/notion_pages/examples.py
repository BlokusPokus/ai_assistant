#!/usr/bin/env python3
"""
Examples of using NotionPagesTool

This file demonstrates various usage patterns for the NotionPagesTool.
Make sure you have NOTION_API_KEY and NOTION_ROOT_PAGE_ID set in your environment.
"""

from personal_assistant.tools.notion_pages.notion_pages_tool import NotionPagesTool
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


async def basic_usage_example():
    """Basic usage example showing CRUD operations"""
    print("=== Basic Usage Example ===")

    tool = NotionPagesTool()

    # 1. Create a note page
    print("\n1. Creating a note page...")
    result = await tool.create_note_page(
        title="Project Ideas",
        content="Here are some ideas for new projects:\n- AI-powered task manager\n- Smart home automation\n- Learning platform",
        tags="ideas,projects,planning",
        category="Work"
    )
    print(f"Result: {result}")

    # 2. Create another note page
    print("\n2. Creating another note page...")
    result = await tool.create_note_page(
        title="Meeting Notes - Q1 Planning",
        content="Q1 Planning Meeting:\n- Review Q4 results\n- Set Q1 goals\n- Assign responsibilities",
        tags="meeting,planning,q1",
        category="Work"
    )
    print(f"Result: {result}")

    # 3. Get table of contents
    print("\n3. Getting table of contents...")
    toc = await tool.get_table_of_contents()
    print(f"Table of Contents:\n{toc}")

    # 4. Search for notes
    print("\n4. Searching for notes...")
    search_result = await tool.search_notes("planning")
    print(f"Search Results:\n{search_result}")


async def linking_example():
    """Example showing bidirectional linking between pages"""
    print("\n=== Linking Example ===")

    tool = NotionPagesTool()

    # 1. Create a source page
    print("\n1. Creating source page...")
    result = await tool.create_note_page(
        title="Project Overview",
        content="This project involves multiple components and phases.",
        tags="project,overview",
        category="Work"
    )
    print(f"Result: {result}")

    # 2. Create a target page
    print("\n2. Creating target page...")
    result = await tool.create_note_page(
        title="Technical Specifications",
        content="Detailed technical requirements and architecture.",
        tags="technical,specs",
        category="Work"
    )
    print(f"Result: {result}")

    # 3. Get the page IDs (in a real scenario, you'd store these)
    print("\n3. Getting page IDs...")
    search_result = await tool.search_notes("Project Overview")
    print(f"Search for Project Overview: {search_result}")

    # Note: In a real scenario, you'd extract the page ID from the search result
    # For this example, we'll assume we have the IDs

    # 4. Create a link between pages
    print("\n4. Creating link between pages...")
    # You would need to replace these with actual page IDs from your search results
    # result = await tool.create_link("source_page_id", "Technical Specifications")
    print("Note: Link creation requires actual page IDs from search results")

    # 5. Get backlinks
    print("\n5. Getting backlinks...")
    # result = await tool.get_backlinks("target_page_id")
    print("Note: Backlink retrieval requires actual page IDs from search results")


async def advanced_usage_example():
    """Advanced usage example showing more complex operations"""
    print("\n=== Advanced Usage Example ===")

    tool = NotionPagesTool()

    # 1. Create multiple categorized notes
    print("\n1. Creating multiple categorized notes...")

    work_notes = [
        ("Client Meeting Notes", "Discussed project requirements and timeline.",
         "client,meeting", "Work"),
        ("Development Log", "Daily development progress and challenges.",
         "development,log", "Work"),
        ("Bug Reports", "Collection of reported bugs and their status.",
         "bugs,reports", "Work")
    ]

    personal_notes = [
        ("Book Recommendations", "Books I want to read and recommendations.",
         "books,reading", "Personal"),
        ("Travel Plans", "Upcoming travel destinations and plans.",
         "travel,plans", "Personal"),
        ("Learning Goals", "Skills I want to learn this year.",
         "learning,goals", "Personal")
    ]

    for title, content, tags, category in work_notes + personal_notes:
        result = await tool.create_note_page(title, content, tags, category)
        print(f"Created: {title}")

    # 2. Get organized table of contents
    print("\n2. Getting organized table of contents...")
    toc = await tool.get_table_of_contents()
    print(f"Organized Table of Contents:\n{toc}")

    # 3. Search with filters
    print("\n3. Searching with category filter...")
    work_results = await tool.search_notes("", category="Work")
    print(f"Work notes:\n{work_results}")

    print("\n4. Searching with tag filter...")
    meeting_results = await tool.search_notes("", tags="meeting")
    print(f"Meeting-related notes:\n{meeting_results}")


async def content_management_example():
    """Example showing content management operations"""
    print("\n=== Content Management Example ===")

    tool = NotionPagesTool()

    # 1. Create a note
    print("\n1. Creating a note...")
    result = await tool.create_note_page(
        title="Draft Document",
        content="This is the initial draft content.",
        tags="draft,work-in-progress",
        category="Work"
    )
    print(f"Result: {result}")

    # 2. Read the note
    print("\n2. Reading the note...")
    # You would need to get the page ID from the create result
    # For this example, we'll search for it
    search_result = await tool.search_notes("Draft Document")
    print(f"Search result: {search_result}")

    # 3. Update the note
    print("\n3. Updating the note...")
    # result = await tool.update_note_page(
    #     page_id="actual_page_id",
    #     content="This is the updated draft content with more information.",
    #     tags="draft,work-in-progress,updated"
    # )
    print("Note: Update requires actual page ID from search results")

    # 4. Delete the note
    print("\n4. Deleting the note...")
    # result = await tool.delete_note_page("actual_page_id")
    print("Note: Delete requires actual page ID from search results")


async def main():
    """Run all examples"""
    print("NotionPagesTool Examples")
    print("=" * 50)

    try:
        await basic_usage_example()
        await linking_example()
        await advanced_usage_example()
        await content_management_example()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nNote: Some operations require actual page IDs from previous operations.")
        print("In a real application, you would store and manage these IDs.")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
