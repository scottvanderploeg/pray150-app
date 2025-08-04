# Pray150 Authentication API Documentation

## Overview

The Pray150 application now includes REST API endpoints for user authentication using Supabase Auth and Flask-JWT-Extended.

## Authentication Endpoints

### POST /api/register
Register a new user with Supabase Authentication.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Success Response (201):**
```json
{
  "message": "User registered",
  "user_id": "3ed2fad9-9ad1-4c7c-ba42-d137afdd6283"
}
```

**Error Responses:**
- `400`: Missing email/password or password too short
- `409`: User already exists
- `500`: Registration failed

### POST /api/login
Login user and receive JWT access token.

**Request Body:**
```json
{
  "email": "user@example.com", 
  "password": "secure123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Responses:**
- `400`: Missing email/password
- `401`: Invalid credentials or email not confirmed
- `500`: Login failed

### GET /api/verify
Verify JWT token and get user information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "valid": true,
  "user_id": "3ed2fad9-9ad1-4c7c-ba42-d137afdd6283",
  "email": "user@example.com"
}
```

**Error Responses:**
- `401`: Invalid or expired token

### POST /api/forgot-password
Send password reset email via Supabase Auth.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

**Error Responses:**
- `400`: Missing email
- `500`: Password reset request failed

### POST /api/reset-password
Reset password using tokens from email link.

**Request Body:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "new_password": "newsecure123"
}
```

**Success Response (200):**
```json
{
  "message": "Password updated successfully"
}
```

**Error Responses:**
- `400`: Missing tokens/password or password too short
- `500`: Password reset failed

## Implementation Details

### Environment Variables
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key  
- `SUPABASE_JWT_SECRET`: Your Supabase JWT secret

### Technology Stack
- **Flask-JWT-Extended**: JWT token management
- **Supabase Auth**: User authentication and management
- **Flask**: Web framework and API endpoints

### Authentication Flow
1. User registers via `/api/register`
2. Supabase creates user account (may require email confirmation)
3. User logs in via `/api/login` 
4. Server returns JWT access token
5. Client includes token in `Authorization: Bearer <token>` header
6. Server validates token on protected endpoints

## Web Interface Routes

### GET /login
Display login form with "Forgot Password" link.

### GET /forgot-password  
Display forgot password form for email entry.

### GET /reset-password
Display password reset form (accessed via email link).

## Password Reset Flow

1. **User requests password reset:**
   - Visit `/forgot-password` or use API endpoint
   - Enter email address
   - System sends reset email via Supabase

2. **User receives email:**
   - Email contains reset link with tokens
   - Link redirects to `/reset-password` with tokens in URL hash

3. **User sets new password:**
   - Enter new password on reset form
   - JavaScript extracts tokens from URL
   - API call updates password via Supabase

## Current Status

✅ **Implemented:**
- Registration endpoint with Supabase Auth integration
- Login endpoint with JWT token generation  
- Token verification endpoint
- Password reset request endpoint
- Password reset completion endpoint
- Web interface for forgot/reset password flow
- Proper error handling and validation
- Integration with existing Flask application

⚠️  **Note about Email Confirmation:**
Supabase requires email confirmation for new users by default. Users must:
1. Register via `/api/register`
2. Check email and click confirmation link
3. Then login via `/api/login`

⚠️  **Note about Password Reset:**
Password reset emails are sent by Supabase and contain secure tokens for verification.

## Testing

Test users can be created with valid email addresses (Gmail, Yahoo, etc.) that can receive confirmation emails.

Example successful registration:
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser123@gmail.com", "password": "secure123"}'
```

After email confirmation, login:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser123@gmail.com", "password": "secure123"}'
```