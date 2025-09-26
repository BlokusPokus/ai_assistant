# Task 094: Note Enhancement Prompt System Improvement

## Context

You are given the following context:

- Current note enhancement system uses generic prompts that don't adapt to different topics
- Note structures are too simple and lack support for sub-pages and hierarchical organization
- The system has basic note type detection but doesn't leverage topic-specific enhancement strategies
- Current prompts are one-size-fits-all and don't provide specialized guidance for different content types

## Current System Analysis

### Existing Architecture

- **LLMNotesEnhancer**: Core service in `src/personal_assistant/tools/notes/llm_notes_enhancer.py`
- **EnhancedNotesTool**: Main tool interface in `src/personal_assistant/tools/notes/enhanced_notes_tool.py`
- **Notion Integration**: Uses Notion pages with basic hierarchical structure
- **Note Types**: Supports meeting, project, personal, research, learning, task, idea, journal, unknown

### Current Prompt Limitations

1. **Generic Approach**: Single prompt template for all note types
2. **Limited Structure**: Basic formatting suggestions without topic-specific guidance
3. **No Sub-page Support**: Cannot create hierarchical note structures
4. **Static Templates**: Prompts don't adapt based on content complexity or domain
5. **Character Limits**: 2000 character limit restricts comprehensive notes \*\*look with notion api if 2000 char is the limit

### Current Prompt Structure

```python
"comprehensive_analysis": """
You are a specialized note analysis AI. Analyze the following note content and provide a comprehensive response.

Note Content: {content}
Note Title: {title}

Please analyze and provide ALL of the following in a single JSON response:
1. Note Type: Choose from meeting, project, personal, research, learning, task, idea, journal, or unknown
2. Key Topics: List 3-5 main subjects or themes
3. Action Items: Extract any tasks, follow-ups, or action items mentioned
4. Important Details: List 3-5 critical pieces of information
5. Structure Suggestions: How to better organize this content (2-3 suggestions)
6. Smart Tags: Generate 3-5 relevant tags for organization and searchability
7. Enhanced Content: Improve the content structure and formatting while preserving meaning
8. Enhanced Title: Generate a clear, descriptive title for this note
9. Confidence Score: Rate your analysis confidence (0.0-1.0)
"""
```

## Task Objectives

### Primary Goals

1. **Topic-Specific Adaptation**: Create specialized prompts for different note types and domains
2. **Hierarchical Structure Support**: Enable creation of sub-pages and complex note hierarchies
3. **Dynamic Prompt Selection**: Implement intelligent prompt selection based on content analysis
4. **Enhanced Structure Templates**: Provide domain-specific formatting and organization patterns

### Secondary Goals

1. **Improved Content Quality**: Better enhancement based on note type and context
2. **Flexible Architecture**: Design system that can easily accommodate new note types
3. **Better User Experience**: More relevant and useful note enhancements
4. **Scalable Design**: Support for complex note structures and relationships

## Technical Requirements

### 1. Topic-Specific Prompt System

- **Meeting Notes**: Focus on attendees, decisions, action items, follow-ups
- **Project Notes**: Emphasize timeline, requirements, milestones, dependencies
- **Learning Notes**: Include source, key concepts, examples, practice exercises
- **Research Notes**: Highlight sources, methodology, findings, implications
- **Personal Notes**: Focus on context, emotions, reminders, personal growth
- **Task Notes**: Prioritize deadlines, status, dependencies, completion criteria

### 2. Hierarchical Structure Support

- **Sub-page Creation**: Ability to create child pages for complex topics
- **Nested Organization**: Support for multi-level note hierarchies
- **Cross-references**: Enhanced linking between related notes
- **Table of Contents**: Automatic generation for complex note structures

### 3. Dynamic Prompt Selection

- **Content Analysis**: Pre-analysis to determine optimal prompt strategy
- **Domain Detection**: Identify specialized domains (technical, creative, business, etc.)
- **Complexity Assessment**: Adapt prompts based on content complexity
- **User Context**: Consider user's note-taking patterns and preferences

### 4. Enhanced Structure Templates

- **Meeting Templates**: Agenda, attendees, discussion points, decisions, action items
- **Project Templates**: Overview, requirements, timeline, milestones, risks
- **Learning Templates**: Source, objectives, key concepts, examples, applications
- **Research Templates**: Hypothesis, methodology, findings, conclusions, references

## Implementation Plan

### Phase 1: Analysis and Design

