"""
Notion Formatter

Converts markdown-formatted content to proper Notion blocks with rich text formatting.
Handles headings, bold, italic, bullet points, numbered lists, and other formatting.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class FormattedBlock:
    """Represents a formatted block for Notion"""
    type: str
    content: List[Dict[str, Any]]
    children: Optional[List['FormattedBlock']] = None


class NotionFormatter:
    """Converts markdown content to Notion blocks with proper formatting"""
    
    def __init__(self):
        self.max_block_length = 2000  # Notion's limit per block
    
    def format_content_to_blocks(self, content: str) -> List[Dict[str, Any]]:
        """
        Convert markdown content to Notion blocks
        
        Args:
            content: Markdown-formatted content
            
        Returns:
            List of Notion block objects
        """
        try:
            blocks = []
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Handle headings
                if line.startswith('#'):
                    block = self._create_heading_block(line)
                    if block:
                        blocks.append(block)
                
                # Handle bullet lists
                elif line.startswith('- ') or line.startswith('* '):
                    bullet_blocks, i = self._create_bullet_list_blocks(lines, i)
                    blocks.extend(bullet_blocks)
                    continue
                
                # Handle numbered lists
                elif re.match(r'^\d+\.\s+', line):
                    numbered_blocks, i = self._create_numbered_list_blocks(lines, i)
                    blocks.extend(numbered_blocks)
                    continue
                
                # Handle regular paragraphs
                else:
                    block = self._create_paragraph_block(line)
                    if block:
                        blocks.append(block)
                
                i += 1
            
            return blocks
            
        except Exception as e:
            # Fallback to simple paragraph if formatting fails
            return [self._create_simple_paragraph_block(content)]
    
    def _create_heading_block(self, line: str) -> Optional[Dict[str, Any]]:
        """Create a heading block"""
        try:
            # Count heading level
            level = 0
            while level < len(line) and line[level] == '#':
                level += 1
            
            if level > 3:  # Notion supports up to heading_3
                level = 3
            
            # Extract heading text
            heading_text = line[level:].strip()
            if not heading_text:
                return None
            
            # Create rich text with formatting
            rich_text = self._parse_rich_text(heading_text)
            
            return {
                "object": "block",
                "type": f"heading_{level}",
                f"heading_{level}": {
                    "rich_text": rich_text
                }
            }
            
        except Exception:
            return None
    
    def _create_bullet_list_blocks(self, lines: List[str], start_idx: int) -> tuple[List[Dict[str, Any]], int]:
        """Create bullet list blocks"""
        blocks = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            if line.startswith('- ') or line.startswith('* '):
                # Extract bullet text
                bullet_text = line[2:].strip()
                rich_text = self._parse_rich_text(bullet_text)
                
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": rich_text
                    }
                })
            else:
                break
            
            i += 1
        
        return blocks, i
    
    def _create_numbered_list_blocks(self, lines: List[str], start_idx: int) -> tuple[List[Dict[str, Any]], int]:
        """Create numbered list blocks"""
        blocks = []
        i = start_idx
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if match:
                # Extract numbered text
                numbered_text = match.group(2).strip()
                rich_text = self._parse_rich_text(numbered_text)
                
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": rich_text
                    }
                })
            else:
                break
            
            i += 1
        
        return blocks, i
    
    def _create_paragraph_block(self, line: str) -> Optional[Dict[str, Any]]:
        """Create a paragraph block"""
        if not line:
            return None
        
        rich_text = self._parse_rich_text(line)
        
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text
            }
        }
    
    def _create_simple_paragraph_block(self, content: str) -> Dict[str, Any]:
        """Create a simple paragraph block as fallback"""
        # Truncate if too long
        if len(content) > self.max_block_length:
            content = content[:self.max_block_length - 3] + "..."
        
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        }
    
    def _parse_rich_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse markdown text into Notion rich text format"""
        try:
            # For now, let's use a simple approach that avoids conflicts
            # We'll handle bold text first, then italic, then code
            
            # Step 1: Handle bold text (**text**)
            result = []
            remaining = text
            
            while '**' in remaining:
                before, after = remaining.split('**', 1)
                if '**' in after:
                    bold_content, after = after.split('**', 1)
                    if before:
                        result.extend(self._parse_rich_text(before))
                    result.append(self._create_text_object(bold_content, 'bold'))
                    remaining = after
                else:
                    # Unmatched **, treat as plain text
                    result.extend(self._parse_rich_text(before + '**' + after))
                    remaining = ''
                    break
            
            if remaining:
                # Step 2: Handle italic text (*text*) - but avoid conflicts with bold
                while '*' in remaining:
                    before, after = remaining.split('*', 1)
                    if '*' in after:
                        italic_content, after = after.split('*', 1)
                        if before:
                            result.extend(self._parse_rich_text(before))
                        result.append(self._create_text_object(italic_content, 'italic'))
                        remaining = after
                    else:
                        # Unmatched *, treat as plain text
                        result.extend(self._parse_rich_text(before + '*' + after))
                        remaining = ''
                        break
            
            if remaining:
                # Step 3: Handle code text (`text`)
                while '`' in remaining:
                    before, after = remaining.split('`', 1)
                    if '`' in after:
                        code_content, after = after.split('`', 1)
                        if before:
                            result.extend(self._parse_rich_text(before))
                        result.append(self._create_text_object(code_content, 'code'))
                        remaining = after
                    else:
                        # Unmatched `, treat as plain text
                        result.extend(self._parse_rich_text(before + '`' + after))
                        remaining = ''
                        break
            
            if remaining:
                result.append(self._create_text_object(remaining))
            
            return result if result else [self._create_text_object(text)]
            
        except Exception:
            # Fallback to simple text
            return [self._create_text_object(text)]
    
    def _create_text_object(self, text: str, format_type: str = None) -> Dict[str, Any]:
        """Create a Notion text object with optional formatting"""
        annotations = {
            "bold": False,
            "italic": False,
            "underline": False,
            "strikethrough": False,
            "code": False,
            "color": "default"
        }
        
        if format_type == 'bold':
            annotations["bold"] = True
        elif format_type == 'italic':
            annotations["italic"] = True
        elif format_type == 'code':
            annotations["code"] = True
        
        return {
            "type": "text",
            "text": {
                "content": text
            },
            "annotations": annotations
        }
    
    def split_long_content(self, content: str) -> List[str]:
        """Split content into chunks that fit within Notion's limits"""
        if len(content) <= self.max_block_length:
            return [content]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.max_block_length:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                else:
                    # Single paragraph is too long, split it
                    chunks.extend(self._split_long_paragraph(paragraph))
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """Split a long paragraph into smaller chunks"""
        if len(paragraph) <= self.max_block_length:
            return [paragraph]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.max_block_length:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    # Single sentence is too long, force split
                    chunks.append(sentence[:self.max_block_length])
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
