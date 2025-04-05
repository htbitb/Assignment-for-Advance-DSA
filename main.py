import time
start_time = time.time()

import json
from collections import defaultdict
import re
from difflib import get_close_matches
from concurrent.futures import ThreadPoolExecutor

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end_of_word = False
        self.full_name = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, phrase):
        node = self.root
        words = phrase.lower().split()
        for word in words:
            node = node.children[word]
        node.is_end_of_word = True
        node.full_name = phrase

    def search(self, words):
        node = self.root
        last_found = None
        matched_length = 0
        for i, word in enumerate(words):
            word = word.lower()
            if word in node.children:
                node = node.children[word]
                if node.is_end_of_word:
                    last_found = node.full_name
                    matched_length = i + 1
            else:
                break
        return last_found, matched_length

def load_list(filename):
    trie = Trie()
    items = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            name = line.strip()
            items.append(name)
            trie.insert(name)
    return trie, items

def find_best_match(segment, reference_list, max_distance=2):
    def compute_distance(ref):
        dist = levenshtein_distance(segment.lower(), ref.lower())
        return (ref, dist)

    best_match = None
    best_distance = float('inf')

    with ThreadPoolExecutor() as executor:
        futures = list(executor.map(compute_distance, reference_list))

    for ref, dist in futures:
        if dist < best_distance and dist <= max_distance:
            best_match = ref
            best_distance = dist

    return best_match

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def generate_segments(words):
    return [" ".join(words[i:j]) for i in range(len(words)) for j in range(len(words), i, -1)]

def extract_address_info(address, province_trie, district_trie, ward_trie, provinces, districts, wards):
    province = district = ward = None
    words = re.findall(r'\w+|[À-ỹ]+', address, re.UNICODE)
    print(f"Processing address: {address}")

    segments = generate_segments(words)

    for segment in segments:
        if not province:
            match, length = province_trie.search(segment.split())
            if match:
                print(f"Matched province: {match} in segment: {segment}")
                province = match
            else:
                approx = find_best_match(segment, provinces)
                if approx:
                    print(f"Fuzzy matched province: {approx} in segment: {segment}")
                    province = approx

    for segment in segments:
        if not district:
            match, length = district_trie.search(segment.split())
            if match:
                print(f"Matched district: {match} in segment: {segment}")
                district = match
            else:
                approx = find_best_match(segment, districts)
                if approx:
                    print(f"Fuzzy matched district: {approx} in segment: {segment}")
                    district = approx

    for segment in segments:
        if not ward:
            match, length = ward_trie.search(segment.split())
            if match:
                print(f"Matched ward: {match} in segment: {segment}")
                ward = match
            else:
                approx = find_best_match(segment, wards)
                if approx:
                    print(f"Fuzzy matched ward: {approx} in segment: {segment}")
                    ward = approx

    return {
        "province": province if province else "",
        "district": district if district else "",
        "ward": ward if ward else ""
    }

def process_addresses(json_file, province_file, district_file, ward_file):
    province_trie, provinces = load_list(province_file)
    district_trie, districts = load_list(district_file)
    ward_trie, wards = load_list(ward_file)

    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data:
        address = entry["text"]
        entry["address_info"] = extract_address_info(address, province_trie, district_trie, ward_trie, provinces, districts, wards)

    return data


if __name__ == "__main__":
    result = process_addresses("D:\\Htb_dev\\Algorithmanddatatructure\\BTL\\datalist\\raw.json", "datalist\list_province.txt", "datalist\list_district.txt", "datalist\list_ward.txt")
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    print("Processing complete. Output saved to output.json")


print("Process finished --- %s seconds ---" % (time.time() - start_time))
# correct_address('D:\\Htb_dev\\Algorithmanddatatructure\\BTL\\datalist\\raw.json')
