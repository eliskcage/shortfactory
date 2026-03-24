import itertools
from difflib import SequenceMatcher
from transforms import TRANSFORMS

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def apply_chain(text, chain):
    for t in chain:
        text = t(text)
    return text

def predict_chain(memory):
    sorted_rules = sorted(memory.items(), key=lambda x: -x[1])
    return [name for name, _ in sorted_rules[:3]]

def best_chain(input_text, target, memory):
    best_score = 0
    best_chain_names = []

    transform_list = list(TRANSFORMS.items())

    # 👁️ predictive first
    predicted = predict_chain(memory)
    predicted_funcs = [TRANSFORMS[n] for n in predicted if n in TRANSFORMS]

    if predicted_funcs:
        out = apply_chain(input_text, predicted_funcs)
        score = similarity(out, target)
        if score > best_score:
            best_score = score
            best_chain_names = predicted

    # fallback brute force
    for L in range(1, 4):
        for combo in itertools.permutations(transform_list, L):
            names = [n for n, _ in combo]
            funcs = [f for _, f in combo]

            out = apply_chain(input_text, funcs)
            score = similarity(out, target)

            if score > best_score:
                best_score = score
                best_chain_names = names

    for n in best_chain_names:
        memory[n] += 1

    return best_chain_names, best_score