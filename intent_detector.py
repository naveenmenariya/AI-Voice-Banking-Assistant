"""
Improved intent detection with controlled matching.
Prevents wrong intent selection due to weak keyword overlap.
"""

import re

# ── Intent keyword map ─────────────────────────────────────────────

INTENT_MAP = {
    "balance": [
        "balance", "account balance", "my balance",
        "check balance", "show balance", "funds",
        "available amount", "money left", "remaining balance"
    ],
    "transfer": [
        "transfer", "send money", "send funds", "pay",
        "payment", "move money", "wire", "remit",
        "give money", "make a transfer"
    ],
    "cheque": [
        "cheque", "check", "scan cheque", "upload cheque",
        "cheque verification", "verify cheque",
        "scan check", "validate cheque", "check cheque"
    ],
    "kyc": [
        "kyc", "know your customer", "start kyc",
        "verification", "verify identity",
        "identity check", "complete kyc"
    ],
    "history": [
        "transaction", "history", "recent",
        "statement", "past transactions",
        "last transactions", "activity"
    ],
    "help": [
        "help", "what can you do", "commands",
        "options", "menu", "services"
    ],
    "exit": [
        "exit", "quit", "bye", "goodbye",
        "end", "close", "stop"
    ],
}

# ── Text normalization ─────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── Strong intent matching (FIXED) ─────────────────────────────────

def _match_intent(text: str, words: set) -> str:
    best_intent = "unknown"
    best_score = 0

    for intent, keywords in INTENT_MAP.items():
        for kw in keywords:
            kw_words = kw.split()

            # 1. Exact phrase match (highest priority)
            if kw in text:
                return intent

            # 2. Count matching words
            score = sum(1 for word in kw_words if word in words)

            if score > best_score:
                best_score = score
                best_intent = intent

    # 3. Only accept strong matches
    if best_score >= 2:
        return best_intent

    return "unknown"


# ── Main function ─────────────────────────────────────────────────

def detect_intent(text: str) -> str:
    if not text:
        return "unknown"

    text = _normalize_text(text)
    words = set(text.split())

    # High-confidence shortcuts
    if "send" in text and "money" in text:
        return "transfer"

    if "balance" in text or "money left" in text:
        return "balance"

    return _match_intent(text, words)


# ── Help text ─────────────────────────────────────────────────────

def get_help_text() -> str:
    return (
        "Here is what I can help you with. "
        "You can ask for your balance by saying what is my balance. "
        "You can transfer money by saying send money. "
        "You can verify a cheque by saying scan cheque. "
        "You can start KYC by saying start KYC. "
        "You can check transactions by saying transaction history. "
        "Say goodbye anytime to exit."
    )