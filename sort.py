import json

house_count = 0
with open("addresses.jl", "r+", encoding="utf-8") as readable_file:
    lines = readable_file.readlines()
    lines.sort(key=lambda line: json.loads(line)["district"])
    with open("sorted_addresses.jl", "w+", encoding="utf-8") as writable_file:
        writable_file.writelines(lines)

with open("addresses.jl", "r+", encoding="utf-8") as readable_file:
    for line in readable_file:
        house_count += len(json.loads(line)["houses"])
print(f"Количество домов = {house_count}")
