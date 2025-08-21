# 🚀 Admin User Setup with Phone Number Authentication

This guide will help you create an admin user for your Personal Assistant application using your phone number for authentication.

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Database running**: Your PostgreSQL database should be running and accessible
2. **Environment variables set**: Make sure your `.env` file has the correct database connection string
3. **Python dependencies installed**: Run `pip install -r requirements.txt` if you haven't already

## 🔧 Step 1: Database Migration

First, we need to add a `phone_number` field to the users table. Run this script:

```bash
python add_phone_number_field.py
```

This script will:

- Check if the `phone_number` field already exists
- Add the field if it doesn't exist
- Create an index for better performance

**Expected output:**

```
🚀 Personal Assistant - Database Migration
========================================
✅ Database connection successful
🔍 Checking if phone_number field exists in users table...
🔧 Adding phone_number field to users table...
✅ phone_number field added successfully
✅ Index created for phone number lookups

🎯 Database migration completed successfully!
You can now run the create_admin_user.py script to create your admin user.
```

## 👤 Step 2: Create Admin User

Now create your admin user with your phone number:

```bash
python create_admin_user.py \
  --phone "+1234567890" \
  --email "your@email.com" \
  --name "Your Full Name" \
  --password "SecurePass123!"
```

**Replace the values with your actual information:**

- `--phone`: Your phone number (with country code, e.g., +1 for US)
- `--email`: Your email address
- `--name`: Your full name
- `--password`: A strong password (at least 8 characters)

**Expected output:**

```
🚀 Personal Assistant - Admin User Creation
==================================================
📱 Phone: +1234567890
📧 Email: your@email.com
👤 Name: Your Full Name
🔒 Password: ************

✅ Database connection successful
🔍 Checking if user with phone +1234567890 already exists...
✅ No existing user found, proceeding with creation...
✅ Admin user created with ID: 1
🔧 Creating administrator role...
✅ Administrator role created with ID: 1
✅ Admin role assigned to user
🔧 Creating permission: user:read
✅ Permission user:read created
✅ Permission user:read assigned to admin role
...
✅ Basic permissions created and assigned

🎉 Admin user created successfully!
   ID: 1
   Name: Your Full Name
   Email: your@email.com
   Phone: +1234567890
   Role: administrator
   Status: Active and Verified

🎯 Next steps:
1. You can now log in using your phone number or email
2. Use the FastAPI app or CLI to access the system
3. Your admin role gives you full system access
```

## 🔐 Step 3: Authentication Options

Your admin user can now authenticate using either:

1. **Phone Number**: Use your phone number as the username
2. **Email**: Use your email address as the username
3. **Password**: Use the password you specified

## 🚀 Step 4: Access the Application

### Option 1: FastAPI Web Interface

If you have the FastAPI server running:

```bash
python src/apps/fastapi_app/main.py
```

Then visit: `http://localhost:8000/docs` to access the API documentation and test endpoints.

### Option 2: CLI Commands

Use the CLI to interact with the system:

```bash
python src/apps/cli/commands.py status
```

### Option 3: Direct Database Access

You can also verify your user was created by checking the database directly.

## 🔒 Security Features

Your admin user comes with:

- **Strong Password**: Bcrypt hashing with 12 salt rounds
- **RBAC System**: Administrator role with full system permissions
- **Phone Verification**: Phone number stored for authentication
- **Account Status**: Active and verified by default
- **Audit Logging**: All actions are logged for security

## 🛠️ Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Check your `.env` file has the correct `DATABASE_URL`
2. Ensure PostgreSQL is running
3. Verify the database exists and is accessible

### Permission Errors

If you get permission errors:

1. Make sure you're running the scripts from the project root
2. Check that all Python dependencies are installed
3. Verify the database user has CREATE/ALTER permissions

### User Already Exists

If you get "user already exists" errors:

1. The phone number or email is already in use
2. Use a different phone number or email
3. Or modify the script to update existing users

## 📱 Phone Number Format

Phone numbers should be in international format:

- ✅ `+1234567890` (US number)
- ✅ `+44123456789` (UK number)
- ✅ `+33123456789` (France number)
- ❌ `123-456-7890` (with dashes)
- ❌ `(123) 456-7890` (with parentheses)

The script will automatically clean the format for you.

## 🔄 Updating Existing Users

If you need to add phone numbers to existing users, you can modify the database directly:

```sql
UPDATE users
SET phone_number = '+1234567890'
WHERE email = 'existing@email.com';
```

## 📞 Support

If you encounter any issues:

1. Check the error messages in the script output
2. Verify your database connection and permissions
3. Ensure all required dependencies are installed
4. Check that the database schema is up to date

## 🎯 Next Steps

Once your admin user is created, you can:

1. **Test Authentication**: Try logging in with your credentials
2. **Explore the System**: Use the admin interface to manage users and settings
3. **Set Up Additional Users**: Create regular users for testing
4. **Configure MFA**: Set up two-factor authentication if needed
5. **Customize Permissions**: Modify the RBAC system as needed

---

**🎉 Congratulations!** You now have a fully functional admin user with phone number authentication for your Personal Assistant application.
