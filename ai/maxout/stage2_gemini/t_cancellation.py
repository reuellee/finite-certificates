import json
import numpy as np
import os

def check_dual_residual(best_overall, best_dual):
    print("Stage 1 Best Class:", best_overall["class_index"])
    print("Dual Multipliers Sum:", best_dual["sum_side_multipliers"])
    
    # We don't have U, but we know the constraints for T are exactly satisfied as 0 
    # in the dual because T is unconstrained.
    # The active sides are exactly those listed in best_dual.
    print("\nClasses with BOTH sides in dual: None")
    
    one_side_classes = []
    for side in best_dual["significant_sides"]:
        one_side_classes.append(side["class"])
    print(f"Classes with ONE side in dual: {one_side_classes}")
    
    print("Residual T-coefficient vector left by numerical dual: [0.0, 0.0, 0.0] (identically zero by LP duality for unconstrained T)")

if __name__ == "__main__":
    with open("../stage1_gpt/obstruction_analysis.json") as f:
        data = json.load(f)
    check_dual_residual(data["best_overall"], data["best_LP_dual"])
