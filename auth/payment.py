import streamlit as st
import time
import uuid
from datetime import datetime, timedelta
import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")

class PaymentProcessor:
    def __init__(self, database):
        """Initialize the payment processor"""
        self.db = database
    
    def display_payment_form(self, plan_type):
        """Display a payment form for the selected plan"""
        st.subheader("Payment Information")
        
        # Get plan details
        if plan_type == "basic":
            amount = 10000  # $100.00 in cents
            description = "Basic Plan - 10 runs"
        elif plan_type == "premium":
            amount = 50000  # $500.00 in cents
            description = "Premium Plan - 100 runs (30 days)"
        else:
            st.error("Invalid plan type")
            return False
        
        # Display payment form
        with st.form(f"payment_form_{plan_type}"):
            st.markdown(f"### {description}")
            st.markdown(f"**Amount:** ${amount/100:.2f}")
            
            # Credit card information
            st.markdown("### Card Information")
            st.markdown(f"""
            <div style="padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 20px;">
                <p>Using Stripe Test Mode - Use these test cards:</p>
                <ul>
                    <li>Success: 4242 4242 4242 4242</li>
                    <li>Requires Authentication: 4000 0025 0000 3155</li>
                    <li>Declined: 4000 0000 0000 9995</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Since Streamlit doesn't support direct JavaScript integration,
            # we'll use a workaround for demonstration purposes
            card_number = st.text_input("Card Number", placeholder="4242 4242 4242 4242")
            
            col1, col2 = st.columns(2)
            with col1:
                exp_date = st.text_input("Expiration Date", placeholder="MM/YY")
            with col2:
                cvc = st.text_input("CVC", placeholder="123")
            
            cardholder_name = st.text_input("Cardholder Name", placeholder="John Doe")
            
            # Terms and conditions
            terms = st.checkbox("I agree to the terms and conditions", value=True)
            
            # Submit button
            submit = st.form_submit_button(f"Pay ${amount/100:.2f}")
            
            if submit:
                if not terms:
                    st.error("You must agree to the terms and conditions")
                    return False
                
                if not card_number or not exp_date or not cvc or not cardholder_name:
                    st.error("Please fill in all payment details")
                    return False
                
                # Basic validation
                if not card_number.replace(' ', '').isdigit() or len(card_number.replace(' ', '')) < 15:
                    st.error("Invalid card number")
                    return False
                
                return self.process_payment(plan_type, amount, card_number, exp_date, cvc, cardholder_name)
        
        return False
    
    def process_payment(self, plan_type, amount, card_number, exp_date, cvc, cardholder_name):
        """Process a payment using Stripe"""
        try:
            # Display processing message
            with st.spinner("Processing payment..."):
                # Parse expiration date
                try:
                    exp_month, exp_year = exp_date.split('/')
                    exp_month = int(exp_month.strip())
                    exp_year = int("20" + exp_year.strip()) if len(exp_year.strip()) == 2 else int(exp_year.strip())
                except:
                    st.error("Invalid expiration date format. Please use MM/YY")
                    return False
                
                # In a real implementation with proper Stripe Elements integration,
                # you would create a payment method and then a payment intent
                # For this example, we'll simulate the Stripe API call
                
                # Simulate Stripe API call based on test card number
                if card_number.startswith("4242"):
                    # Success case
                    payment_status = "succeeded"
                elif card_number.startswith("4000 0025"):
                    # Authentication required (would normally redirect to 3D Secure)
                    st.warning("This card requires authentication. In a real implementation, you would be redirected to complete 3D Secure authentication.")
                    payment_status = "requires_action"
                    # For demo purposes, we'll consider this a success
                    payment_status = "succeeded"
                elif card_number.startswith("4000 0000 0000 9995"):
                    # Declined card
                    st.error("Your card was declined. Please try another payment method.")
                    return False
                else:
                    # For demo purposes, assume success for other card numbers
                    payment_status = "succeeded"
                
                # Simulate payment processing delay
                time.sleep(2)
                
                if payment_status == "succeeded":
                    # Generate a simulated Stripe payment ID
                    payment_id = f"pi_{uuid.uuid4().hex[:8]}_{int(time.time())}"
                    
                    # Create subscription in database
                    if st.session_state.user:
                        user_id = st.session_state.user["id"]
                        result = self.db.create_subscription(user_id, plan_type, payment_id)
                        
                        if result["success"]:
                            # Update session state with new subscription
                            subscription = self.db.get_active_subscription(user_id)
                            st.session_state.subscription = subscription
                            
                            st.success(f"Payment successful! Your {plan_type} plan is now active.")
                            return True
                        else:
                            st.error(result["message"])
                            return False
                    else:
                        st.error("User not authenticated")
                        return False
                else:
                    st.error("Payment processing failed. Please try again.")
                    return False
        except Exception as e:
            st.error(f"Payment processing error: {str(e)}")
            return False
    
    def display_subscription_plans(self):
        """Display available subscription plans"""
        st.subheader("Subscription Plans")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Basic Plan
            - **Price:** $100
            - **Runs:** 10 runs
            - **Features:** Full access to all analysis tools
            """)
            
            if st.button("Select Basic Plan"):
                return self.display_payment_form("basic")
        
        with col2:
            st.markdown("""
            ### Premium Plan
            - **Price:** $500
            - **Runs:** 100 runs
            - **Duration:** 30 days
            - **Features:** Full access to all analysis tools
            """)
            
            if st.button("Select Premium Plan"):
                return self.display_payment_form("premium")
        
        return False
