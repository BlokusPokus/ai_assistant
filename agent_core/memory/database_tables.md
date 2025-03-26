-- 🧑 User & Authentication
CREATE TABLE users (
id SERIAL PRIMARY KEY,
email TEXT UNIQUE NOT NULL,
full_name TEXT,
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE auth_tokens (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
token TEXT NOT NULL,
expires_at TIMESTAMP,
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE user_settings (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
key TEXT NOT NULL,
value TEXT
);

-- 🧠 Agent Core Logs
CREATE TABLE agent_logs (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
user_input TEXT,
agent_response TEXT,
tool_called TEXT,
tool_output TEXT,
memory_used JSONB,
timestamp TIMESTAMP DEFAULT now()
);

-- 🗓️ Scheduling & Calendar
CREATE TABLE events (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
title TEXT,
description TEXT,
start_time TIMESTAMP,
end_time TIMESTAMP,
source TEXT DEFAULT 'assistant',
external_id TEXT
);

CREATE TABLE reminders (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
message TEXT NOT NULL,
remind_at TIMESTAMP NOT NULL,
created_at TIMESTAMP DEFAULT now(),
sent BOOLEAN DEFAULT FALSE
);

CREATE TABLE calendar_sync_log (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
synced_at TIMESTAMP DEFAULT now(),
sync_status TEXT
);

-- 💸 Expense Tracking
CREATE TABLE expense_categories (
id SERIAL PRIMARY KEY,
name TEXT NOT NULL
);

CREATE TABLE expenses (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
amount NUMERIC(10,2),
category_id INT REFERENCES expense_categories(id),
description TEXT,
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE budget_sync_log (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
synced_at TIMESTAMP DEFAULT now(),
sync_status TEXT
);

-- 🛒 Grocery Intelligence
CREATE TABLE grocery_deals (
id SERIAL PRIMARY KEY,
source TEXT,
title TEXT,
price TEXT,
image_url TEXT,
flyer_date DATE,
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE grocery_items (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
name TEXT,
quantity TEXT,
added_at TIMESTAMP DEFAULT now()
);

CREATE TABLE grocery_analysis (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
analysis JSONB,
created_at TIMESTAMP DEFAULT now()
);

-- 📔 Notes & Obsidian Sync
CREATE TABLE notes (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
title TEXT,
content TEXT,
created_at TIMESTAMP DEFAULT now(),
last_synced TIMESTAMP
);

CREATE TABLE note_sync_log (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
note_id INT REFERENCES notes(id),
synced_at TIMESTAMP DEFAULT now(),
sync_status TEXT
);

-- 🔔 Notifications
CREATE TABLE notifications (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
message TEXT,
channel TEXT, -- e.g., 'sms', 'email'
status TEXT DEFAULT 'pending',
scheduled_at TIMESTAMP,
sent_at TIMESTAMP
);

CREATE TABLE notification_templates (
id SERIAL PRIMARY KEY,
name TEXT UNIQUE,
content TEXT
);

-- ⚙️ Background Tasks
CREATE TABLE tasks (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
task_name TEXT,
status TEXT DEFAULT 'pending',
scheduled_at TIMESTAMP,
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE task_results (
id SERIAL PRIMARY KEY,
task_id INT REFERENCES tasks(id),
result JSONB,
completed_at TIMESTAMP
);

-- 🧠 Vector Memory (optional metadata)
CREATE TABLE memory_chunks (
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
content TEXT,
embedding VECTOR, -- replace with your vector type if using pgvector
created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE memory_metadata (
id SERIAL PRIMARY KEY,
chunk_id INT REFERENCES memory_chunks(id),
key TEXT,
value TEXT
);
