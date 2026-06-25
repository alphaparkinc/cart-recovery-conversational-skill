import os
import requests
from typing import List, Dict, Any, Optional

class CartRecoveryError(Exception):
    """Base exception class for Cart Recovery Client."""
    pass

class CartRecoveryClient:
    """
    Client for exit-intent session analysis and conversational recovery with dynamic discount bidding.
    Supports a mock mode for local testing.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.cart-recovery.ai/v1"):
        self.api_key = api_key or os.environ.get("RECOVERY_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.mock_mode = self.api_key is None or self.api_key == "mock"
        
        if self.mock_mode:
            print("[CartRecoveryClient] API Key not set. Running in MOCK Mode.")

    def analyze_cart(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate total value and determine target retention limits.
        """
        total = sum(i["price"] * i["quantity"] for i in items)
        
        # Protect margins: high value carts get lower maximum discounts to protect absolute margins,
        # but can get free premium shipping or gifts.
        if total > 200.00:
            max_discount = 10.0
            allowed_perks = ["free_shipping", "premium_packaging"]
        else:
            max_discount = 15.0
            allowed_perks = ["free_shipping"]
            
        return {
            "cart_total": round(total, 2),
            "max_allowed_discount": max_discount,
            "allowed_perks": allowed_perks
        }

    def get_negotiation_step(
        self,
        cart_total: float,
        abandon_reason: str,
        dialog_history: List[Dict[str, str]],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate customer dialog and decide on the next response and discount state.
        """
        if self.mock_mode:
            current_discount = current_state.get("current_discount_percent", 0.0)
            max_discount = current_state.get("max_allowed_discount_percent", 15.0)
            status = current_state.get("status", "negotiating")
            
            # Simple state machine negotiation simulation
            last_message = dialog_history[-1]["text"].lower() if dialog_history else ""
            
            # Acceptance keywords
            if any(k in last_message for k in ["ok", "deal", "fine", "yes", "accept", "buy"]):
                return {
                    "bot_response": "Awesome! I've updated your cart with the offer. You can complete your purchase using the link above.",
                    "negotiation_state": {
                        "current_discount_percent": current_discount,
                        "max_allowed_discount_percent": max_discount,
                        "status": "accepted"
                    }
                }
            
            # Rejection keywords
            if any(k in last_message for k in ["no", "never", "too expensive", "bye", "stop"]):
                status = "negotiating"
            
            # Negotiation ladder
            if current_discount == 0.0:
                if "shipping" in abandon_reason.lower() or "shipping" in last_message:
                    response = "I noticed you left because of shipping costs. What if I offer you Free Shipping on this order?"
                    next_discount = 0.0 # Free shipping perk instead
                else:
                    response = "We really want you to experience these items. Can I offer you a special 5% discount to help you get started?"
                    next_discount = 5.0
            elif current_discount == 5.0:
                response = "I completely understand. To make it easier, I can extend a one-time 10% discount on your entire order. How does that sound?"
                next_discount = 10.0
            elif current_discount < max_discount:
                response = f"I'd love to help you out. My absolute final offer is a {max_discount}% discount on the entire cart. We cannot go lower than this."
                next_discount = max_discount
            else:
                response = "I'm sorry, that is the best discount we can offer today. The cart link will remain active if you change your mind!"
                next_discount = max_discount
                status = "rejected"
                
            return {
                "bot_response": response,
                "negotiation_state": {
                    "current_discount_percent": next_discount,
                    "max_allowed_discount_percent": max_discount,
                    "status": status
                }
            }

        # Remote API integration call
        payload = {
            "cart_total": cart_total,
            "abandon_reason": abandon_reason,
            "dialog_history": dialog_history,
            "current_state": current_state
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            resp = requests.post(f"{self.base_url}/negotiate", json=payload, headers=headers, timeout=30)
            return resp.json()
        except Exception as e:
            raise CartRecoveryError(f"API Negotiation step failed: {e}")
