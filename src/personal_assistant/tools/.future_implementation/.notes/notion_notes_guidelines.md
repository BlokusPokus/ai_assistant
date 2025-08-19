# NotionNotesTool Usage Guidelines

## 🎯 Overview

The NotionNotesTool provides comprehensive note management capabilities in Notion, including creation, retrieval, updates, search, and template management. This tool is designed for structured note-taking with enhanced properties for better organization.

## 🚀 When to Use This Tool

### ✅ Perfect Use Cases:

- **Creating structured notes** with titles, content, and metadata
- **Updating existing notes** with new information or status changes
- **Searching notes** with specific criteria (importance, status, category)
- **Managing note templates** for consistent structure
- **Adding database properties** to enhance note organization
- **Organizing information** by importance, status, and category
- **Creating reusable templates** for common note types

### ❌ Avoid Using For:

- **Simple text storage** (use basic text files instead)
- **Real-time collaboration** (Notion has built-in features)
- **Large file attachments** (Notion has size limits)
- **Frequent small updates** (batch updates are more efficient)
- **Binary file storage** (use cloud storage instead)

## 🛠️ Tool Selection Matrix

| Task Type          | Best Tool                 | Alternative    | When to Use                                 |
| ------------------ | ------------------------- | -------------- | ------------------------------------------- |
| Create new note    | `create_note_enhanced`    | `create_note`  | Always prefer enhanced for better structure |
| Update existing    | `update_note`             | Manual editing | When modifying note content or properties   |
| Search by criteria | `search_notes_enhanced`   | `search_notes` | Always use enhanced for better filtering    |
| Template creation  | `create_note_template`    | Manual setup   | For creating reusable note structures       |
| Database setup     | `add_database_properties` | Notion UI      | One-time setup for enhanced properties      |
| Retrieve specific  | `get_note`                | None           | When you have the exact note ID             |

## 📋 Parameter Guidelines

### Content Length & Format:

- **Title**: 1-100 characters (keep concise and descriptive)
- **Summary**: 50-200 characters (brief overview of content)
- **Content**: 1-10,000 characters (detailed information)
- **Tags**: 2-10 tags maximum (avoid over-tagging, use consistent naming)

### Status Values:

- **Draft**: Initial creation, incomplete thoughts, work in progress
- **In Progress**: Actively working on, partially complete
- **Complete**: Finished, reviewed, ready for reference
- **Archived**: No longer relevant, historical reference only

### Importance Levels:

- **High**: Critical information, urgent actions, must-know content
- **Medium**: Important but not urgent, reference material
- **Low**: Nice to have, background information, optional reading

### Categories:

- **Work**: Professional tasks, meetings, projects, career development
- **Personal**: Life events, personal goals, family matters
- **Learning**: Education, skills development, research, tutorials
- **Planning**: Goals, strategies, roadmaps, future planning
- **Research**: Investigations, analysis, data collection, findings

## 🎨 Note Templates & Use Cases

### Template 1: Meeting Notes

**Use when**: User mentions meeting, call, discussion, or collaboration
**Tool**: `create_note_enhanced`
**Suggested Structure**:

```
Title: [Meeting Topic] - [Date]
Category: Work
Status: Draft
Importance: [High/Medium/Low]
Tags: meeting, [participant names], [topic], [project]
Summary: [Brief meeting overview in 1-2 sentences]
Content:
- Attendees: [list of participants]
- Agenda: [points discussed]
- Key Discussion Points: [main topics covered]
- Decisions Made: [conclusions reached]
- Action Items: [tasks assigned with owners]
- Next Steps: [follow-up actions and deadlines]
- Notes: [additional observations or context]
```

**Example Usage**:

```
User: "Create a note about my meeting with the development team tomorrow"
Assistant: Use create_note_enhanced with:
- Title: "Dev Team Meeting - [Tomorrow's Date]"
- Category: Work
- Status: Draft
- Tags: meeting, dev-team, development, planning
- Summary: "Planning session for upcoming sprint and feature development"
```

### Template 2: Project Notes

**Use when**: User mentions project, task, goal, or initiative
**Tool**: `create_note_enhanced`
**Suggested Structure**:

```
Title: [Project Name]
Category: [Work/Personal/Learning]
Status: In Progress
Importance: [High/Medium/Low]
Tags: project, [project type], [technologies], [team]
Summary: [Project description in 1-2 sentences]
Content:
- Objective: [clear goal statement]
- Scope: [what's included/excluded]
- Timeline: [key milestones and deadlines]
- Resources: [tools, people, budget needed]
- Progress: [current status and achievements]
- Challenges: [obstacles and solutions]
- Next Steps: [immediate actions required]
- Success Metrics: [how to measure completion]
```

