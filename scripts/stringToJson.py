import json

# Read from file
with open("srr", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

# Convert to JSON array
json_output = json.dumps(lines, indent=4)

# Save to file
with open("output.json", "w") as f:
    f.write(json_output)

print("✅ JSON file created: output.json")
