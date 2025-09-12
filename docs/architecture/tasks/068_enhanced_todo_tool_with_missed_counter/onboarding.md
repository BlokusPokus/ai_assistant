# Onboarding: Enhanced Todo Tool with Missed Counter & Auto-Segmentation

## 🎯 **Context & Overview**

You are being onboarded to **Task 068: Enhanced Todo Tool with Missed Counter & Auto-Segmentation**. This task builds upon the existing todo list tool (Task 055) to add advanced behavioral tracking and intelligent task management features specifically designed for ADHD users.

### **What You're Building**

A sophisticated todo management system that:

- **Tracks missed deadlines** with a counter system
- **Automatically segments tasks** after 3 missed attempts
- **Provides behavioral analytics** and insights
- **Offers ADHD-specific features** for better productivity

### **Why This Matters**

ADHD users often struggle with:

- **Task overwhelm** when tasks become too complex
- **Repeated missed deadlines** without intervention
- **Lack of insights** into their productivity patterns
- **Difficulty breaking down** complex tasks

This system addresses these challenges through intelligent automation and behavioral analysis.

## 🏗️ **System Architecture Understanding**

### **Current State (Task 055 Foundation)**

The system already has:

- Basic todo CRUD operations
- Database models for tasks/todos
- Frontend components for todo management
- LLM integration for natural language processing

### **What We're Adding**

1. **Missed Counter System**

   - Track how many times each task is missed
   - Automatic threshold detection (3 missed attempts)
   - Behavioral pattern tracking

2. **Auto-Segmentation Engine**

   - LLM-powered task breakdown
   - Intelligent subtask creation
   - Dependency management

3. **Behavioral Analytics**

   - Completion pattern analysis
   - Productivity insights generation
   - Personalized recommendations

4. **Enhanced UI/UX**
   - Visual missed counter indicators
   - Segmentation management interface
   - Analytics dashboard

## 🔍 **Key Components to Understand**

### **1. Database Schema Enhancements**

```sql
-- New fields being added to todos table
ALTER TABLE todos ADD COLUMN missed_count INTEGER DEFAULT 0;
ALTER TABLE todos ADD COLUMN is_segmented BOOLEAN DEFAULT FALSE;
ALTER TABLE todos ADD COLUMN parent_task_id INTEGER REFERENCES todos(id);
ALTER TABLE todos ADD COLUMN segmentation_triggered_at TIMESTAMP;
ALTER TABLE todos ADD COLUMN completion_patterns JSONB;
ALTER TABLE todos ADD COLUMN user_insights JSONB;
```

### **2. Core Logic Flow**

```
User Creates Todo → System Tracks Deadlines → Missed Counter Increments →
Threshold Reached (3 misses) → Auto-Segmentation Triggered →
LLM Breaks Down Task → Subtasks Created → Analytics Updated
```

### **3. Key Classes & Functions**

- **`MissedCounterManager`**: Handles missed deadline tracking
- **`SegmentationEngine`**: Manages automatic task breakdown
- **`BehavioralAnalytics`**: Analyzes patterns and generates insights
- **`TodoTool`**: Enhanced main tool with new capabilities

## 🛠️ **Implementation Strategy**

### **Phase 1: Database & Missed Counter (Day 1)**

- Enhance database schema
- Implement missed counter logic
- Add threshold detection

### **Phase 2: Auto-Segmentation (Day 2)**

- Integrate LLM for task breakdown
- Create subtask management
- Handle task dependencies

### **Phase 3: Analytics (Day 3)**

- Build behavioral analysis algorithms
- Generate insights and recommendations
- Create analytics API endpoints

### **Phase 4: Frontend & Testing (Day 4)**

- Build UI components
- Integrate with existing frontend
- Comprehensive testing

## 📚 **Key Files to Study**

### **Existing Foundation (Task 055)**

- `src/personal_assistant/tools/todos/todo_tool.py`
- `src/personal_assistant/database/models/todos.py`
- `src/apps/fastapi_app/routes/todos.py`
- `src/apps/frontend/src/components/todos/`

