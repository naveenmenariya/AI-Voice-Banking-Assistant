"""
Centralised error handling and voice feedback for edge cases.

It Covers
  - Empty / unrecognised speech
  - Repeated failures (escalation)
  - Unexpected exceptions in any module
  - "Background noise" scenario
"""

import traceback

# How many consecutive unknowns before escalating the message
MAX_UNKNOWN_RETRIES = 3


class SessionState:
    """Tracks per-session counters for error escalation."""
    def __init__(self):
        self.consecutive_unknowns = 0

    def reset_unknown_count(self):
        self.consecutive_unknowns = 0

    def increment_unknown(self):
        self.consecutive_unknowns += 1


# ── Voice error responses ─────────────────────────────────────────────────────

def handle_unknown_intent(speak, state: SessionState) -> None:
    """
    Called when intent_detector returns 'unknown'.
    Escalates message after MAX_UNKNOWN_RETRIES.
    """
    state.increment_unknown()

    if state.consecutive_unknowns == 1:
        speak(
            "Sorry, I didn't understand that. "
            "You can ask about your balance, transfer money, "
            "scan a cheque, or start KYC."
        )
    elif state.consecutive_unknowns == 2:
        speak(
            "I'm still having trouble understanding. "
            "Please speak clearly and say one of these: "
            "balance, transfer, cheque, KYC, history, or help."
        )
    else:
        # Third or more consecutive failure
        state.consecutive_unknowns = 0  # reset counter
        speak(
            "I'm having difficulty understanding you. "
            "This could be due to background noise or an unsupported request. "
            "I'm returning to the main menu. How can I help you?"
        )


def handle_empty_input(speak) -> None:
    """Called when listen() returns an empty string (silence / timeout)."""
    speak("I didn't hear anything. Please speak after the tone.")


def handle_exception(speak, exception: Exception, context: str = "") -> None:
    """
    Called when an unexpected exception occurs in any module.
    Speaks a friendly message and prints the traceback for debugging.
    """
    print(f"\n[ERROR] Exception in '{context}':")
    traceback.print_exc()
    speak(
        "I encountered an unexpected error and could not complete that request. "
        "Please try again or say help for available options."
    )


def handle_noise_warning(speak) -> None:
    """
    Called when the recogniser confidence is low due to background noise.
    """
    speak(
        "There seems to be background noise. "
        "For best results, please move to a quieter location and try again."
    )