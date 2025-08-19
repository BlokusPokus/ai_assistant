# Notion Pages Tool

A comprehensive tool for managing Notion note pages with bidirectional linking, following the Obsidian-style approach.

## Features

- **Page-based note structure** with main table of contents page
- **Bidirectional linking** between pages using `[[Page Name]]` syntax
- **Auto-updating table of contents** organized by categories
- **Full CRUD operations** for note pages
- **Rich text support** with Notion's block system
- **Search functionality** across all notes
- **Category and tag organization**

## Setup

1. **Environment Variables**: Set the following in your `.env` file:

   ```env
   NOTION_API_KEY=your_notion_api_key_here
   NOTION_ROOT_PAGE_ID=your_root_page_id_here
   ```

2. **Notion Integration**: Make sure your Notion integration has access to the workspace and root page.

## Available Tools

### 1. create_note_page

Create a new note page under the main table of contents.

**Parameters:**

- `title` (required): Title of the note page
- `content` (required): Content of the note page
- `tags` (optional): Comma-separated tags for categorization
- `category` (optional): Category for organizing the note

**Example:**

```python
result = await tool.create_note_page(
    title="Meeting Notes",
    content="Discussed project timeline and next steps.",
    tags="meeting,project,planning",
    category="Work"
)
```

### 2. read_note_page

Read note content and properties by page ID or title.

**Parameters:**

- `page_identifier` (required): Page ID or page title to read

**Example:**

```python
result = await tool.read_note_page("Meeting Notes")
# or
result = await tool.read_note_page("page_id_here")
```

### 3. update_note_page

Update note content and properties by page ID.

**Parameters:**

- `page_id` (required): Page ID to update
- `content` (optional): New content for the note page
- `title` (optional): New title for the note page
- `tags` (optional): New comma-separated tags
- `category` (optional): New category

**Example:**

```python
result = await tool.update_note_page(
    page_id="page_id_here",
    content="Updated content with new information.",
    tags="meeting,project,planning,updated"
)
```

### 4. delete_note_page

Delete a note page by page ID (archives the page).

**Parameters:**

- `page_id` (required): Page ID to delete

**Example:**

```python
result = await tool.delete_note_page("page_id_here")
```

### 5. search_notes

Search across all note pages.

**Parameters:**

- `query` (required): Search query
- `category` (optional): Filter by category
- `tags` (optional): Filter by comma-separated tags

**Example:**

```python
result = await tool.search_notes("project", category="Work")
```

### 6. get_table_of_contents

Get the current table of contents from the main page.

**Parameters:** None

**Example:**

```python
result = await tool.get_table_of_contents()
```

### 7. create_link

Create a link between two pages using Obsidian-style syntax.

**Parameters:**

- `source_page_id` (required): Page ID of the source page
- `target_page_title` (required): Title of the target page to link to

**Example:**

```python
result = await tool.create_link(
    source_page_id="source_page_id",
    target_page_title="Target Page Title"
)
```

### 8. get_backlinks

Get all pages that link to the specified page.

**Parameters:**

- `page_id` (required): Page ID to find backlinks for

**Example:**

```python
result = await tool.get_backlinks("page_id_here")
```

## Page Structure

The tool creates the following structure in Notion:

```
Main Page (Table of Contents)
├── Welcome message
├── Category 1
│   ├── Note Page 1
│   └── Note Page 2
├── Category 2
│   ├── Note Page 3
│   └── Note Page 4
└── Uncategorized
    └── Note Page 5
```

## Linking System

### Forward Links

Use `[[Page Name]]` syntax in your note content to create links to other pages.

### Backlinks

The tool automatically tracks which pages link to each page, providing a reverse reference system.

### Example

If you have a note called "Project Planning" and you write "See [[Meeting Notes]] for details", the "Meeting Notes" page will show a backlink to "Project Planning".

## Categories and Tags

- **Categories**: Use to group related notes (e.g., Work, Personal, Learning)
- **Tags**: Use for more specific classification (e.g., meeting, project, idea)

## Error Handling

The tool includes comprehensive error handling:

- API errors are caught and logged
- User-friendly error messages are returned
- Non-critical operations (like TOC updates) don't fail the main functionality

## Future Enhancements

- Graph view of page relationships
- Advanced search and filtering
- Template system for note types
- Collaborative editing features
- Export/import functionality
- RAG system integration

## Testing

Run the test script to verify functionality:

```bash
cd src/personal_assistant/tools/notion_pages
python test_notion_pages.py
```

Make sure you have the required environment variables set before testing.

## Integration

The tool follows the Personal Assistant framework patterns:

- Class-based tool structure
- Async methods for all operations
- Proper error handling and logging
- Tool registration in the main system

## Notes

- The tool automatically creates a "Table of Contents" page if it doesn't exist
- All note pages are created as children of the main page
- The table of contents is automatically updated when pages are created/deleted
- Pages are archived (not permanently deleted) when using delete_note_page
