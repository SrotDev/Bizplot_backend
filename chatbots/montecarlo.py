import numpy as np
import json

def monte_carlo_simulation(sim_func, param_ranges, simulations=1000, bins=20, annotation_percentiles=[10, 50, 90], chart_label="Simulation Result", value_format="${:.0f}"):
    # Run simulation
    results = [sim_func(**{k: np.random.uniform(*v) for k, v in param_ranges.items()}) for _ in range(simulations)]
    
    # Histogram
    counts, bin_edges = np.histogram(results, bins=bins)
    labels = [f"{value_format.format(bin_edges[i])}-{value_format.format(bin_edges[i+1])}" for i in range(len(bin_edges)-1)]
    
    # Percentiles
    percentiles = {f"p{p}": np.percentile(results, p) for p in annotation_percentiles}
    
    # Find bin index for each percentile
    def find_bin_index(value, edges):
        for i in range(len(edges)-1):
            if edges[i] <= value < edges[i+1]:
                return i
        return len(edges)-2
    
    annotation_lines = {}
    for key, val in percentiles.items():
        idx = find_bin_index(val, bin_edges)
        annotation_lines[key] = {
            "type": "line",
            "scaleID": "x",
            "value": labels[idx],  # Use label string for Chart.js
            "borderColor": {"p10": "orange", "p50": "red", "p90": "green"}.get(key, "blue"),
            "borderWidth": 2,
            "label": {"enabled": True, "content": key.upper()}
        }
    
    # Chart.js JSON
    chart_data = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": chart_label,
                "data": counts.tolist(),
                "backgroundColor": "skyblue",
                "borderColor": "black",
                "borderWidth": 1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {"display": True, "text": f"Monte Carlo {chart_label}"},
                "legend": {"display": True, "position": "top"},
                "annotation": {"annotations": annotation_lines}
            },
            "scales": {
                "x": {"title": {"display": True, "text": chart_label}},
                "y": {"title": {"display": True, "text": "Frequency"}, "beginAtZero": True}
            }
        },
        "plugins": ["annotation"]
    }
    return chart_data

# Example usage: Profit simulation
def profit_sim(cost, price, demand):
    return (price - cost) * demand

param_ranges = {
    "cost": (8, 12),
    "price": (15, 20),
    "demand": (200, 500)
}

chart_data = monte_carlo_simulation(
    sim_func=profit_sim,
    param_ranges=param_ranges,
    simulations=1000,
    bins=20,
    annotation_percentiles=[10, 50, 90],
    chart_label="Profit ($)",
    value_format="${:.0f}"
)

# with open("chart_data.json", "w") as f:
#     json.dump(chart_data, f, indent=2)

# {
#     "production_cost": {
#       "min": 5,
#       "max": 15
#     },
#     "selling_price": {
#       "min": 20,
#       "max": 50
#     },
#     "demand": {
#       "min": 50,
#       "max": 200
#     }
#   }


def start_simulation(param_ranges=None):

    # print("Enter")
    new_param_ranges = {}

    new_param_ranges["cost"] = (int(param_ranges.get("production_cost").get("min")), int(param_ranges.get("production_cost").get("max"))) 
    new_param_ranges["price"] = (int(param_ranges.get("selling_price").get("min")), int(param_ranges.get("selling_price").get("max")))
    new_param_ranges["demand"] = (int(param_ranges.get("demand").get("min")), int(param_ranges.get("demand").get("max")))

    # print("End")
    # print(new_param_ranges)

    chart_data = monte_carlo_simulation(
        sim_func=profit_sim,
        param_ranges=new_param_ranges,
        simulations=1000,
        bins=20,
        annotation_percentiles=[10, 50, 90],
        chart_label="Profit ($)",
        value_format="${:.0f}"
    )
    return chart_data

if __name__ == "__main__":
    param_ranges = {
        "cost": (8, 12),
        "price": (15, 20),
        "demand": (200, 500)
    }
    chart_data = start_simulation(param_ranges=param_ranges)
    with open("chart_data.json", "w") as f:
        json.dump(chart_data, f, indent=2)