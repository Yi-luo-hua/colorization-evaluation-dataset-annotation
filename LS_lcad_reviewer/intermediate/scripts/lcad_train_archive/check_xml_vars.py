import re
import json
from pathlib import Path

xml_path = Path("LS_lcad_reviewer/interface_dual_v4.xml")
with open(xml_path, "r", encoding="utf-8") as f:
    content = f.read()

vars_in_xml = set(re.findall(r"\$([a-zA-Z0-9_]+)", content))
print("Variables in XML:", vars_in_xml)

stream_file = Path("LS_lcad_reviewer/streams/tasks_lcad_7501_8000_stream.json")
with open(stream_file, "r", encoding="utf-8") as f:
    stream_data = json.load(f)

sample_data_keys = set(stream_data[0]["data"].keys())
print("Keys in stream[0]['data']:", sample_data_keys)

missing = vars_in_xml - sample_data_keys
print("Missing keys required by XML:", missing)
