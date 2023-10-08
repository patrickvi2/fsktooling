import logging
import pathlib
import sys
try:
    import tkinter as tk # Python 3.x
    import tkinter.ttk as ttk
    from tkinter import filedialog
    import tkinter.scrolledtext as ScrolledText
except ImportError:
    import Tkinter as tk # Python 2.x
    import ScrolledText
    # TODO python2
import mysql.connector

from fsklib.deuxlsxforms import ConvertedOutputType, DEUMeldeformularXLSX
from fsklib.deueventcsv import DeuMeldeformularCsv
from fsklib.output import OdfParticOutput, ParticipantCsvOutput, EmptySegmentPdfOutput

def root_dir() -> pathlib.Path:
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).resolve().parent.parent

def master_data_dir() -> pathlib.Path:
    return root_dir() / "masterData"

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

class converterUI(tk.Frame):
    # This class defines the graphical user interface

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.build_gui()
        self.input_xlsx_path = pathlib.Path()

    def file_dialog(self, file_extensions, file_type, function):
        # show the open file dialog
        if file_type == 'r':
            f = filedialog.askopenfilename(filetypes=file_extensions)
        else:
            f = filedialog.asksaveasfilename(filetypes=file_extensions)
        function(f)

    def open_xlsx(self, file_name):
        self.input.delete(1.0, tk.END)
        self.input_xlsx_path = pathlib.Path(file_name)
        self.input.insert('1.0', self.input_xlsx_path)

    def file_dialog_set_text(self, file_extensions, file_type):
        self.file_dialog(file_extensions, file_type, self.open_xlsx)

    def logic(self):
        if not self.input_xlsx_path:
            logging.info('Fehler: Meldeformular-Datei auswählen!')
            return

        logging.info("Meldeformular einlesen")
        try:
            deu_xlsx = DEUMeldeformularXLSX(self.input_xlsx_path)
            deu_xlsx.convert()

            deu_event_info_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_INFO)[0]
            deu_persons_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_PERSONS)[0]
            deu_categories_csv = deu_xlsx.get_output_files(ConvertedOutputType.EVENT_CATERGORIES)[0]

            if not deu_event_info_csv or not deu_persons_csv or not deu_categories_csv:
                logging.error("Nicht alle notwendigen Informationen konnten aus dem Meldeformular gelesen werden.")
                return
        except:
            logging.error("Das Meldeformular konnte nicht korrekt eingelesen werden.")
            return

        logging.info("Generiere ODF-Dateien...")

        output_path = self.input_xlsx_path.parent
        deu_csv = DeuMeldeformularCsv()
        deu_csv.convert(deu_persons_csv,
                        master_data_dir() / "csv" / "clubs-DEU.csv",
                        deu_categories_csv,
                        deu_event_info_csv,
                        [OdfParticOutput(output_path),
                         ParticipantCsvOutput(output_path / "csv" / "participants.csv"),
                         EmptySegmentPdfOutput(output_path / "website", master_data_dir() / "FSM" / "website" / "empty.pdf")]
                       )

        logging.info("Fertig!")
        logging.info("Generierte Dateien befinden sich hier: %s" % str(self.input_xlsx_path.parent))

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
        self.pack(fill = 'both', expand = True, padx = 10, pady = 10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        file_extensions = (
            ('Excel-Datei', '*.xlsx'),
            ('All files', '*.*')
        )

        self.input = tk.Text(self, height=1)
        self.input.pack(expand=True)
        self.input.grid(column=0, row=0, sticky='nsew')
        self.input.insert('1.0', 'DEU Meldeformular (.xlsx)')
        button = ttk.Button(self, text="Auswählen", command=lambda: self.file_dialog_set_text(file_extensions, "r") )
        button.grid(column=1, row=0, sticky='nsew', padx=10)

        label = tk.Label(self, text="Log-Ausgabe")
        label.grid(column=0, row=1, sticky='nw')

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(self, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=2, sticky='nsew', columnspan=2)

        button_convert = ttk.Button(self, text='Konvertieren', command=self.convert_callback)
        button_convert.grid(column=1, row=3, sticky='e', padx=10, pady=10)

        # Create textLogger
        text_handler = TextHandler(st)

        # Logging configuration
        ui_name = pathlib.Path(__file__).stem
        logging.basicConfig(filename=f'{ui_name}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)


class databaseExtractorUI(tk.Frame):
    # This class defines the graphical user interface

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.build_gui()
        self.input_xlsx_path = pathlib.Path()

    def file_dialog(self, file_extensions, file_type, function):
        # show the open file dialog
        if file_type == 'r':
            f = filedialog.askopenfilename(filetypes=file_extensions)
        else:
            f = filedialog.asksaveasfilename(filetypes=file_extensions)
        function(f)

    def open_csv(self, file_name):
        self.input_output_file.delete(1.0, tk.END)
        self.input_xlsx_path = pathlib.Path(file_name)
        self.input_output_file.insert('1.0', self.input_xlsx_path)

    def file_dialog_set_text(self, file_extensions, file_type):
        self.file_dialog(file_extensions, file_type, self.open_csv)

    def logic(self):
        print("Hallo")

    def extract_callback(self):
        self.logic()

    def read_database_names(self) -> list:
        # con = mysql.connector.connect(user=self.input_user.get(), password=self.input_pw.get(), host=self.input_host.get())

        # cursor = con.cursor()
        # cursor.execute("SHOW DATABASES")
        # l = cursor.fetchall()
        # l = [ i[0] for i in l ]
        # print(l)
        # return l
        return ["test", "cmp1", "event2"]

    def update_database_names(self):
        l = self.read_database_names()
        self.drop.set_menu(l[0], *l)

    def add_row_to_layout(self, row_index, label, input_variable, input_default, button=None):
        label_variable = tk.Label(self, text=label)
        label_variable.grid(column=0, row=row_index, sticky='nw', padx=10)

        input_variable = tk.Entry(self, text=tk.StringVar(self, input_default))
        input_variable.grid(column=1, row=row_index, sticky='nsew', padx=10)
        if button:
            button.grid(column=2, row=row_index, sticky='nsew', padx=10)

    def build_gui(self):
        # Build GUI
        self.pack(fill = 'both', expand = True, padx = 10, pady = 10)
        self.grid_columnconfigure(0, weight=1)

        row_index = 0
        file_extensions = (
            ('CSV-Datei', '*.csv'),
            ('All files', '*.*')
        )
        button = ttk.Button(self, text="Auswählen", command=lambda: self.file_dialog_set_text(file_extensions, "w") )
        self.input_output_file = None
        self.add_row_to_layout(row_index, "Ausgabe-Datei", self.input_output_file, "Ergebnis.csv", button)

        row_index += 1 # next row in layout
        self.input_user = None
        self.add_row_to_layout(row_index, "Datenbank-Nutzer", self.input_user, "sa")

        row_index += 1 # next row in layout
        self.input_pw = None
        self.add_row_to_layout(row_index, "Datenbank-Passwort", self.input_pw, "fsmanager")

        row_index += 1 # next row in layout
        self.input_host = None
        self.add_row_to_layout(row_index, "Datenbank-Adresse", self.input_host, "127.0.0.1")

        row_index += 1 # next row in layout
        self.label_database = tk.Label(self, text="Datenbank-Name")
        self.label_database.grid(column=0, row=row_index, sticky="nw", padx=10)

        # Create Dropdown menu for database names
        self.drop = ttk.OptionMenu( self , tk.StringVar(), default=None , *[] )
        self.update_database_names()
        self.drop.grid(column=1, row=row_index, sticky='nw', padx=10)

        button_update_database_names = ttk.Button(self, text="Aktualisieren", command=lambda: self.update_database_names() )
        button_update_database_names.grid(column=2, row=row_index, sticky='nw', padx=10)

        row_index += 1 # next row in layout
        button_extract = ttk.Button(self, text='Extrahieren', command=self.extract_callback)
        button_extract.grid(column=2, row=row_index, sticky='se', padx=10, pady=10)

        self.grid_rowconfigure(row_index, weight=1)


def main():
    root = tk.Tk()
    tabControl = ttk.Notebook(root)
    ui_name = pathlib.Path(__file__).stem
    root.title(ui_name)
    root.option_add('*tearOff', 'FALSE')
    tab1 = converterUI(tabControl)
    # tab2 = ttk.Frame(tabControl)
    tab3 = databaseExtractorUI(tabControl)
    tabControl.add(tab1, text="Meldelisten-Konverter")
    # tabControl.add(tab2, text="PPC-Konverter")
    tabControl.add(tab3, text="FSM-Datenbank auslesen")
    tabControl.pack(expand=1, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()
