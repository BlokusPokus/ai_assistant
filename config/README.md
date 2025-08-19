# 📁 Configuration Guide

This folder contains all configuration files for the Personal Assistant application.

## 🗂️ File Structure

### Environment Files

- **`env.example`** - Template with all available configuration options
- **`development.env`** - Development environment configuration
- **`production.env`** - Production environment configuration
- **`test.env`** - Test environment configuration

### Tools & Documentation

- **`validate_config.py`** - Configuration validation script
- **`PRODUCTION_CHECKLIST.md`** - Production deployment checklist
- **`README.md`** - This file

## 🚀 Quick Start

1. **Copy the example file:**

   ```bash
   cp env.example .env
   ```

2. **Fill in your configuration values:**

   - Set `ENVIRONMENT` to your target environment
   - Configure required API keys
   - Set database connection strings

3. **Validate your configuration:**
   ```bash
   python config/validate_config.py
   ```

## 🔑 Required Configuration

### Core Settings

- `ENVIRONMENT` - Current environment (development/test/production)
- `DATABASE_URL` - Database connection string
- `GOOGLE_API_KEY` - Google API key for Gemini LLM functionality

### Application Settings

- `DEBUG` - Enable/disable debug mode
- `LOG_LEVEL` - Logging verbosity level
- `CONVERSATION_RESUME_WINDOW_MINUTES` - Minutes after which conversations are considered "old" (default: 30)

### Optional Integrations

- **Twilio** - For SMS notifications
- **YouTube API** - For YouTube data access
- **Qdrant** - For vector database operations
- **Microsoft Graph** - For email integration
- **Notion** - For knowledge management

## 🌍 Environment-Specific Configuration

### Development

- Debug mode enabled
- Verbose logging
- Local service endpoints
- Test API keys

### Production

- Debug mode disabled
- Production logging levels
- Production service endpoints
- Real API keys and credentials

### Test

- In-memory database
- Mock API keys
- Debug logging enabled

## 🔒 Security Best Practices

1. **Never commit real credentials to version control**
2. **Use environment variables for sensitive data**
3. **Rotate API keys regularly**
4. **Use minimal required permissions**
5. **Enable HTTPS in production**

## 📊 Configuration Validation

Run the validation script to check your configuration:

```bash
# From project root
python config/validate_config.py

# Or from config directory
cd config && python validate_config.py
```

The script will:

- ✅ Check required settings are configured
- ⚠️ Warn about optional settings
- ❌ Fail if critical settings are missing
- 🔍 Validate environment-specific configurations

## 🚀 Production Deployment

Before deploying to production:

1. **Review the production checklist:**

   - [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

2. **Validate configuration:**

   ```bash
   ENVIRONMENT=production python config/tests/validate_config.py
   ```

3. **Test all integrations:**
   - Database connectivity
   - External API connections
   - Notification services

## 🛠️ Troubleshooting

### Common Issues

**"Configuration validation FAILED"**

- Check that all required fields are set
- Ensure no placeholder values remain
- Verify environment file is being loaded

**"Environment variables not found"**

- Check file path in validation script
- Ensure .env file exists in correct location
- Verify ENVIRONMENT variable is set

**"API key validation failed"**

- Verify API keys are valid and active
- Check API key permissions and quotas
- Test API connections manually

### Getting Help

1. Check the validation script output for specific errors
2. Review the production checklist for missing items
3. Verify your environment file structure matches the examples
4. Test configuration loading in your application

## 📚 Additional Resources

- [Settings Module](../src/personal_assistant/config/settings.py) - Main configuration logic
- [Environment Examples](env.example) - Complete configuration template
- [Production Checklist](PRODUCTION_CHECKLIST.md) - Deployment guide

---

_For questions or issues, check the main project documentation or create an issue._
