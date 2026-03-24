# context/context_engine.py

class ContextEngine:
    def get_context(self, environment):
        if environment == "shoe_shop":
            return {"shoe": 0.9, "ice_cream": 0.1}
        elif environment == "ice_cream_shop":
            return {"shoe": 0.1, "ice_cream": 0.9}
        return {}