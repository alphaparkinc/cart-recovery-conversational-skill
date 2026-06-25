# Conversational Cart Recovery Skill

This repository contains the **Conversational Cart Recovery Skill** — a modular developer Python client SDK (`cart_recovery.py`), an agent skill configuration interface (`skill.json`), and executable dialogue tests. It is designed to engage visitors who abandon carts via SMS/WhatsApp or onsite chat, utilizing dynamic discount bidding to recover sales while protecting product profit margins.

---

## 🚀 Capabilities

* **Cart Margin Protection:** Calculates cart values and sets strict upper bounds for allowable discounts.
* **Conversational Negotiation Engine:** Simulates dialogue steps that slowly increase discounts (e.g. 5% -> 10% -> 15% Max) or pivot to non-discount incentives (e.g. Free Shipping) depending on abandon reasons.
* **Exit-Intent Dialog Recovery:** Generates copy templates optimized for casual onsite chat and SMS triggers.

---

## 🛠️ Setup & Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configuration:
   Set your API environment variables if executing requests against the live production server (otherwise, client executes in mock mode):
   * **PowerShell**:
     ```powershell
     $env:RECOVERY_API_KEY="your_api_key"
     ```
   * **bash**:
     ```bash
     export RECOVERY_API_KEY="your_api_key"
     ```

---

## 💻 SDK Usage Reference

```python
from cart_recovery import CartRecoveryClient

# Initialize Client (mock mode by default)
client = CartRecoveryClient()

# Calculate cart boundaries
analysis = client.analyze_cart([
    {"item_name": "Premium Leather Boot", "price": 120.00, "quantity": 1}
])
print(f"Max Discount: {analysis['max_allowed_discount']}%")

# Perform a dialogue step negotiation
step = client.get_negotiation_step(
    cart_total=analysis["cart_total"],
    abandon_reason="Price too high",
    dialog_history=[{"sender": "customer", "text": "Too expensive."}],
    current_state={
        "current_discount_percent": 0.0,
        "max_allowed_discount_percent": analysis["max_allowed_discount"],
        "status": "negotiating"
    }
)
print(step["bot_response"])
print(step["negotiation_state"])
```

---

## 📜 License
This project is licensed under the MIT License.
