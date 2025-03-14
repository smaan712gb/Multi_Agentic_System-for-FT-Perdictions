# Futures Market Analysis - Admin Dashboard

This admin dashboard provides tools for managing users, subscriptions, and monitoring usage of the Futures Market Analysis application.

## Features

- **Overview**: View key metrics and recent activity
- **User Management**: Add, delete, and manage users
- **Subscription Management**: Manage subscription plans and usage limits
- **Usage Analytics**: View usage statistics and trends

## Getting Started

### Running the Admin Dashboard

#### On Windows

```bash
.\run_admin_dashboard.bat
```

#### On macOS/Linux

```bash
# Make the script executable
chmod +x run_admin_dashboard.sh

# Run the script
./run_admin_dashboard.sh
```

The admin dashboard will be available at http://localhost:8501

### Login Credentials

Use the following credentials to log in to the admin dashboard:

- **Username**: admin
- **Password**: admin123

## Dashboard Sections

### Overview

The Overview section provides a high-level view of the application's usage and performance:

- Total users
- Active subscriptions
- Total runs
- Total revenue
- Subscription distribution
- Recent activity

### User Management

The User Management section allows you to:

- View all registered users
- Delete users
- Add free trials for users

### Subscription Management

The Subscription Management section allows you to:

- View all subscriptions
- Deactivate subscriptions
- Add runs to active subscriptions

### Usage Analytics

The Usage Analytics section provides detailed insights into how the application is being used:

- Usage by symbol
- Usage by plan type
- Usage over time
- Top users

## Security Considerations

In a production environment, you should:

1. Change the default admin credentials
2. Implement proper authentication with secure password storage
3. Add role-based access control for different admin levels
4. Enable HTTPS to encrypt data in transit

## Customization

You can customize the admin dashboard by:

1. Adding more analytics and reports
2. Implementing additional management features
3. Customizing the UI to match your brand
4. Adding email notifications for important events

## Troubleshooting

If you encounter issues with the admin dashboard:

1. Check that the database file exists and is accessible
2. Verify that you're using the correct admin credentials
3. Check the Streamlit logs for error messages
4. Restart the admin dashboard if needed
