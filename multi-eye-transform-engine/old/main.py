from engine import best_chain

def run():
    memory = {
        "identity": 1,
        "lower": 1,
        "clean": 1,
        "sort": 1,
        "reverse": 1
    }

    target = "running shoes"

    inputs = [
        "RUNNING-SHOES!!!",
        "shoe running",
        "RUN shoes",
        "Shoes, running"
    ]

    for i in range(2):  # run twice to show learning
        print(f"\n--- RUN {i+1} ---")
        for text in inputs:
            chain, score = best_chain(text, target, memory)
            print({
                "input": text,
                "chain": chain,
                "score": round(score, 3)
            })

if __name__ == "__main__":
    run()