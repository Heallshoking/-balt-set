-- AI Service Marketplace Database Schema
-- PostgreSQL Schema for MVP

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Masters table
CREATE TABLE masters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    specializations TEXT[] NOT NULL,
    service_zones JSONB,
    schedule JSONB,
    bank_details TEXT, -- encrypted
    tools TEXT[],
    rating DECIMAL(3, 2) DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255),
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    addresses JSONB,
    preferred_channel VARCHAR(20) CHECK (preferred_channel IN ('telegram', 'whatsapp', 'phone', 'web')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id),
    master_id UUID REFERENCES masters(id),
    category VARCHAR(50) NOT NULL CHECK (category IN ('electrical', 'plumbing', 'renovation', 'appliances')),
    client_description TEXT NOT NULL,
    ai_diagnosis TEXT,
    media_files TEXT[],
    address TEXT NOT NULL,
    location JSONB,
    scheduled_time TIMESTAMP,
    client_cost DECIMAL(10, 2) NOT NULL,
    master_earnings DECIMAL(10, 2) NOT NULL,
    platform_commission DECIMAL(10, 2) NOT NULL,
    instructions TEXT,
    required_materials JSONB,
    status VARCHAR(20) DEFAULT 'created' CHECK (status IN ('created', 'assigned', 'in_transit', 'in_progress', 'completed', 'paid', 'cancelled')),
    dialogue_history JSONB,
    status_history JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id),
    master_id UUID REFERENCES masters(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) CHECK (payment_method IN ('card', 'sbp', 'qr', 'cash', 'wallet')),
    gateway_transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'refunded')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Availability table for masters
CREATE TABLE master_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    master_id UUID REFERENCES masters(id),
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(master_id, date, start_time, end_time)
);

-- Conversation messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id),
    sender_type VARCHAR(10) CHECK (sender_type IN ('client', 'ai', 'master')),
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'voice', 'photo', 'video', 'document')),
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_masters_phone ON masters(phone);
CREATE INDEX idx_masters_status ON masters(status);
CREATE INDEX idx_masters_specializations ON masters USING GIN(specializations);

CREATE INDEX idx_clients_phone ON clients(phone);

CREATE INDEX idx_jobs_client_id ON jobs(client_id);
CREATE INDEX idx_jobs_master_id ON jobs(master_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_scheduled_time ON jobs(scheduled_time);

CREATE INDEX idx_transactions_job_id ON transactions(job_id);
CREATE INDEX idx_transactions_master_id ON transactions(master_id);
CREATE INDEX idx_transactions_status ON transactions(status);

CREATE INDEX idx_availability_master_date ON master_availability(master_id, date);

CREATE INDEX idx_messages_job_id ON messages(job_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_masters_updated_at BEFORE UPDATE ON masters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
