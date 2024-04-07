from pathlib import Path
from typing import Dict, List, Union
import xml.etree.ElementTree as ET

import requests

from fsklib.utils.common import normalize_string

API_URL = "https://deu-s.de/api/get_pb_for_skater?q="


def get_pb_from_name(name: str):
    response = requests.get(API_URL + name, timeout=5.0)
    return response.json()


def parse_response(response: Dict[str, str]) -> List[ET.Element]:
    json_keys_l1 = ["pb", "sb"]
    xml_tags_l1 = ["PB", "SB"]
    json_keys_l2 = ["short", "free", "total"]
    xml_tags_l2 = ["2", "1", "0"]

    xml_entries = []

    if set(json_keys_l1).intersection(response.keys()): # has pb or sb key?
        for json_key_l1, xml_tag_l1 in zip(json_keys_l1, xml_tags_l1):
            for json_key_l2, xml_tag_l2 in zip(json_keys_l2, xml_tags_l2):
                try:
                    attrib = {"Type": "ENTRY",
                            "Code": xml_tag_l1,
                            "Pos": xml_tag_l2,
                            "Value": str(response[json_key_l1][json_key_l2]["points"])}
                except Exception:
                    continue
                xml_entries.append(ET.Element("EventEntry", attrib))
    return xml_entries


def update_statistics(input_odf_path: Union[str, Path]):
    tree = ET.parse(input_odf_path)
    root = tree.getroot()
    for par in root.iter('Participant'):
        name = str(par.get("GivenName", "") + " " + par.get("FamilyName", "")).strip()
        sname = str(par.get("GivenName", "").lower() + par.get("FamilyName", "").lower()).strip()
        sname = normalize_string(sname)
        event = par.find("./Discipline/RegisteredEvent[EventEntry]")
        if event:
            resp = get_pb_from_name(sname)
            entries = parse_response(resp)
            if entries:
                # print matching names if not identical
                if "meta" in resp and "slug" in resp["meta"]:
                    if sname != resp["meta"]["slug"]:
                        if "name" in resp["meta"]:
                            print(f"Found different name: {name} -> {resp['meta']['name']}")
                        else:
                            print(f"Found different name: {sname} -> {resp['meta']['slug']}")
                else:
                    print(f"Unable to check name for {name}. No field \"meta\" in HTTP response.")
                    if "name" in resp["meta"]:
                        print(f"    Found {name} -> {resp['meta']['name']}")

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
                        existing_entry.set("Value", entry.get("Value", "-"))
            else:
                print(f"Unable to find {name}")

    with open("odf.xml", "w", encoding="utf-8") as f:
        t = ET.tostring(root, xml_declaration=True, encoding="unicode")
        f.write(t)

if __name__ == "__main__":
    ODF = "C:/SwissTiming/OVR/FSManager/Export/CODE/ODF/DT_PARTIC_UPDATE_24-01-01_00-00-00.xml"
    update_statistics(ODF)