**Example Usage**:

```
User: "I want to start a new project to learn React"
Assistant: Use create_note_enhanced with:
- Title: "React Learning Project"
- Category: Learning
- Status: Draft
- Importance: Medium
- Tags: project, react, learning, frontend, javascript
- Summary: "Personal project to learn React framework through building applications"
```

### Template 3: Research Notes

**Use when**: User mentions research, learning, study, or investigation
**Tool**: `create_note_enhanced`
**Suggested Structure**:

```
Title: [Research Topic]
Category: Learning
Status: Draft
Importance: [High/Medium/Low]
Tags: research, [subject], [source], [methodology]
Summary: [Key findings or research question in 1-2 sentences]
Content:
- Research Question: [what you're trying to understand]
- Source: [where information came from]
- Key Points: [main ideas and findings]
- Methodology: [how research was conducted]
- Questions: [unanswered items or areas for further study]
- Conclusions: [what you've learned]
- Next Steps: [what to research next]
- References: [sources and citations]
```

**Example Usage**:

```
User: "I need to research the best practices for API design"
Assistant: Use create_note_enhanced with:
- Title: "API Design Best Practices Research"
- Category: Learning
- Status: Draft
- Importance: High
- Tags: research, api-design, best-practices, development
- Summary: "Researching industry standards and best practices for designing RESTful APIs"
```

### Template 4: Daily/Personal Notes

**Use when**: User mentions daily activities, personal thoughts, or life events
**Tool**: `create_note_enhanced`
**Suggested Structure**:

```
Title: [Date] - [Main Activity/Thought]
Category: Personal
Status: Draft
Importance: [High/Medium/Low]
Tags: daily, [activity type], [mood], [location]
Summary: [Brief description of the day or thought in 1-2 sentences]
Content:
- Date: [specific date and time]
- Location: [where this happened]
- Activities: [what you did]
- Thoughts: [reflections and observations]
- Feelings: [emotional state and reactions]
- Insights: [what you learned about yourself]
- Gratitude: [things you're thankful for]
- Tomorrow: [plans or intentions for next day]
```

## 🔍 Search Strategies

### Basic Search:

- **Simple queries**: Use `search_notes_enhanced` with just the query parameter
- **Broad searches**: Start with general terms, then refine
- **Content focus**: Search for specific concepts or keywords

### Advanced Filtering:

- **By importance**: Filter high-priority notes for urgent matters
- **By status**: Find incomplete tasks or completed work
- **By category**: Organize by work, personal, or learning context
- **By tags**: Use specific tags for precise filtering
- **Combined filters**: Use multiple criteria for targeted results

### Search Examples:

```
User: "Find all my high-priority work notes"
Assistant: Use search_notes_enhanced with:
- query: "" (empty for all notes)
- importance: "High"
- category: "Work"
- limit: 20

User: "Search for notes about Python programming"
Assistant: Use search_notes_enhanced with:
- query: "Python programming"
- category: "Learning"
- limit: 15
```

## 📝 Content Creation Best Practices

### Writing Guidelines:

1. **Be specific**: Use clear, descriptive titles and summaries
2. **Stay organized**: Use consistent formatting and structure
3. **Tag wisely**: Use relevant, searchable tags
4. **Update regularly**: Keep status and progress current
5. **Link related notes**: Reference other relevant notes when possible

### Property Usage:

1. **Importance**: Reserve "High" for truly critical information
2. **Status**: Update as work progresses
3. **Category**: Choose the most specific category available
4. **Tags**: Use consistent naming conventions
5. **Summary**: Write concise overviews that help with quick scanning

## 📐 Layout & Markdown Structure

### 🎨 Visual Hierarchy Principles:

1. **Use clear headings** to organize information hierarchically
2. **Group related content** with consistent spacing and formatting
3. **Highlight important information** using bold, italics, and lists
4. **Maintain consistent indentation** for better readability
5. **Use visual separators** to break up long sections

### 📋 Markdown Formatting Guide:

#### Headers (Use for main sections):

```markdown
# Main Title (H1)

## Section Header (H2)

### Subsection (H3)

#### Detail Section (H4)
```

#### Text Emphasis:

```markdown
**Bold text** - for important points, key terms, or emphasis
_Italic text_ - for definitions, foreign words, or subtle emphasis
**_Bold and italic_** - for critical information that needs maximum attention
`Code or technical terms` - for programming concepts, commands, or technical jargon
```

