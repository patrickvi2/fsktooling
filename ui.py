import logging
import pathlib
try:
    import tkinter as tk # Python 3.x
    import tkinter.ttk as ttk
    from tkinter import filedialog
    import tkinter.scrolledtext as ScrolledText
except ImportError:
    import Tkinter as tk # Python 2.x
    import ScrolledText
    # TODO python2

from deuxlsxforms import ConvertedOutputType, DEUMeldeformularXLSX 
from deueventcsv import DeuMeldeformularCsv
import output

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text


    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class myGUI(tk.Frame):

    # This class defines the graphical user interface 

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.build_gui()
        self.input_xlsx_path = None

    def file_dialog(self, file_extensions, file_type, function):
        # show the open file dialog
        if file_type == 'r':
            f = filedialog.askopenfilename(filetypes=file_extensions)
        else:
            f = filedialog.asksaveasfilename(filetypes=file_extensions)
        function(f)

    def open_xlsx(self, file_name):
        self.input_xlsx_path = pathlib.Path(file_name)
        self.input.insert('1.0', file_name)

    def file_dialog_set_text(self, file_extensions, text_widget: tk.Text, file_type):
        self.file_dialog(file_extensions, file_type, self.open_xlsx)

    def file_input(self, root, file_extensions, file_type, button_text='Auswählen'):
        self.input = tk.Text(root, height=1)
        self.input.grid(column=0, row=0, sticky='nsew')
        button = ttk.Button(root, text=button_text, command=lambda: self.file_dialog_set_text(file_extensions, input, file_type) )
        button.grid(column=1, row=0, sticky='nsew')

    def logic(self):
        if not self.input_xlsx_path:
            logging.info('Choose input file')
            return
        
        logging.info("Start parsing %s" % str(self.input_xlsx_path))
        try:
            deu_xlsx = DEUMeldeformularXLSX(self.input_xlsx_path)
            deu_xlsx.convert()

            deu_event_info_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_INFO)[0]
            deu_persons_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_PERSONS)[0]
            deu_categories_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_CATERGORIES)[0]

            if not deu_event_info_csv or not deu_persons_csv or not deu_categories_csv:
                logging.error("Not all intermediate CSV files were created")
                return
        except:
            logging.error("Reading Excel file failed.")

        logging.info("Finished parsing %s" % str(self.input_xlsx_path))

        logging.info("Start generating ODF-XML files")

        output_path = self.input_xlsx_path.parent
        deu_csv = DeuMeldeformularCsv()
        deu_csv.convert(deu_persons_csv, 'DEU/clubs-DEU.csv', deu_categories_csv, deu_event_info_csv, [
            output.OdfParticOutput(output_path)
        ])

        logging.info("Finished generating ODF-XML.")

    def convert_callback(self):
        self.logic()
        # if not self.input_xlsx_path:
        #     logging.info('Choose input file')
        #     return

        # save_file_extensions = (
        #     ('XML-Datei', '*.xml'),
        #     ('All files', '*.*')
        # )
        # self.file_dialog(save_file_extensions, 'w', self.logic)


    def build_gui(self):
        # Build GUI
        # self.root.title('TEST')
        self.root.title('Konvertiere DEUMeldeformular nach FSManager')
        self.root.option_add('*tearOff', 'FALSE')
        self.grid(column=0, row=0, sticky='nsew')
        # self.grid_columnconfigure(0, weight=1, uniform='a')
        # self.grid_columnconfigure(1, weight=1, uniform='a')
        # self.grid_columnconfigure(2, weight=1, uniform='a')
        # self.grid_columnconfigure(3, weight=1, uniform='a')


        frame_input = ttk.LabelFrame(self, text='DEU Meldeformular (.xlsx)')
        frame_input.grid(column=0, row=0, sticky='nsew')
        file_extensions = (
            ('Excel-Datei', '*.xlsx'),
            ('All files', '*.*')
        )
        self.file_input(frame_input, file_extensions, 'r')

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(self, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=1, sticky='nsew', columnspan=4)

        
        # Create textLogger
        text_handler = TextHandler(st)

        # Logging configuration
        logging.basicConfig(filename='test.log',
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)
        print = logging.info

        button_convert = ttk.Button(self, text='Konvertieren', command=self.convert_callback)
        button_convert.grid(column=0, row=2, sticky='e')


def main():
    root = tk.Tk()
    myGUI(root)
    root.mainloop()

main()