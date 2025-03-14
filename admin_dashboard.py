import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import time

from auth.database import Database

# Set page config
st.set_page_config(
    page_title="Admin Dashboard - FuturesInsight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply dark theme
st.markdown("""
<style>
    .reportview-container {
        background-color: #0e1117;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #0e1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1a3a5f;
        border-radius: 4px 4px 0 0;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
        margin-right: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0077b6;
    }
    .stButton>button {
        background-color: #0077b6;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00b4d8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
db = Database()

# Admin authentication
def admin_login():
    """Simple admin login form"""
    st.title("Admin Dashboard")
    st.subheader("Login")
    
    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # In a real application, you would check against admin credentials in the database
            # For this example, we'll use a hardcoded admin user
            # Make sure to use the exact credentials: admin/admin123
            if username.strip() == "admin" and password.strip() == "admin123":
                st.session_state.admin_authenticated = True
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password")

# Initialize session state
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Main app
def main():
    """Main admin dashboard function"""
    st.title("Admin Dashboard - FuturesInsight AI")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Overview", "Users", "Subscriptions", "Usage Analytics"])
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Display selected page
    if page == "Overview":
        display_overview()
    elif page == "Users":
        display_users()
    elif page == "Subscriptions":
        display_subscriptions()
    elif page == "Usage Analytics":
        display_usage_analytics()

def display_overview():
    """Display overview dashboard"""
    st.header("Overview")
    
    # Get data from database
    conn = db.conn
    cursor = conn.cursor()
    
    # Get user count
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    # Get active subscriptions count
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE active = 1")
    active_subscriptions = cursor.fetchone()[0]
    
    # Get total runs
    cursor.execute("SELECT SUM(runs_used) FROM subscriptions")
    total_runs = cursor.fetchone()[0] or 0
    
    # Get revenue (simulated)
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE plan_type = 'basic'")
    basic_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE plan_type = 'premium'")
    premium_count = cursor.fetchone()[0]
    
    revenue = basic_count * 100 + premium_count * 500
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_count)
    
    with col2:
        st.metric("Active Subscriptions", active_subscriptions)
    
    with col3:
        st.metric("Total Runs", total_runs)
    
    with col4:
        st.metric("Total Revenue", f"${revenue}")
    
    # Display charts
    st.subheader("Subscription Distribution")
    
    # Get subscription data
    cursor.execute("SELECT plan_type, COUNT(*) FROM subscriptions GROUP BY plan_type")
    subscription_data = cursor.fetchall()
    
    if subscription_data:
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = [row[0] for row in subscription_data]
        sizes = [row[1] for row in subscription_data]
        colors = ['#0077b6', '#00b4d8', '#90e0ef']
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')
        
        st.pyplot(fig)
    else:
        st.info("No subscription data available")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    cursor.execute("""
    SELECT u.username, s.plan_type, l.timestamp, l.symbol
    FROM usage_logs l
    JOIN users u ON l.user_id = u.id
    JOIN subscriptions s ON l.subscription_id = s.id
    ORDER BY l.timestamp DESC
    LIMIT 10
    """)
    
    recent_activity = cursor.fetchall()
    
    if recent_activity:
        activity_data = []
        for row in recent_activity:
            activity_data.append({
                "Username": row[0],
                "Plan": row[1],
                "Timestamp": datetime.fromisoformat(row[2]).strftime("%Y-%m-%d %H:%M:%S"),
                "Symbol": row[3]
            })
        
        st.table(pd.DataFrame(activity_data))
    else:
        st.info("No recent activity")

def display_users():
    """Display user management page"""
    st.header("User Management")
    
    # Get users from database
    conn = db.conn
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT u.id, u.username, u.email, u.created_at, u.last_login,
           (SELECT COUNT(*) FROM subscriptions s WHERE s.user_id = u.id AND s.active = 1) as has_active_sub
    FROM users u
    ORDER BY u.created_at DESC
    """)
    
    users = cursor.fetchall()
    
    if users:
        user_data = []
        for row in users:
            created_at = datetime.fromisoformat(row[3]).strftime("%Y-%m-%d")
            last_login = row[4]
            if last_login:
                last_login = datetime.fromisoformat(last_login).strftime("%Y-%m-%d")
            else:
                last_login = "Never"
            
            user_data.append({
                "ID": row[0],
                "Username": row[1],
                "Email": row[2],
                "Created": created_at,
                "Last Login": last_login,
                "Active Subscription": "Yes" if row[5] > 0 else "No"
            })
        
        # Display user table
        st.dataframe(pd.DataFrame(user_data))
        
        # User actions
        st.subheader("User Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Delete user
            st.subheader("Delete User")
            user_options = [f"{u[1]} ({u[2]})" for u in users]
            selected_user = st.selectbox("Select User", user_options, key="delete_user")
            # Find the index of the selected user
            selected_index = user_options.index(selected_user)
            selected_user_id = users[selected_index][0]
            
            if st.button("Delete User"):
                # In a real application, you would want to confirm this action
                cursor.execute("DELETE FROM sessions WHERE user_id = ?", (selected_user_id,))
                cursor.execute("DELETE FROM usage_logs WHERE user_id = ?", (selected_user_id,))
                cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (selected_user_id,))
                cursor.execute("DELETE FROM users WHERE id = ?", (selected_user_id,))
                conn.commit()
                
                st.success("User deleted successfully!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            # Add free trial
            st.subheader("Add Free Trial")
            user_options = [f"{u[1]} ({u[2]})" for u in users]
            selected_user = st.selectbox("Select User", user_options, key="add_trial")
            # Find the index of the selected user
            selected_index = user_options.index(selected_user)
            selected_user_id = users[selected_index][0]
            
            if st.button("Add Free Trial"):
                # Deactivate existing subscriptions
                cursor.execute("UPDATE subscriptions SET active = 0 WHERE user_id = ?", (selected_user_id,))
                
                # Create new free trial
                subscription_id = db.create_free_trial(selected_user_id)
                
                st.success("Free trial added successfully!")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No users found")

def display_subscriptions():
    """Display subscription management page"""
    st.header("Subscription Management")
    
    # Get subscriptions from database
    conn = db.conn
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, u.username, s.plan_type, s.start_date, s.end_date, s.runs_allowed, s.runs_used, s.active
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    ORDER BY s.start_date DESC
    """)
    
    subscriptions = cursor.fetchall()
    
    if subscriptions:
        subscription_data = []
        for row in subscriptions:
            start_date = datetime.fromisoformat(row[3]).strftime("%Y-%m-%d")
            end_date = row[4]
            if end_date:
                end_date = datetime.fromisoformat(end_date).strftime("%Y-%m-%d")
            else:
                end_date = "No expiration"
            
            subscription_data.append({
                "ID": row[0],
                "Username": row[1],
                "Plan": row[2],
                "Start Date": start_date,
                "End Date": end_date,
                "Runs": f"{row[6]}/{row[5]}",
                "Status": "Active" if row[7] else "Inactive"
            })
        
        # Display subscription table
        st.dataframe(pd.DataFrame(subscription_data))
        
        # Subscription actions
        st.subheader("Subscription Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Deactivate subscription
            st.subheader("Deactivate Subscription")
            active_subs = [s for s in subscriptions if s[7]]
            if active_subs:
                sub_options = [f"{s[1]} - {s[2]} ({s[0]})" for s in active_subs]
                selected_sub = st.selectbox("Select Subscription", sub_options, key="deactivate_sub")
                # Find the index of the selected subscription
                selected_index = sub_options.index(selected_sub)
                selected_sub_id = active_subs[selected_index][0]
                
                if st.button("Deactivate"):
                    
                    cursor.execute("UPDATE subscriptions SET active = 0 WHERE id = ?", (selected_sub_id,))
                    conn.commit()
                    
                    st.success("Subscription deactivated successfully!")
                    time.sleep(1)
                    st.rerun()
        
        with col2:
            # Add runs to subscription
            st.subheader("Add Runs")
            active_subs = [s for s in subscriptions if s[7]]
            if active_subs:
                sub_options = [f"{s[1]} - {s[2]} ({s[0]})" for s in active_subs]
                selected_sub = st.selectbox("Select Subscription", sub_options, key="add_runs")
                # Find the index of the selected subscription
                selected_index = sub_options.index(selected_sub)
                selected_sub_id = active_subs[selected_index][0]
                
                runs_to_add = st.number_input("Runs to Add", min_value=1, max_value=100, value=10)
                
                if st.button("Add Runs"):
                    
                    cursor.execute("UPDATE subscriptions SET runs_allowed = runs_allowed + ? WHERE id = ?", 
                                  (runs_to_add, selected_sub_id))
                    conn.commit()
                    
                    st.success(f"Added {runs_to_add} runs to subscription!")
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("No subscriptions found")

def display_usage_analytics():
    """Display usage analytics page"""
    st.header("Usage Analytics")
    
    # Get usage data from database
    conn = db.conn
    cursor = conn.cursor()
    
    # Get usage by symbol
    cursor.execute("""
    SELECT symbol, COUNT(*) as count
    FROM usage_logs
    GROUP BY symbol
    ORDER BY count DESC
    """)
    
    symbol_usage = cursor.fetchall()
    
    if symbol_usage:
        st.subheader("Usage by Symbol")
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        symbols = [row[0] for row in symbol_usage]
        counts = [row[1] for row in symbol_usage]
        
        ax.bar(symbols, counts, color='#0077b6')
        ax.set_xlabel('Symbol')
        ax.set_ylabel('Number of Analyses')
        ax.set_title('Usage by Symbol')
        
        st.pyplot(fig)
    
    # Get usage by plan type
    cursor.execute("""
    SELECT s.plan_type, COUNT(*) as count
    FROM usage_logs l
    JOIN subscriptions s ON l.subscription_id = s.id
    GROUP BY s.plan_type
    ORDER BY count DESC
    """)
    
    plan_usage = cursor.fetchall()
    
    if plan_usage:
        st.subheader("Usage by Plan Type")
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        plans = [row[0] for row in plan_usage]
        counts = [row[1] for row in plan_usage]
        colors = ['#0077b6', '#00b4d8', '#90e0ef']
        
        ax.pie(counts, labels=plans, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')
        
        st.pyplot(fig)
    
    # Get usage over time
    cursor.execute("""
    SELECT DATE(timestamp) as date, COUNT(*) as count
    FROM usage_logs
    GROUP BY DATE(timestamp)
    ORDER BY date
    """)
    
    time_usage = cursor.fetchall()
    
    if time_usage:
        st.subheader("Usage Over Time")
        
        # Create line chart
        fig, ax = plt.subplots(figsize=(12, 6))
        dates = [row[0] for row in time_usage]
        counts = [row[1] for row in time_usage]
        
        ax.plot(dates, counts, marker='o', linestyle='-', color='#0077b6')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Analyses')
        ax.set_title('Usage Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
    
    # Top users
    cursor.execute("""
    SELECT u.username, COUNT(*) as count
    FROM usage_logs l
    JOIN users u ON l.user_id = u.id
    GROUP BY u.username
    ORDER BY count DESC
    LIMIT 10
    """)
    
    top_users = cursor.fetchall()
    
    if top_users:
        st.subheader("Top Users")
        
        user_data = []
        for row in top_users:
            user_data.append({
                "Username": row[0],
                "Analyses Run": row[1]
            })
        
        st.table(pd.DataFrame(user_data))

# Run the app
if not st.session_state.admin_authenticated:
    admin_login()
else:
    main()
