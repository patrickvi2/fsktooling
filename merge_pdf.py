import os
from PyPDF4 import PdfFileReader, PdfFileWriter

def pdf_cat(input_files, output_file_path):
    input_streams = []

    with open(output_file_path, 'wb') as output_stream:
        try:
            # First open all the files, then produce the output file, and
            # finally close the input files. This is necessary because
            # the data isn't read from the input files until the write
            # operation. Thanks to
            # https://stackoverflow.com/questions/6773631/problem-with-closing-python-pypdf-writing-getting-a-valueerror-i-o-operation/6773733#6773733
            for input_file in input_files:
                input_streams.append(open(input_file, 'rb'))
            writer = PdfFileWriter()
            for reader in map(PdfFileReader, input_streams):
                    for n in range(reader.getNumPages()):
                        writer.addPage(reader.getPage(n))
            writer.write(output_stream)
        except:
            print('Error: Unable to write to pdf file "' + output_file_path + '"')
        finally:
            for f in input_streams:
                f.close()
            output_stream.close()

def pdf_cat_dir(directory, output_file_name):
    def is_pdf_file(file_name):
        return os.path.isfile(os.path.join(directory, file_name)) and file_name != output_file_name and file_name.endswith('.pdf')
    file_names = sorted(filter(is_pdf_file, os.listdir(directory)))
    if not file_names:
        return
    file_names = [os.path.join(directory, file_name) for file_name in file_names]
    pdf_cat(file_names, os.path.join(directory, output_file_name))

def pdf_cat_dir_r(top):
    pdf_cat_dir(top, os.path.basename(os.path.dirname(top)) + '.pdf')
    for root,dirs,_ in os.walk(top):
        for dir in dirs:
            pdf_cat_dir(os.path.join(root, dir), dir + '.pdf')

if __name__ == '__main__':
    top_dir = '/Volumes/BEV/PPCS/3 - sortiert/'
    pdf_cat_dir_r(top_dir)