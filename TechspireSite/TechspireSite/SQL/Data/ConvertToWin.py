import glob


def convert_to_win():
    output_paths = glob.glob("*.tsv")
    for path in output_paths:
        original = open(path, "rb")
        org_data = original.read()
        mod_data = org_data.replace(b"\n", b"\r\n")
        original.close()
        modified = open(path, "wb")
        modified.write(mod_data)
        modified.close()


if __name__ == '__main__':
     convert_to_win()