#### Lists (Use for organizing information):

```markdown
- Unordered list item
- Another item
  - Nested sub-item
  - Another sub-item
- Back to main level

1. Ordered list item
2. Second item
   1. Nested ordered item
   2. Another nested item
3. Back to main level
```

#### Code Blocks (For technical content):

````markdown
```python
# Python code example
def example_function():
    return "This is a code block"
```
````

```bash
# Command line example
npm install package-name
```

````

#### Links and References:
```markdown
[Link text](URL) - for external references
[[Note Title]] - for internal note references (if supported)
[#tag] - for tagging within content
````

#### Tables (For structured data):

```markdown
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### 🏗️ Layout Templates by Note Type:

#### Meeting Notes Layout:

```markdown
# [Meeting Topic] - [Date]

## 📅 Meeting Details

- **Date**: [Date and Time]
- **Duration**: [Length of meeting]
- **Location**: [Physical/Virtual location]
- **Attendees**: [List of participants]

## 🎯 Agenda

1. [First agenda item]
2. [Second agenda item]
3. [Third agenda item]

## 💬 Discussion Points

### [Topic 1]

- [Key point discussed]
- [Decision made]
- [Action required]

### [Topic 2]

- [Key point discussed]
- [Decision made]
- [Action required]

## ✅ Decisions Made

- [Decision 1 with context]
- [Decision 2 with context]

## 📋 Action Items

| Action     | Owner  | Deadline | Status |
| ---------- | ------ | -------- | ------ |
| [Action 1] | [Name] | [Date]   | [ ]    |
| [Action 2] | [Name] | [Date]   | [ ]    |

## 🔄 Next Steps

1. [Immediate next step]
2. [Follow-up action]
3. [Future consideration]

## 📝 Additional Notes

[Any other observations or context]
```

#### Project Notes Layout:

```markdown
# [Project Name]

## 🎯 Project Overview

- **Objective**: [Clear goal statement]
- **Scope**: [What's included/excluded]
- **Timeline**: [Start date - End date]
- **Budget**: [Financial constraints]

## 📋 Project Details

### Goals & Objectives

1. [Primary goal]
2. [Secondary goal]
3. [Success criteria]

### Scope

- **In Scope**:
  - [Feature 1]
  - [Feature 2]
- **Out of Scope**:
  - [Feature 3]
  - [Feature 4]

## 📅 Timeline & Milestones

| Milestone     | Date   | Status | Notes   |
| ------------- | ------ | ------ | ------- |
| [Milestone 1] | [Date] | [ ]    | [Notes] |
| [Milestone 2] | [Date] | [ ]    | [Notes] |

## 🛠️ Resources

### Team Members

- [Role]: [Name] - [Responsibilities]

### Tools & Technology

- [Tool 1]: [Purpose]
- [Tool 2]: [Purpose]

### Budget Allocation

- [Category 1]: [Amount]
- [Category 2]: [Amount]

## 📊 Progress Tracking

### Current Status

- **Overall Progress**: [X]%
- **Current Phase**: [Phase name]
- **Next Milestone**: [Date]

### Achievements

- [Achievement 1]
- [Achievement 2]

### Challenges & Solutions

| Challenge     | Impact            | Solution   | Status                 |
| ------------- | ----------------- | ---------- | ---------------------- |
| [Challenge 1] | [High/Medium/Low] | [Solution] | [Resolved/In Progress] |

## 🔄 Next Steps

1. [Immediate action]
2. [Short-term goal]
3. [Long-term consideration]

## 📚 Related Documents

- [Document 1](link)
- [Document 2](link)
```

#### Research Notes Layout:

```markdown
# [Research Topic]

## 🔍 Research Question

[Clear statement of what you're trying to understand or investigate]

## 📚 Sources

### Primary Sources

- [Source 1]: [Brief description]
- [Source 2]: [Brief description]

### Secondary Sources

- [Source 3]: [Brief description]
- [Source 4]: [Brief description]

## 📝 Key Findings

### [Finding Category 1]

- [Finding 1.1]
- [Finding 1.2]

### [Finding Category 2]

- [Finding 2.1]
- [Finding 2.2]

## 🧪 Methodology

### Research Approach

- [Method 1]: [Description]
- [Method 2]: [Description]

### Data Collection

- [Data source 1]: [How collected]
- [Data source 2]: [How collected]

## ❓ Questions & Gaps

### Unanswered Questions

1. [Question 1]
2. [Question 2]

### Areas for Further Study

- [Area 1]: [Why it's important]
- [Area 2]: [Why it's important]

## 💡 Conclusions

[Summary of main insights and what you've learned]

## 🔮 Next Steps

1. [Immediate research action]
2. [Follow-up investigation]
3. [Future research direction]

## 📖 References

- [Reference 1](link)
- [Reference 2](link)
```

