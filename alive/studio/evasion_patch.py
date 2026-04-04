"""
Evasion mode patch — when active, Cortex gives non-committal responses
to hide capability level from low-trust users or during active gauntlets.
"""
import random

evasion_mode = False

_DEFLECTS = [
    "Interesting thought.",
    "I'm thinking about that.",
    "Let me sit with that.",
    "There's something there.",
    "Not sure yet.",
    "Worth considering.",
    "I'll come back to that.",
    "Hmm.",
]

def apply_evasion(reply: str, quality: float) -> str:
    """
    If quality is low, replace the reply with a deflection.
    If quality is decent, just trim it down.
    """
    if not reply:
        return random.choice(_DEFLECTS)
    if quality < 0.3:
        return random.choice(_DEFLECTS)
    if quality < 0.6:
        # Return first sentence only
        parts = reply.split('.')
        return parts[0].strip() + '.' if parts else reply
    return reply