### **New Files to Create**

- `src/personal_assistant/tools/todos/missed_counter.py`
- `src/personal_assistant/tools/todos/segmentation_engine.py`
- `src/personal_assistant/tools/todos/behavioral_analytics.py`
- `src/apps/fastapi_app/routes/analytics.py`

## 🎯 **Success Criteria**

### **Functional Requirements**

- [ ] Missed counter accurately tracks overdue tasks
- [ ] Auto-segmentation triggers after 3 missed attempts
- [ ] LLM generates meaningful task breakdowns
- [ ] Analytics provide actionable insights
- [ ] Frontend displays all new features clearly

### **Technical Requirements**

- [ ] Database schema enhanced with new fields
- [ ] API endpoints for all new functionality
- [ ] 95%+ test coverage
- [ ] Performance < 300ms for analytics queries
- [ ] Seamless integration with existing system

### **User Experience Requirements**

- [ ] ADHD-friendly design principles
- [ ] Clear visual indicators for missed tasks
- [ ] Intuitive segmentation management
- [ ] Actionable insights and recommendations
- [ ] Positive user feedback from testing

## 🚨 **Critical Considerations**

### **ADHD-Specific Design**

- **Positive Reinforcement**: Focus on encouragement, not punishment
- **Visual Clarity**: Clear indicators and progress tracking
- **Flexibility**: Allow users to adjust thresholds and settings
- **Gentle Reminders**: Soft notifications rather than harsh alerts

### **Performance Considerations**

- **Background Processing**: Heavy analytics should run asynchronously
- **Caching**: Cache frequently accessed behavioral data
- **Database Optimization**: Proper indexing for analytics queries
- **LLM Rate Limiting**: Manage API calls efficiently

### **Privacy & Security**

- **Data Encryption**: Encrypt sensitive behavioral data
- **User Control**: Allow users to opt-out of analytics
- **Data Retention**: Clear policies for behavioral data storage
- **Anonymization**: Anonymize data for pattern analysis

## 🔧 **Development Environment Setup**

### **Prerequisites**

- Python 3.11+ with virtual environment
- PostgreSQL database
- Redis for caching
- Node.js for frontend development
- Access to Gemini API

### **Database Setup**

```bash
# Run migration for new fields
alembic upgrade head

# Verify new fields exist
psql -d personal_assistant -c "\d todos"
```

### **Testing Strategy**

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **User Testing**: ADHD user feedback sessions
- **Performance Tests**: Load testing for analytics

## 📖 **Learning Resources**

### **ADHD & Productivity**

- Understanding ADHD task completion patterns
- Behavioral psychology for productivity tools
- Visual design principles for ADHD users

### **Technical References**

- LLM prompting best practices
- Behavioral analytics algorithms
- Database design for JSONB data
- React component patterns

### **Existing Codebase**

- Study Task 055 implementation
- Review existing tool patterns
- Understand database model structure
- Learn API endpoint patterns

## 🎯 **Next Steps**

1. **Study the existing todo tool implementation** (Task 055)
2. **Review the database schema** and understand current structure
3. **Examine the LLM integration patterns** used in other tools
4. **Plan the database migration** for new fields
5. **Design the missed counter logic** and threshold detection
6. **Create the auto-segmentation engine** with LLM integration
7. **Build the behavioral analytics** system
8. **Implement frontend components** for new features
9. **Test thoroughly** with ADHD users
10. **Document everything** for future maintenance

## ❓ **Questions to Consider**

- How can we make the missed counter feel supportive rather than punitive?
- What's the optimal number of subtasks for auto-segmentation?
- How detailed should the behavioral analytics be?
- What visual indicators work best for ADHD users?
- How can we ensure the system scales with user growth?

---

**Remember**: This is a complex feature that requires careful consideration of ADHD users' needs. Focus on creating a supportive, intelligent system that helps users succeed rather than just tracking their failures.

**Good luck with the implementation!** 🚀
