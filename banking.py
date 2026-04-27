"""
Handles all banking operations using dummy data from dummy_data.json.
"""

import json
import os

# ── Load dummy data ───────────────────────────────────────────────────────────
_DATA_FILE = os.path.join(os.path.dirname(__file__), "dummy_data.json")


def _load_data() -> dict:
    try:
        with open(_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError("Dummy data file not found.")
    except json.JSONDecodeError:
        raise RuntimeError("Dummy data file is corrupted or invalid.")


# Save updated data
def _save_data(data: dict):
    with open(_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Balance Inquiry ───────────────────────────────────────────────────────────

def get_balance() -> str:
    data = _load_data()
    acc = data["accounts"]["user_001"]

    return (
        f"Hello {acc['name']}. "
        f"Your current account balance is "
        f"{acc['balance']:,.2f} {acc['currency']}. "
        f"Account type: {acc['account_type']}."
    )


# ── Transaction History ───────────────────────────────────────────────────────

def get_transaction_history() -> str:
    data = _load_data()
    txns = data["recent_transactions"]

    lines = ["Here are your last 3 transactions: "]

    for i, t in enumerate(txns[:3], start=1):
        direction = "credited" if t["type"] == "credit" else "debited"
        lines.append(
            f"Transaction {i}: {t['description']} on {t['date']}, "
            f"amount {abs(t['amount']):,.2f} INR {direction}."
        )

    return " ".join(lines)


# ── Amount Parser ─────────────────────────────────────────────────────────────

def _parse_amount(amount_text: str):
    digits_only = "".join(filter(lambda c: c.isdigit() or c == ".", amount_text))

    if digits_only:
        try:
            return float(digits_only)
        except:
            pass

    try:
        from word2number import w2n
        return float(w2n.word_to_num(amount_text))
    except:
        return None


# ── Money Transfer Workflow ───────────────────────────────────────────────────

def start_transfer(speak, listen) -> None:

    speak("Starting money transfer. I will ask you a few questions.")

    # Step 1 — Beneficiary
    speak("Please say the full name of the beneficiary.")
    beneficiary = ""
    for _ in range(3):
        beneficiary = listen()
        if beneficiary:
            break
        speak("I didn't catch the name. Please say it again.")
    if not beneficiary:
        speak("Unable to get beneficiary name. Transfer cancelled.")
        return

    # Step 2 — Bank
    speak(f"Which bank does {beneficiary} have an account at?")
    bank = ""
    for _ in range(3):
        bank = listen()
        if bank:
            break
        speak("Please say the bank name again.")
    if not bank:
        speak("Unable to get bank name. Transfer cancelled.")
        return

    # Step 3 — Account number
    speak("Please say the account number. I will mask it for your security.")
    raw_account = ""
    for _ in range(3):
        raw_account = listen()
        if raw_account:
            break
        speak("Please say the account number again.")
    if not raw_account:
        speak("Unable to get account number. Transfer cancelled.")
        return

    digits = "".join(filter(str.isdigit, raw_account))
    masked = "XXXX-XXXX-" + (digits[-4:] if len(digits) >= 4 else "XXXX")

    # Step 4 — Amount
    speak("How much would you like to transfer in INR?")
    amount_text = ""
    amount_value = None

    for _ in range(3):
        amount_text = listen()
        if amount_text:
            amount_value = _parse_amount(amount_text)
            if amount_value is not None:
                break
        speak("Please say the amount clearly, for example five hundred.")

    if amount_value is None:
        speak("Unable to understand the amount. Transfer cancelled.")
        return

    # 🔥 Load current balance
    data = _load_data()
    acc = data["accounts"]["user_001"]
    current_balance = acc["balance"]

    # 🔥 Prevent overdraft
    if amount_value > current_balance:
        speak(
            f"Insufficient balance. Your current balance is "
            f"{current_balance:.2f} INR. Transfer cancelled."
        )
        return

    # Step 5 — Confirmation
    speak(
        f"Please confirm the transfer details. "
        f"Beneficiary: {beneficiary}. "
        f"Bank: {bank}. "
        f"Account ending: {masked}. "
        f"Amount: {amount_value:.2f} INR. "
        f"Say yes to confirm or no to cancel."
    )

    from voice_engine import listen_for_confirmation
    confirmed = listen_for_confirmation()

    if confirmed:
        # Deduct balance
        acc["balance"] -= amount_value

        # Add transaction history
        data["recent_transactions"].insert(0, {
            "date": "2025-04-27",
            "description": f"Transfer to {beneficiary}",
            "amount": -amount_value,
            "type": "debit"
        })

        # save updated data
        _save_data(data)

        speak(
            f"Transfer of {amount_value:.2f} INR to {beneficiary} at {bank} "
            f"has been processed successfully. "
            f"Your updated balance is {acc['balance']:.2f} INR. "
            f"Your reference number is TXN-2025-00417. "
            f"Is there anything else I can help you with?"
        )

    else:
        speak("Transfer has been cancelled. No money was moved.")