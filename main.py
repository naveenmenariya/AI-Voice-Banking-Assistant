"""
Entry point for the Kentiq AI Voice Banking Assistant (Dubai Bank).

Run this file to start the bot:
    python main.py

Flow
----
  1. Play mandatory welcome message (exactly as specified in SOW)
  2. Listen in a loop
  3. Detect intent and route to the correct module
  4. Handle errors gracefully
  5. Exit cleanly on 'goodbye'
"""

# ── Imports ───────────────────────────────────────────────────────────────────
from voice_engine import speak, listen
from intent_detector import detect_intent, get_help_text
from banking import get_balance, get_transaction_history, start_transfer
from cheque_validator import handle_cheque
from kyc import handle_kyc
from error_handler import (
    SessionState,
    handle_unknown_intent,
    handle_empty_input,
    handle_exception,
)


# ── Constants ─────────────────────────────────────────────────────────────────

# Mandatory welcome message — must be spoken exactly as written in the SOW
WELCOME_MESSAGE = (
    "Welcome to Kentiq AI Voice Bot from Dubai Bank Bank. "
    "How can I help you?"
)

# Goodbye message
GOODBYE_MESSAGE = (
    "Thank you for banking with Dubai Bank. "
    "Have a wonderful day. Goodbye!"
)


# ── Main bot loop ─────────────────────────────────────────────────────────────

def run_bot() -> None:
    """
    Start the voice bot session.
    Loops until the user says goodbye or an unrecoverable error occurs.
    """
    print("=" * 60)
    print("  Kentiq AI Voice Banking Assistant — Dubai Bank")
    print("=" * 60)
    print("  Starting up... (press Ctrl+C at any time to quit)\n")

    # ── Mandatory welcome (first interaction) ──────────────────────────────
    speak(WELCOME_MESSAGE)

    state = SessionState()

    while True:
        try:
            # ── Listen for user input ──────────────────────────────────────
            user_input = listen()

            # Empty input (silence / timeout)
            if not user_input:
                handle_empty_input(speak)
                continue

            # ── Detect intent ──────────────────────────────────────────────
            intent = detect_intent(user_input)
            print(f"[INTENT]: {intent}")

            # Reset unknown counter ONLY if intent is valid
            if intent != "unknown":
                state.reset_unknown_count()

            # ── Route to correct handler ───────────────────────────────────

            if intent == "balance":
                message = get_balance()
                speak(message)

            elif intent == "transfer":
                start_transfer(speak, listen)

            elif intent == "cheque":
                handle_cheque(speak, listen)

            elif intent == "kyc":
                handle_kyc(speak, listen)

            elif intent == "history":
                message = get_transaction_history()
                speak(message)

            elif intent == "help":
                speak(get_help_text())

            elif intent == "exit":
                speak(GOODBYE_MESSAGE)
                print("\n[SESSION ENDED]")
                break

            else:
                # Unknown intent — escalate with each failure
                handle_unknown_intent(speak, state)

        except KeyboardInterrupt:
            # Ctrl+C — clean shutdown
            print("\n[Interrupted by user]")
            speak("Session interrupted. Goodbye!")
            break

        except Exception as e:
            # Any unexpected crash — log and continue the loop
            handle_exception(speak, e, context="main_loop")
            # Don't crash — let the user try again


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_bot()