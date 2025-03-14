# Futures Market Analysis - Production Deployment Guide

This guide provides instructions for deploying the Futures Market Analysis application to production with user authentication and subscription features.

## Features

- **User Authentication**: Registration and login system
- **Subscription Plans**:
  - 3-day free trial for new users
  - Basic Plan: $100 for 10 runs
  - Premium Plan: $500 for 100 runs per month
- **Usage Tracking**: Monitors and limits usage based on subscription
- **Payment Processing**: Simulated payment system (can be replaced with Stripe or another payment processor)

## Prerequisites

- Python 3.8+
- Virtual environment (qaidi804ft_env)
- All dependencies installed (see requirements.txt)
- API keys for DeepSeek, Gemini, Groq, and Alpha Vantage

## Deployment Steps

### 1. Set Up the Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd <repository-directory>

# Create and activate virtual environment
python -m venv qaidi804ft_env

# On Windows
.\qaidi804ft_env\Scripts\activate

# On macOS/Linux
source qaidi804ft_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the `agents` directory with your API keys:

```
DEEPSEEK_API_KEY=your_deepseek_api_key
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

Alternatively, run the update_api_keys.py script:

```bash
python update_api_keys.py
```

### 3. Set Up the Database

The application uses SQLite for storing user data, subscriptions, and usage information. The database will be automatically created when the application is first run.

### 4. Configure Payment Processing

The current implementation uses a simulated payment system. For production, you should integrate with a real payment processor like Stripe.

To integrate with Stripe:

1. Sign up for a Stripe account at https://stripe.com
2. Get your API keys from the Stripe dashboard
3. Install the Stripe Python library: `pip install stripe`
4. Update the `auth/payment.py` file to use the Stripe API instead of the simulated payment system

### 5. Run the Production Application

#### On Windows

```bash
.\run_streamlit_prod.bat
```

#### On macOS/Linux

```bash
# Make the script executable
chmod +x run_streamlit_prod.sh

# Run the script
./run_streamlit_prod.sh
```

The application will be available at http://localhost:8501 by default.

### 6. Deploy to a Server (Optional)

For a production deployment, you should host the application on a server. Here are some options:

#### Option 1: Deploy on a VPS (e.g., AWS EC2, DigitalOcean)

1. Set up a VPS with Ubuntu or another Linux distribution
2. Install Python and other dependencies
3. Clone your repository to the server
4. Set up a virtual environment and install dependencies
5. Use a process manager like Supervisor to keep the application running
6. Set up Nginx as a reverse proxy to handle HTTPS

#### Option 2: Deploy with Docker

1. Create a Dockerfile for the application
2. Build a Docker image
3. Run the container on your server

#### Option 3: Deploy with Streamlit Sharing

1. Push your code to a GitHub repository
2. Sign up for Streamlit Sharing at https://streamlit.io/sharing
3. Connect your GitHub repository to Streamlit Sharing

## Security Considerations

### Password Storage

The current implementation uses SHA-256 for password hashing. For production, consider using a more secure hashing algorithm like bcrypt or Argon2.

To implement bcrypt:

1. Install the bcrypt library: `pip install bcrypt`
2. Update the `hash_password` method in `auth/database.py` to use bcrypt

### HTTPS

When deploying to production, always use HTTPS to encrypt data in transit. You can use Let's Encrypt to get free SSL certificates.

### Environment Variables

Store sensitive information like API keys and database credentials as environment variables rather than hardcoding them in your application.

## Monitoring and Maintenance

### Logging

Implement logging to track errors and user activity. Python's built-in logging module or a third-party solution like Sentry can be used.

### Backups

Regularly back up your database to prevent data loss. Set up automated backups to a secure location.

### Updates

Keep your dependencies up to date to ensure security and stability. Regularly check for updates to the libraries you use.

## Customization

### Branding

Update the application's title, logo, and color scheme to match your brand.

### Additional Features

Consider adding these features for a more complete product:

- Email verification for new users
- Password reset functionality
- Admin dashboard for managing users and subscriptions
- Analytics dashboard for tracking usage and revenue
- Automated emails for subscription expiration and renewal

## Troubleshooting

### Database Issues

If you encounter database issues, you can reset the database by deleting the `auth/users.db` file. A new database will be created when the application is restarted.

### Payment Processing

If payment processing is not working, check your payment processor configuration and API keys.

### API Rate Limits

Be aware of rate limits for the external APIs you're using (DeepSeek, Gemini, Groq, Alpha Vantage). Implement rate limiting in your application to avoid exceeding these limits.
