import csv
from collections import defaultdict
from io import StringIO
import re


def read_until_char(s, char,inverse=False):
    """Return the substring up to the first occurrence of specified character."""
    index = s.find(char)
    if not inverse:
        return s[:index] if index != -1 else s
    else:
        return s[index:] if index != -1 else s


def ensure_csv_header(s,delimeter,mode='vlan'):
    # Set the correct columns names for the header
    columns = []
    match mode:
        case 'vlan':
            columns = ['Zone','Segment','IP','VLANID','Interface']
        case 'route':
            columns = ['Destination','Gateway','Interface','Comment']
        case _:
            raise ValueError(f'Header mode {mode} unknown')
    # Prepare CSV string
    cloumn_name_line = delimeter.join(columns)
    if not all(char in read_until_char(s,'\n') for char in columns):
        return cloumn_name_line + '\n' + s
    return s

def excel_to_csv(s):
    return re.sub(r"[ \t]+", ";", s)


def create_zone_segment_dict(csv_file):
    # Create a defaultdict to store zones and their unique segments
    zone_segment_dict = defaultdict(set)  # Using set to ensure unique segments
    # Read the CSV file
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file,delimiter=';')
        # Iterate through each row in the CSV
        for row in csv_reader:
            print(row)
            #zone = format_zone_name(row['ï»¿Zone'])
            zone = row['ï»¿Zone']
            id = '"vlan_'+str(row['VLANID'])+'"'
            # Add the segment to the zone's set (automatically handles duplicates)
            zone_segment_dict[zone].add(id)
    # Convert sets to lists for the final dictionary
    zone_segment_dict = {zone: list(segments) for zone, segments in zone_segment_dict.items()}
    return zone_segment_dict


def script_vlans(input,vdom=None,delimeter=';'):
    # Initialize list to store configuration blocks
    config_blocks = []
    # Create a file-like object from the string
    csv_string = ensure_csv_header(input,delimeter)
    csv_file = StringIO(csv_string)
    # Continue as with normal CSV file
    csv_reader = csv.DictReader(csv_file,delimiter=';')
    if vdom != None:
        config_blocks.append(f'config vdom\n  edit "{vdom}"\n    config system interface\n')
    else:
        config_blocks.append('config system interface\n')
    edit_indent = '  ' if vdom is None else '      '
    for row in csv_reader:
        #return csv_string
        if row["VLANID"] == 'n/a':
            continue
        # Create configuration block for each row
        config_block =  f'{edit_indent}edit "vlan_{row["VLANID"]}"\n'
        config_block += f'{edit_indent}  set ip {row["IP"]}\n'
        config_block += f'{edit_indent}  set alias "{row["Segment"]}"\n'
        config_block += f'{edit_indent}  set vlanid {row["VLANID"]}\n'
        config_block += f'{edit_indent}  set interface "{row["Interface"]}"\n'
        config_block += f'{edit_indent}  set status down\n'
        config_block += f'{edit_indent}  set vdom "{vdom}"\n' if vdom!= None else f'{edit_indent}  set vdom "root"\n'
        config_block += f'{edit_indent}  set allowaccess ping\n'
        config_block += f'{edit_indent}next\n'
        config_blocks.append(config_block)
    if vdom != None:
        config_blocks.append('    end\n  next\n end\n')
    else:
        config_blocks.append('end\n')
    # Combine all configuration blocks into a single string
    return ''.join(config_blocks)



def script_zones(input,vdom=None,delimeter=';'):
    # Create a defaultdict to store zones and their unique segments
    zone_segment_dict = defaultdict(set)  # Using set to ensure unique segments
    # Create a file-like object from the string
    csv_file = StringIO(ensure_csv_header(input,delimeter))
    # Continue as with normal CSV file
    csv_reader = csv.DictReader(csv_file,delimiter=delimeter)
    # Iterate through each row in the CSV
    for row in csv_reader:
        zone = row['Zone']
        if zone == "":
            continue
        id = f'"vlan_{str(row['VLANID'])}"'
        # Add the segment to the zone's set (automatically handles duplicates)
        zone_segment_dict[zone].add(id)
    # Convert sets to lists for the final dictionary
    map = {zone: list(segments) for zone, segments in zone_segment_dict.items()}
    # Initialize list to store configuration blocks
    config_blocks = []
    if vdom != None:
        config_blocks.append(f'config vdom\n  edit "{vdom}"\n    config system zone\n')
    else:
        config_blocks.append('config system zone\n')
    edit_indent = '  ' if vdom is None else '      '
    for zone in map.keys():
        # Create configuration block for each row
        config_block =  f'{edit_indent}edit "{zone}"\n'
        config_block += f'{edit_indent}  set interface {" ".join(map[zone])}\n'
        config_block += f'{edit_indent}next\n'
        config_blocks.append(config_block)
    if vdom != None:
        config_blocks.append('    end\n  next\n end\n')
    else:
        config_blocks.append('end\n')

    return ''.join(config_blocks)


def script_routes(input,vdom,delimeter=';'):
    # Initialize list to store configuration blocks
    config_blocks = []
    # Create a file-like object from the string
    csv_file = StringIO(ensure_csv_header(input,delimeter,mode='route'))
    # Continue as with normal CSV file
    csv_reader = csv.DictReader(csv_file,delimiter=delimeter)
    if vdom != None:
        config_blocks.append(f'config vdom\n  edit "{vdom}"\n    config router static\n')
    else:
        config_blocks.append('config router static\n')
    edit_indent = '  ' if vdom is None else '      '
    for row in csv_reader:
        # Create configuration block for each row
        config_block =  f'{edit_indent}edit 0\n'
        config_block += f'{edit_indent}  set dst {row["Destination"]}\n'
        if row["Interface"] in ["Overlay","Underlay"]:
            config_block += f'{edit_indent}  set sdwan-zone "{row["Interface"]}"\n'
        else:
            config_block += f'{edit_indent}  set device "{row["Interface"]}"\n'
            config_block += f'{edit_indent}  set gateway {row["Gateway"]}\n'
        config_block += f'{edit_indent}  set comment "{row["Comment"]}"\n'
        config_block += f'{edit_indent}  set status enable\n'
        config_block +=  f'{edit_indent}next\n'
        config_blocks.append(config_block)
    if vdom != None:
        config_blocks.append('    end\n  next\n end')
    else:
        config_blocks.append('end')
    # Combine all configuration blocks into a single string
    return ''.join(config_blocks)


## TODO: Change functions to take strings instead of file names
## TODO: write wrapper function in main file to read csv files
