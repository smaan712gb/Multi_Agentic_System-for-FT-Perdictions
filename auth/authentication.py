import streamlit as st
from .database import Database
import time
from datetime import datetime, timedelta

class Authentication:
    def __init__(self):
        """Initialize the authentication system"""
        self.db = Database()
        
        # Initialize session state variables
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        if 'subscription' not in st.session_state:
            st.session_state.subscription = None
        
        # Check for existing session
        self.check_session()
    
    def check_session(self):
        """Check if there's an existing valid session"""
        if st.session_state.session_id:
            user_id = self.db.validate_session(st.session_state.session_id)
            if user_id:
                user = self.db.get_user(user_id)
                subscription = self.db.get_active_subscription(user_id)
                
                st.session_state.user = user
                st.session_state.authenticated = True
                st.session_state.subscription = subscription
                return True
            else:
                # Session is invalid or expired
                self.logout()
        
        return False
    
    def login_form(self):
        """Display login form and handle login"""
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False
                
                result = self.db.authenticate_user(username, password)
                
                if result["success"]:
                    user = self.db.get_user(result["user_id"])
                    subscription = self.db.get_active_subscription(result["user_id"])
                    
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.session_state.session_id = result["session_id"]
                    st.session_state.subscription = subscription
                    
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                    return True
                else:
                    st.error(result["message"])
                    return False
        
        return False
    
    def register_form(self):
        """Display registration form and handle registration"""
        st.subheader("Register")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if not username or not email or not password or not password_confirm:
                    st.error("Please fill in all fields")
                    return False
                
                if password != password_confirm:
                    st.error("Passwords do not match")
                    return False
                
                if len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                    return False
                
                result = self.db.create_user(username, email, password)
                
                if result["success"]:
                    st.success("Registration successful! You can now log in.")
                    return True
                else:
                    st.error(result["message"])
                    return False
        
        return False
    
    def logout(self):
        """Log out the current user"""
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.session_id = None
        st.session_state.subscription = None
    
    def display_auth_page(self):
        """Display the authentication page with login and registration forms"""
        st.title("Futures Market Analysis")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            self.login_form()
        
        with tab2:
            self.register_form()
    
    def check_subscription(self):
        """Check if the user has an active subscription"""
        if not st.session_state.authenticated:
            return False
        
        # Special case for admin user - always has an active subscription
        if st.session_state.user["username"] == "admin":
            # If admin doesn't have a subscription, create one
            if not st.session_state.subscription:
                user_id = st.session_state.user["id"]
                payment_id = f"admin_override_{int(time.time())}"
                result = self.db.create_subscription(user_id, "premium", payment_id)
                if result["success"]:
                    st.session_state.subscription = self.db.get_active_subscription(user_id)
            return True
        
        user_id = st.session_state.user["id"]
        subscription = self.db.get_active_subscription(user_id)
        st.session_state.subscription = subscription
        
        return subscription is not None
    
    def log_usage(self, symbol):
        """Log usage of the analysis tool"""
        if not st.session_state.authenticated or not st.session_state.subscription:
            return False
        
        user_id = st.session_state.user["id"]
        subscription_id = st.session_state.subscription["id"]
        
        updated_subscription = self.db.log_usage(user_id, subscription_id, symbol)
        st.session_state.subscription = updated_subscription
        
        return True
    
    def display_subscription_info(self):
        """Display subscription information"""
        if not st.session_state.authenticated:
            return
        
        user_id = st.session_state.user["id"]
        stats = self.db.get_usage_stats(user_id)
        
        if stats["has_subscription"]:
            plan_name = {
                "free_trial": "Free Trial",
                "basic": "Basic Plan ($100)",
                "premium": "Premium Plan ($500)"
            }.get(stats["plan_type"], stats["plan_type"])
            
            st.sidebar.markdown(f"### Subscription: {plan_name}")
            
            # Display progress bar for usage
            progress = stats["runs_used"] / stats["runs_allowed"]
            st.sidebar.progress(progress)
            
            st.sidebar.markdown(f"**Runs Used:** {stats['runs_used']} / {stats['runs_allowed']}")
            
            if stats["end_date"]:
                end_date = datetime.fromisoformat(stats["end_date"])
                days_left = (end_date - datetime.now()).days
                st.sidebar.markdown(f"**Days Remaining:** {max(0, days_left)}")
        else:
            st.sidebar.warning("No active subscription")
    
    def require_auth(self):
        """Require authentication to access the page"""
        if not st.session_state.authenticated:
            self.display_auth_page()
            return False
        
        return True
    
    def require_subscription(self):
        """Require an active subscription to access the page"""
        if not self.require_auth():
            return False
        
        if not self.check_subscription():
            st.warning("You don't have an active subscription. Please purchase a subscription to continue.")
            self.display_subscription_page()
            return False
        
        return True
    
    def display_subscription_page(self):
        """Display the subscription page with available plans"""
        st.subheader("Subscription Plans")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Basic Plan
            - **Price:** $100
            - **Runs:** 10 runs
            - **Features:** Full access to all analysis tools
            """)
            
            if st.button("Purchase Basic Plan"):
                self.handle_payment("basic")
        
        with col2:
            st.markdown("""
            ### Premium Plan
            - **Price:** $500
            - **Runs:** 100 runs
            - **Duration:** 30 days
            - **Features:** Full access to all analysis tools
            """)
            
            if st.button("Purchase Premium Plan"):
                self.handle_payment("premium")
    
    def handle_payment(self, plan_type):
        """Handle payment for subscription"""
        # In a real application, this would integrate with a payment gateway like Stripe
        # For this example, we'll simulate a successful payment
        
        st.info("Processing payment...")
        
        # Simulate payment processing delay
        time.sleep(2)
        
        # Create subscription
        user_id = st.session_state.user["id"]
        payment_id = f"sim_{int(time.time())}"  # Simulated payment ID
        
        result = self.db.create_subscription(user_id, plan_type, payment_id)
        
        if result["success"]:
            subscription = self.db.get_active_subscription(user_id)
            st.session_state.subscription = subscription
            
            st.success(f"Payment successful! Your {plan_type} plan is now active.")
            time.sleep(2)
            st.rerun()
        else:
            st.error(result["message"])
