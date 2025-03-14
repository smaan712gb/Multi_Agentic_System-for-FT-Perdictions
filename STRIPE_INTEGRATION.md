# Stripe Integration Guide for FutureInsight AI

This guide explains how to integrate Stripe payment processing into the FutureInsight AI application to enable real user payments.

## Overview of Stripe

Stripe is a popular payment processing platform that allows businesses to accept payments online. It provides a secure way to handle credit card information without having to store sensitive data on your own servers.

## Prerequisites

1. **Stripe Account**: Sign up for a Stripe account at [stripe.com](https://stripe.com)
2. **API Keys**: Once registered, obtain your API keys from the Stripe Dashboard
3. **Python Stripe Library**: The `stripe` Python package (already added to requirements.txt)

## Step 1: Set Up Stripe Account

1. Go to [stripe.com](https://stripe.com) and sign up for an account
2. Complete the verification process
3. Navigate to the Developers section in your Stripe Dashboard
4. Locate your API keys (you'll need both publishable and secret keys)

## Step 2: Store API Keys Securely

Never store your Stripe API keys directly in your code. Instead:

1. Create a `.env` file in the project root (if not already present)
2. Add your Stripe API keys to this file:

```
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
```

3. Make sure the `.env` file is included in your `.gitignore` to prevent it from being committed to version control

## Step 3: Update the Payment Processor

Replace the simulated payment system in `auth/payment.py` with the Stripe integration:

```python
import streamlit as st
import time
import uuid
from datetime import datetime, timedelta
import stripe
import os
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
            <script src="https://js.stripe.com/v3/"></script>
            <div id="card-element">
                <!-- Stripe Elements will create form elements here -->
            </div>
            <div id="card-errors" role="alert"></div>
            <script>
                const stripe = Stripe('{publishable_key}');
                const elements = stripe.elements();
                const cardElement = elements.create('card');
                cardElement.mount('#card-element');
            </script>
            """, unsafe_allow_html=True)
            
            # Since Streamlit doesn't support direct JavaScript integration,
            # we'll use a workaround for demonstration purposes
            st.text_input("Card Number", placeholder="4242 4242 4242 4242")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Expiration Date", placeholder="MM/YY")
            with col2:
                st.text_input("CVC", placeholder="123")
            
            st.text_input("Cardholder Name", placeholder="John Doe")
            
            # Terms and conditions
            st.checkbox("I agree to the terms and conditions", value=True)
            
            # Submit button
            submit = st.form_submit_button(f"Pay ${amount/100:.2f}")
            
            if submit:
                return self.process_payment(plan_type, amount)
        
        return False
    
    def process_payment(self, plan_type, amount):
        """Process a payment using Stripe"""
        try:
            # In a real implementation, you would create a payment intent
            # and confirm it with the card details from the form
            # For this example, we'll simulate a successful payment
            
            # Create a payment intent (in a real implementation)
            # payment_intent = stripe.PaymentIntent.create(
            #     amount=amount,
            #     currency="usd",
            #     description=f"FutureInsight AI - {plan_type.capitalize()} Plan",
            #     payment_method_types=["card"],
            # )
            
            # Display processing message
            with st.spinner("Processing payment..."):
                # Simulate payment processing delay
                time.sleep(2)
                
                # Generate a simulated payment ID
                # In a real implementation, this would come from Stripe
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
```

## Step 4: Implement Stripe Checkout (Alternative Approach)

For a more seamless integration, you can use Stripe Checkout, which provides a pre-built, hosted payment page:

```python
def create_checkout_session(plan_type):
    """Create a Stripe Checkout session"""
    if plan_type == "basic":
        price_id = "price_your_basic_plan_price_id"  # Create this in Stripe Dashboard
    elif plan_type == "premium":
        price_id = "price_your_premium_plan_price_id"  # Create this in Stripe Dashboard
    else:
        return None
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{YOUR_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{YOUR_DOMAIN}/cancel",
        )
        return checkout_session
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        return None
```

## Step 5: Handle Webhooks

To properly track payment status, set up Stripe webhooks:

1. Create a webhook endpoint in your application:

```python
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fulfill the purchase...
        fulfill_order(session)
    
    return "Success", 200
```

2. Register this webhook URL in your Stripe Dashboard

## Step 6: Update Requirements

Ensure the following packages are installed:

```
stripe>=5.0.0
python-dotenv>=1.0.0
```

## Step 7: Test the Integration

1. Use Stripe's test cards for testing:
   - Test successful payment: 4242 4242 4242 4242
   - Test payment requiring authentication: 4000 0025 0000 3155
   - Test declined payment: 4000 0000 0000 9995

2. Set your Stripe account to test mode during development

## Step 8: Go Live

When ready to accept real payments:

1. Complete Stripe's verification process
2. Switch from test to live API keys
3. Update your webhook endpoints
4. Test the entire payment flow with a real card (make a small test purchase)

## Security Considerations

1. **Never** store credit card information in your database
2. Always use HTTPS for your application
3. Keep your Stripe API keys secure and never expose them in client-side code
4. Regularly update your Stripe library to the latest version
5. Follow PCI compliance guidelines

## Troubleshooting

- Check Stripe Dashboard logs for detailed error information
- Use Stripe's webhook testing tools to simulate events
- Monitor your application logs for any Stripe-related errors

## Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Python API Reference](https://stripe.com/docs/api?lang=python)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
