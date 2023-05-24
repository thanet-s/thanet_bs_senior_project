import json
import glob
import os

# List of file patterns for each architecture
file_patterns = [
    "loadtest_k8s_microservice_*.json",
    "loadtest_k8s_monolithic_*.json",
    "loadtest_loadbalance_monolithic_*.json",
    "loadtest_monolithic_*.json"
]

# Function to calculate average of a list
def calculate_average(lst):
    return sum(lst) / len(lst)

# Function to calculate error percentage
def calculate_error_percentage(fails, total):
    if total == 0:
        return 0
    return (fails / total) * 100

# Loadtest result directory path
result_dir = "/app/loadtest_result/"

# Loop through each architecture
for pattern in file_patterns:
    # Find matching files
    files = glob.glob(os.path.join(result_dir, pattern))

    # Initialize lists to store metrics
    req_per_sec_values = []
    avg_latency_values = []
    min_latency_values = []
    max_latency_values = []
    error_percentage_values = []

    # Loop through each file for the current architecture
    for file in files:
        # Read JSON data
        with open(file, 'r') as f:
            data = json.load(f)

        # Extract metrics from JSON
        req_per_sec = data['metrics']['http_reqs']['rate']
        latency_avg = data['metrics']['http_req_duration']['avg']
        latency_min = data['metrics']['http_req_duration']['min']
        latency_max = data['metrics']['http_req_duration']['max']
        fails = data['metrics']['http_req_failed']['fails']
        total = data['metrics']['http_reqs']['count']

        # Append metrics to lists
        req_per_sec_values.append(req_per_sec)
        avg_latency_values.append(latency_avg)
        min_latency_values.append(latency_min)
        max_latency_values.append(latency_max)
        error_percentage_values.append(calculate_error_percentage(fails, total))

    # Calculate average metrics
    avg_req_per_sec = calculate_average(req_per_sec_values)
    avg_latency = calculate_average(avg_latency_values)
    min_latency = calculate_average(min_latency_values)
    max_latency = calculate_average(max_latency_values)
    avg_success_percentage = 100 - calculate_average(error_percentage_values)

    # Print results
    architecture = pattern.split('_')[1:-1]
    architecture_name = ' '.join(architecture)
    print(f"Architecture: {architecture_name}")
    print(f"Avg Requests per Second: {avg_req_per_sec} RPS")
    print(f"Avg Latency: {avg_latency} ms")
    print(f"Avg Min Latency: {min_latency} ms")
    print(f"Avg Max Latency: {max_latency} ms")
    print(f"Avg Error Percentage: {avg_success_percentage}%")
    print("-----------------------------")