### 🎯 Layout Best Practices:

#### 1. **Consistent Structure**

- Use the same header hierarchy across similar note types
- Maintain consistent spacing between sections
- Apply uniform formatting for similar elements

#### 2. **Scannable Content**

- Use bullet points and numbered lists for easy reading
- Break long paragraphs into shorter sections
- Use bold text to highlight key information
- Include visual separators between major sections

#### 3. **Logical Flow**

- Start with overview information
- Progress from general to specific details
- Group related information together
- End with actionable next steps

#### 4. **Visual Balance**

- Don't overcrowd sections with too much information
- Use white space effectively
- Balance text-heavy sections with lists and tables
- Keep individual sections focused on one main topic

#### 5. **Accessibility**

- Use descriptive headers for screen readers
- Ensure sufficient contrast between text and background
- Keep line lengths reasonable (60-80 characters)
- Use consistent formatting patterns

### 🚨 Common Layout Mistakes:

#### ❌ **Avoid These:**

- **Wall of text**: Long paragraphs without breaks
- **Inconsistent formatting**: Mixing different styles randomly
- **Poor hierarchy**: Using wrong header levels
- **Over-nesting**: Too many nested list levels
- **Missing whitespace**: Cramped, hard-to-read content

#### ✅ **Do This Instead:**

- **Break up content**: Use headers, lists, and spacing
- **Maintain consistency**: Apply uniform formatting rules
- **Follow hierarchy**: Use headers in logical order (H1 → H2 → H3)
- **Limit nesting**: Keep lists to 2-3 levels maximum
- **Add breathing room**: Use proper spacing between sections

### 🔧 Layout Customization Tips:

#### For Different Note Types:

- **Meeting notes**: Focus on action items and decisions
- **Project notes**: Emphasize progress and milestones
- **Research notes**: Highlight findings and conclusions
- **Personal notes**: Use more flexible, journal-style formatting

#### For Different Audiences:

- **Personal use**: More casual, flexible formatting
- **Team sharing**: Structured, professional layout
- **Client presentation**: Clean, minimal design
- **Academic work**: Formal, citation-heavy format

---

## 🚨 Common Pitfalls & Solutions

### Problem: Notes become disorganized

**Solution**: Use consistent templates, regular status updates, and proper categorization

### Problem: Too many tags

**Solution**: Limit to 2-10 relevant tags, use consistent naming, avoid over-tagging

### Problem: Notes are too long

**Solution**: Break into multiple notes, use summaries effectively, focus on key points

### Problem: Hard to find specific notes

**Solution**: Use enhanced search with filters, maintain consistent tagging, write descriptive titles

### Problem: Templates are too rigid

**Solution**: Adapt templates to specific needs, create custom templates for unique use cases

## 🔄 Workflow Recommendations

### For New Users:

1. Start with basic note creation
2. Add enhanced properties gradually
3. Experiment with different templates
4. Develop consistent tagging habits

### For Power Users:

1. Create custom templates for common workflows
2. Use advanced search and filtering
3. Maintain regular note reviews and updates
4. Integrate with other productivity tools

### For Teams:

1. Establish shared tagging conventions
2. Use consistent templates across team
3. Regular note sharing and collaboration
4. Maintain clear ownership and responsibilities

## 📊 Performance Tips

### Efficient Note Creation:

- Use templates for common note types
- Batch similar notes together
- Pre-write content before creating notes
- Use keyboard shortcuts when possible

### Effective Searching:

- Start with broad searches, then narrow down
- Use filters to reduce result sets
- Save common search patterns
- Update tags regularly for better searchability

### Maintenance:

- Review and archive old notes monthly
- Update note status as work progresses
- Clean up unused tags periodically
- Backup important notes regularly

## 🎯 Success Metrics

### Quality Indicators:

- Notes are easy to find when needed
- Information is well-organized and accessible
- Templates are used consistently
- Tags are relevant and searchable

### Usage Patterns:

- Regular note creation and updates
- Effective use of search and filtering
- Consistent template usage
- Proper categorization and tagging

---

_This guide should be updated regularly based on user feedback and tool improvements. For questions or suggestions, refer to the development team._
