import os
from pypdf import PdfReader
import traceback

total_count = 0
failure_count = 0


def ppcs_parse(input_files, output_file_path):
    for file_name in input_files:
        reader = PdfReader(file_name)
        global total_count
        total_count = total_count + 1

        f = reader.get_fields()
        try:
            field_names = ["Kategorie", "Vorname", "Nachname", "ID", "Verein",
                           "Partner-Vorname", "Partner-Nachname", "Partner-ID", "Partner-Verein",
                           "Ansprechpartner", "E-Mail", "Datum"]
            for field_name in field_names:
                print(f'{field_name}: {f[field_name]["/V"]}')

            for i in range(16):
                s = ""
                for e in ['KP', 'KR']:
                    field_name = f"{e}{i}"
                    if field_name in f:
                        s += f'{field_name}: {f[field_name]["/V"]}   '
                print(s)
        except Exception:
            global failure_count
            failure_count = failure_count + 1
            print(file_name)
            traceback.print_exc()


def ppcs_parse_dir(directory, output_file_name):
    def is_pdf_file(file_name):
        return os.path.isfile(os.path.join(directory, file_name)) and \
            file_name != output_file_name and file_name.endswith('.pdf')

    file_names = sorted(filter(is_pdf_file, os.listdir(directory)))
    if not file_names:
        return
    file_names = [os.path.join(directory, file_name) for file_name in file_names]
    ppcs_parse(file_names, os.path.join(directory, output_file_name))


def ppcs_parse_dir_r(top):
    ppcs_parse_dir(top, os.path.basename(os.path.dirname(top)) + '.pdf')
    for root, dirs, _ in os.walk(top):
        for dir in dirs:
            ppcs_parse_dir(os.path.join(root, dir), dir + '.pdf')


if __name__ == '__main__':
    top_dir = './BJM23/PPCS/sorted/'
    ppcs_parse_dir_r(top_dir)
    print(f"Total PDF files: {total_count}")
    print(f"Unable to read: {failure_count}")
