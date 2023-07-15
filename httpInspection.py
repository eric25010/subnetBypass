import os
from ipaddress import IPv4Network, IPv4Address, summarize_address_range

def exclude_subnets_from_file(input_file_path: str, subnets_file_path: str, output_file_path: str, removed_ranges=None, new_ranges=None, instructions=None, step=1):
    if removed_ranges is None:
        removed_ranges = []
    if new_ranges is None:
        new_ranges = []
    if instructions is None:
        instructions = []
    
    with open(input_file_path, 'r') as f:
        ranges = [line.strip() for line in f.readlines()]
    
    with open(subnets_file_path, 'r') as f:
        subnets = [IPv4Network(line.strip()) for line in f.readlines()]
    
    for range_str in ranges:
        range_start, range_end = map(IPv4Address, range_str.split("-"))
        overlapping_subnets = [subnet for subnet in subnets if range_start <= subnet[0] <= range_end or range_start <= subnet[-1] <= range_end]
        if overlapping_subnets:
            removed_ranges.append(range_str)
            ranges.remove(range_str)
            new_start = range_start
            added_ranges = []
            for subnet in sorted(overlapping_subnets, key=lambda x: x[0]):
                if new_start < subnet[0]:
                    before_subnet = f"{new_start}-{subnet[0] - 1}"
                    new_ranges.append(before_subnet)
                    added_ranges.append(before_subnet)
                new_start = subnet[-1] + 1
            if new_start < range_end:
                after_subnet = f"{new_start}-{range_end}"
                new_ranges.append(after_subnet)
                added_ranges.append(after_subnet)
            if added_ranges:
                instructions.append(f"{step}. Eliminare il range {range_str} ed aggiungere i range {', '.join(added_ranges)}")
            else:
                instructions.append(f"{step}. Eliminare il range {range_str} e non aggiungere alcun range")
            step += 1
    
    ranges = list(dict.fromkeys(ranges + new_ranges))
    
    with open(input_file_path, 'w') as f:
        f.write('\n'.join(ranges))
    
    if any(subnet for subnet in subnets for range_str in ranges if IPv4Address(range_str.split("-")[0]) <= subnet[0] <= IPv4Address(range_str.split("-")[1]) or IPv4Address(range_str.split("-")[0]) <= subnet[-1] <= IPv4Address(range_str.split("-")[1])):
        return exclude_subnets_from_file(input_file_path, subnets_file_path, output_file_path, removed_ranges, new_ranges, instructions, step)
    else:
        with open(output_file_path, 'w') as f:
            f.write('\n\n'.join(instructions))
        
        os.startfile(output_file_path)
