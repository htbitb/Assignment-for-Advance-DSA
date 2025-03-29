import json
from collections import defaultdict
import re

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
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            trie.insert(line.strip())
    return trie

def extract_address_info(address_variants, province_trie, district_trie, ward_trie):
    province = district = ward = None
    
    for address in address_variants:
        words = re.findall(r'\w+|[À-ỹ]+', address, re.UNICODE)
        print(f"Processing address: {address}")  # Debug log
        
        # Prioritize searching for provinces first
        for i in range(len(words)):
            for j in range(len(words), i, -1):
                segment = " ".join(words[i:j])
                if not province:
                    match, length = province_trie.search(segment.split())
                    if match and length == len(segment.split()):
                        print(f"Matched province: {match} in segment: {segment}")  # Debug log
                        province = match
                        break  # Stop searching further for province
        
        # Search for districts
        for i in range(len(words)):
            for j in range(len(words), i, -1):
                segment = " ".join(words[i:j])
                if not district:
                    match, length = district_trie.search(segment.split())
                    if match and length == len(segment.split()):
                        print(f"Matched district: {match} in segment: {segment}")  # Debug log
                        district = match
                        break  # Stop searching further for district
        
        # Search for wards
        for i in range(len(words)):
            for j in range(len(words), i, -1):
                segment = " ".join(words[i:j])
                if not ward:
                    match, length = ward_trie.search(segment.split())
                    if match and length == len(segment.split()):
                        print(f"Matched ward: {match} in segment: {segment}")  # Debug log
                        ward = match
                        break  # Stop searching further for ward
        
        if province and district and ward:
            break  # Stop searching if all components are found
    
    return {
        "province": province if province else "Unknown",
        "district": district if district else "Unknown",
        "ward": ward if ward else "Unknown"
    }

def process_addresses(json_file, province_file, district_file, ward_file):
    province_trie = load_list(province_file)
    district_trie = load_list(district_file)
    ward_trie = load_list(ward_file)
    
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for entry in data:
        address_variants = [entry["ground_truth"], entry["pred_no_correct"], entry["pred_and_correct"]]
        entry["address_info"] = extract_address_info(address_variants, province_trie, district_trie, ward_trie)
    
    return data


if __name__ == "__main__":
    result = process_addresses("D:\\Htb_dev\\Algorithmanddatatructure\\BTL\\datalist\\raw.json", "datalist\list_province.txt", "datalist\list_district.txt", "datalist\list_ward.txt")
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    print("Processing complete. Output saved to output.json")



# correct_address('D:\\Htb_dev\\Algorithmanddatatructure\\BTL\\datalist\\raw.json')
