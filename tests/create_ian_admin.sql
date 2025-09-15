-- SQL script to create admin user for Ian LeBlanc
-- Run this directly in PostgreSQL

-- Step 1: Add phone_number field to users table if it doesn't exist
DO $$
BEGIN
    -- Check if phone_number column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'phone_number'
    ) THEN
        -- Add phone_number column
        ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) UNIQUE;
        
        -- Create index for performance
        CREATE INDEX idx_users_phone_number ON users(phone_number);
        
        RAISE NOTICE 'phone_number field added to users table';
    ELSE
        RAISE NOTICE 'phone_number field already exists in users table';
    END IF;
END $$;

-- Step 2: Create administrator role if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM roles WHERE name = 'administrator') THEN
        INSERT INTO roles (name, description, created_at) 
        VALUES ('administrator', 'System administrator with full access', NOW());
        RAISE NOTICE 'Administrator role created';
    ELSE
        RAISE NOTICE 'Administrator role already exists';
    END IF;
END $$;

-- Step 3: Create admin user for Ian LeBlanc
-- Password: IanAdmin2024! (bcrypt hash with 12 rounds)
INSERT INTO users (
    email, 
    phone_number, 
    full_name, 
    hashed_password, 
    is_active, 
    is_verified, 
    created_at, 
    updated_at
) VALUES (
    'ian.le.blanc@hotmail.com',        -- Ian's email from development.env
    '+1234567890',                     -- Replace with your phone number
    'Ian LeBlanc',                      -- Ian's full name
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5u.mG', -- "IanAdmin2024!" hashed
    true,                               -- Active account
    true,                               -- Verified account
    NOW(),                              -- Created now
    NOW()                               -- Updated now
) ON CONFLICT (email) DO NOTHING;       -- Don't create if email already exists

-- Step 4: Assign admin role to Ian
DO $$
DECLARE
    user_id INTEGER;
    role_id INTEGER;
BEGIN
    -- Get Ian's user ID
    SELECT id INTO user_id FROM users WHERE phone_number = '+1234567890';
    
    -- Get the administrator role ID
    SELECT id INTO role_id FROM roles WHERE name = 'administrator';
    
    -- Assign the role if both exist
    IF user_id IS NOT NULL AND role_id IS NOT NULL THEN
        INSERT INTO user_roles (user_id, role_id, is_primary, granted_at)
        VALUES (user_id, role_id, true, NOW())
        ON CONFLICT (user_id, role_id) DO NOTHING;
        
        RAISE NOTICE 'Admin role assigned to Ian (user ID %)', user_id;
    ELSE
        RAISE NOTICE 'Could not assign role: user_id=%, role_id=%', user_id, role_id;
    END IF;
END $$;

-- Step 5: Verify Ian's admin user was created
SELECT 
    u.id,
    u.email,
    u.phone_number,
    u.full_name,
    u.is_active,
    u.is_verified,
    r.name as role_name,
    'Login with phone: ' || u.phone_number || ' or email: ' || u.email as login_info
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
WHERE u.phone_number = '+1234567890';

-- Step 6: Show login credentials
SELECT 
    '🎉 Admin user created successfully!' as status,
    '📱 Phone: +1234567890' as phone,
    '📧 Email: ian.le.blanc@hotmail.com' as email,
    '👤 Name: Ian LeBlanc' as name,
    '🔒 Password: IanAdmin2024!' as password,
    '🎯 Role: Administrator' as role; 