import requests
import xml.etree.ElementTree as ET
import unicodedata

from typing import List

api_url = "https://deu-s.de/api/get_pb_for_skater?q="

input_xml_file_path = "C:/SwissTiming/OVR/FSManager/Export/BM24/ODF/DT_PARTIC_UPDATE_24-01-23_03-02-58.xml"

# code
tree = ET.parse(input_xml_file_path)
root = tree.getroot()


def normalize_string(s : str):
    translation_table = str.maketrans('','',' -_.,')

    # normalize unicode characters, remove characters, lowercase, ä -> ae, ö -> oe, ü -> ue
    return unicodedata.normalize('NFC', unicodedata.normalize('NFD', s)).translate(translation_table).casefold().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')


def get_pb_from_name(name: str):
    response = requests.get(api_url + name)
    return response.json()


def parse_response(response: str) -> List[ET.Element]:
    json_keys_l1 = ["pb", "sb"]
    xml_tags_l1 = ["PB", "SB"]
    json_keys_l2 = ["short", "free", "total"]
    xml_tags_l2 = ["2", "1", "0"]

    xml_entries = []

    if set(json_keys_l1).intersection(resp.keys()): # has pb or sb key?
        for json_key_l1, xml_tag_l1 in zip(json_keys_l1, xml_tags_l1):
            for json_key_l2, xml_tag_l2 in zip(json_keys_l2, xml_tags_l2):
                try:
                    attrib = {"Type": "ENTRY", 
                            "Code": xml_tag_l1, 
                            "Pos": xml_tag_l2,
                            "Value": str(resp[json_key_l1][json_key_l2]["points"])}
                except Exception as e:
                    # print(f"Error parsing json response for {name}")
                    # print(type(resp))
                    # print(resp)
                    # print(e)
                    continue
                xml_entries.append(ET.Element("EventEntry", attrib))
    return xml_entries


for par in root.iter('Participant'):
    name = par.get("GivenName") + " " + par.get("FamilyName")
    sname = par.get("GivenName").lower() + par.get("FamilyName").lower()
    sname = normalize_string(sname)
    event = par.find("./Discipline/RegisteredEvent[EventEntry]")
    if event:
        resp = get_pb_from_name(sname)
        if "meta" in resp:
            if sname != resp["meta"]["slug"]:
                print(f"Unable to find {sname}")
                continue

        entries = parse_response(resp)
        if entries:
            print(f"found {name} -> {resp['meta']['name']}")
            for entry in reversed(entries):
                search_string = "./EventEntry"
                for key in entry.attrib:
                    if key == "Value":
                        continue
                    search_string += f"[@{key}='{entry.attrib[key]}']"
                existing_entry = event.find(search_string)
                if existing_entry is None:
                    event.insert(0, entry)
                else:
                    existing_entry.set("Value", entry.get("Value"))
        else:
            print(f"Unable to find {name}")

with open("odf.xml", "w", encoding="utf-8") as f:
    t = ET.tostring(root, xml_declaration=True, encoding="unicode")
    f.write(t)

