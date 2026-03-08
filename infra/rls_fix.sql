-- Run this in Supabase SQL Editor if /locations returns empty due to Row Level Security.
-- This disables RLS so the API can read without policies.

ALTER TABLE locations DISABLE ROW LEVEL SECURITY;
ALTER TABLE congestion_readings DISABLE ROW LEVEL SECURITY;
