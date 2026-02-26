
-- seed.sql (Placeholder for PostgreSQL Database Seed Data)

-- Insert a test user
INSERT INTO users (id, whatsapp_id, telegram_id) VALUES
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'whatsapp_user_123', 'telegram_user_456')
ON CONFLICT (id) DO NOTHING;

-- Insert a test conversation for the user on Telegram
INSERT INTO conversations (id, user_id, platform) VALUES
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'telegram')
ON CONFLICT (id) DO NOTHING;

-- Insert some messages for the conversation
INSERT INTO messages (conversation_id, sender, content) VALUES
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'user', 'Hi MAISU, how are you?'),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'maisu', 'I am doing great, how can I help you today?');