1. **Current System Audit**: Document all existing prompt templates and their limitations
2. **User Research**: Analyze existing note patterns and enhancement needs
3. **Template Design**: Create topic-specific prompt templates
4. **Architecture Planning**: Design system for dynamic prompt selection

### Phase 2: Core Implementation

1. **Prompt Template System**: Implement topic-specific prompt templates
2. **Dynamic Selection Logic**: Create intelligent prompt selection algorithm
3. **Enhanced Note Types**: Extend note type system with specialized categories
4. **Structure Templates**: Implement domain-specific formatting patterns

### Phase 3: Hierarchical Support

1. **Sub-page Creation**: Implement ability to create child pages
2. **Hierarchy Management**: Add support for multi-level note structures
3. **Cross-referencing**: Enhanced linking and relationship management
4. **Navigation**: Improved navigation for complex note hierarchies

### Phase 4: Testing and Optimization

1. **Template Testing**: Validate topic-specific prompts with real content
2. **Performance Testing**: Ensure system handles complex structures efficiently
3. **User Testing**: Gather feedback on enhanced note quality and usability
4. **Iteration**: Refine prompts and templates based on testing results

## Success Criteria

### Functional Requirements

- [ ] Topic-specific prompts provide more relevant enhancements
- [ ] System can create and manage hierarchical note structures
- [ ] Dynamic prompt selection improves enhancement quality
- [ ] Users can create complex, well-organized note hierarchies

### Quality Metrics

- [ ] Enhanced notes show 30% improvement in structure and clarity
- [ ] Topic-specific enhancements are more relevant than generic ones
- [ ] Hierarchical structures support complex knowledge organization
- [ ] System maintains performance with complex note structures

### User Experience

- [ ] Enhanced notes are more useful and actionable
- [ ] Complex topics can be properly organized and structured
- [ ] System provides intelligent suggestions for note improvement
- [ ] Users can easily navigate and manage note hierarchies

## Technical Considerations

### Architecture Changes

- **Prompt Template System**: New module for managing topic-specific prompts
- **Dynamic Selection**: Enhanced LLMNotesEnhancer with intelligent prompt selection
- **Hierarchy Support**: Extended Notion integration for sub-page creation
- **Structure Templates**: New system for domain-specific formatting

### Integration Points

- **LLMNotesEnhancer**: Core enhancement logic needs significant updates
- **EnhancedNotesTool**: Tool interface needs new parameters for hierarchy support
- **Notion Integration**: Extended to support sub-page creation and management
- **Note Types**: Enhanced enum with specialized categories and subcategories

### Performance Considerations

- **Prompt Selection**: Efficient algorithm for choosing optimal prompts
- **Hierarchy Management**: Optimized queries for complex note structures
- **Content Analysis**: Fast pre-analysis for prompt selection
- **Caching**: Cache frequently used prompts and templates

## Risk Mitigation

### Technical Risks

- **Complexity**: Hierarchical structures may complicate the system
- **Performance**: Dynamic prompt selection may impact response times
- **Integration**: Changes to Notion integration may break existing functionality
- **Testing**: Complex note structures may be difficult to test comprehensively

### Mitigation Strategies

- **Incremental Implementation**: Implement features gradually with thorough testing
- **Fallback Mechanisms**: Maintain generic prompts as fallback options
- **Comprehensive Testing**: Test all note types and hierarchy levels
- **Documentation**: Maintain clear documentation for all new features

## Next Steps

1. **Complete Current Analysis**: Finish documenting all existing limitations
2. **Design Prompt Templates**: Create topic-specific prompt templates
3. **Implement Dynamic Selection**: Build intelligent prompt selection system
4. **Add Hierarchy Support**: Implement sub-page creation and management
5. **Test and Iterate**: Validate improvements with real-world usage

## Resources

### Key Files

- `src/personal_assistant/tools/notes/llm_notes_enhancer.py` - Core enhancement logic
- `src/personal_assistant/tools/notes/enhanced_notes_tool.py` - Tool interface
- `src/personal_assistant/tools/notion_pages/` - Notion integration
- `docs/architecture/tasks/064_enhanced_notes_tool_with_llm/` - Previous implementation docs

### Dependencies

- Notion API for sub-page creation
- LLM client for enhanced prompt processing
- Database for note metadata and relationships
- User context for personalization

This task represents a significant enhancement to the note-taking system, moving from generic, simple notes to intelligent, topic-specific, hierarchical knowledge management.
