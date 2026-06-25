import sys
from cart_recovery import CartRecoveryClient

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("=== Conversational Cart Recovery retention example ===")
    
    # Initialize client in mock mode
    client = CartRecoveryClient()
    
    cart_items = [
        {"item_name": "Premium Leather Boot", "price": 120.00, "quantity": 1},
        {"item_name": "Cedar Shoe Tree", "price": 25.00, "quantity": 2}
    ]
    
    # 1. Analyze cart metrics
    print("\n--- Step 1: Cart Metrics Analysis ---")
    analysis = client.analyze_cart(cart_items)
    print(f"Cart Total: ${analysis['cart_total']:.2f}")
    print(f"Max Allowed Discount: {analysis['max_allowed_discount']}%")
    print(f"Allowed Perks: {analysis['allowed_perks']}")

    # 2. Simulate conversational negotiation flow
    print("\n--- Step 2: Simulating Negotiation Dialogue ---")
    
    # Starting state
    state = {
        "current_discount_percent": 0.0,
        "max_allowed_discount_percent": analysis['max_allowed_discount'],
        "status": "negotiating"
    }
    
    dialogue = []
    
    # Scenario A: Customer complains about price, bot counters
    print("\n[User exits due to pricing]")
    abandon_reason = "Price too high"
    
    # Bot response 1
    dialogue.append({"sender": "customer", "text": "It's just too expensive for me right now."})
    step = client.get_negotiation_step(analysis['cart_total'], abandon_reason, dialogue, state)
    print(f"Bot: {step['bot_response']}")
    state = step['negotiation_state']
    dialogue.append({"sender": "bot", "text": step['bot_response']})
    
    # Customer response 2 (still hesitating)
    print("\n[Customer: Still a bit much. Can you do any better?]")
    dialogue.append({"sender": "customer", "text": "Still a bit much. Can you do any better?"})
    step = client.get_negotiation_step(analysis['cart_total'], abandon_reason, dialogue, state)
    print(f"Bot: {step['bot_response']}")
    state = step['negotiation_state']
    dialogue.append({"sender": "bot", "text": step['bot_response']})
    
    # Customer response 3 (Accepts deal)
    print("\n[Customer: Okay, that sounds like a deal!]")
    dialogue.append({"sender": "customer", "text": "Okay, that sounds like a deal!"})
    step = client.get_negotiation_step(analysis['cart_total'], abandon_reason, dialogue, state)
    print(f"Bot: {step['bot_response']}")
    state = step['negotiation_state']
    print(f"\nFinal Negotiation Status: {state['status'].upper()} (Applied Discount: {state['current_discount_percent']}%)")

if __name__ == "__main__":
    main()
