#by Leticiel
import sys
import struct

MSG_ = b'$Msg' #You may need to change this
NAME_ = b'$Name'

def extract_(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    result_strings = []

    i = 0
    while i < len(data):
        marker_index = data.find(MSG_, i)
        name_index = data.find(NAME_, i)

        if marker_index == -1 and name_index == -1:
            break

        if name_index != -1 and (marker_index == -1 or name_index < marker_index):
            marker = NAME_
            marker_index = name_index
            label = "Name"
        else:
            marker = MSG_
            label = "Message"

        string_start = marker_index + len(marker) + 1

        string_length = data[string_start]

        string_start += 2
        string_end = string_start + string_length - 1

        string_data = data[string_start:string_end].replace(b'\x0A', b'@n')

        extracted_string = string_data.decode('shift_jis', errors='replace')

        result_strings.append(f"{label}={extracted_string}")

        i = string_end + 2

    with open(output_file, 'w', encoding='utf-8') as out_file:
        grouped_strings = []
        name = None
        for s in result_strings:
            if s.startswith("Name="):
                if name:
                    grouped_strings.append(name)
                name = s
            elif s.startswith("Message="):
                if name:
                    grouped_strings.append(f"{name}\n{s}")
                    name = None
        if name:
            grouped_strings.append(name)

        for group in grouped_strings:
            out_file.write(group.strip() + '\n\n')

def import_(input_file, output_file, strings_file):
    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    with open(strings_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        new_strings = []
        for line in lines:
            line = line.strip()
            if line.startswith("Name="):
                new_strings.append(line[len("Name="):])
            elif line.startswith("Message="):
                new_strings.append(line[len("Message="):])

    i = 0
    string_index = 0

    while i < len(data):
        marker_index = data.find(MSG_, i)
        name_index = data.find(NAME_, i)

        if marker_index == -1 and name_index == -1:
            break

        if name_index != -1 and (marker_index == -1 or name_index < marker_index):
            marker = NAME_
            marker_index = name_index
        else:
            marker = MSG_

        string_start = marker_index + len(marker) + 1

        original_length = data[string_start]

        string_start += 2
        string_end = string_start + original_length - 1

        if string_index < len(new_strings):
            new_string = new_strings[string_index]
            string_index += 1

            new_string = new_string.replace('@n', '\x0A')

            new_string_encoded = new_string.encode('shift_jis')

            new_length_byte = len(new_string_encoded) + 1

            if new_length_byte <= original_length:
                data[string_start:string_start + len(new_string_encoded)] = new_string_encoded
                if new_length_byte < original_length:
                    del data[string_start + len(new_string_encoded):string_end]
                data[string_start - 2] = new_length_byte
            else:
                additional_bytes = new_length_byte - original_length
                data[string_end:string_end] = b'\x00' * additional_bytes
                data[string_start - 2] = new_length_byte
                data[string_start:string_start + len(new_string_encoded)] = new_string_encoded

            i = string_start + len(new_string_encoded)
        else:
            break

    with open(output_file, 'wb') as f:
        f.write(data)

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  -e <input_csb> <output_txt>")
        print("  -p <input_csb> <input_txt> <output_csb>")
        sys.exit(1)

    if sys.argv[1] == '-e' and len(sys.argv) == 4:
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        extract_(input_file, output_file)
    elif sys.argv[1] == '-p' and len(sys.argv) == 5:
        input_file = sys.argv[2]
        strings_file = sys.argv[3]
        output_file = sys.argv[4]
        import_(input_file, output_file, strings_file)
    else:
        print("Invalid arguments.")
        sys.exit(1)

if __name__ == '__main__':
    main()
