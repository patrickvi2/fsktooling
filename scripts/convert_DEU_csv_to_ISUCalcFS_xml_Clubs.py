import csv, codecs

csv_file_path = "DEU/clubs-DEU.csv"
xml_output_file_path_FSM = "DEU/clubs-DEU-FSM.xml"
xml_output_file_path_ISUCalcFS = "DEU/clubs-DEU.xml"

xml_content_FSM = "<Clubs>\n"
xml_content_ISUCalcFS = "<ISUCalcFS>\n"\
                        "  <Club_List>\n"

club_abbreviations = set()
err = False

with open(csv_file_path, 'r') as fi:
    r = csv.DictReader(fi, delimiter=';')
    for row in r:
        id = str(row['ID'])
        name = str(row['Name'])
        abbr = str(row['Abk.'])
        region = str(row['Region'])
        if abbr in club_abbreviations:
            print("Error: no unique club abbreviation")
            err = True
            break
        else:
            club_abbreviations.add(abbr)

        if '"' in name:
            name = name.replace('"', '\'')

        if '&' in name:
            name = name.replace('&', 'und')

        xml_content_FSM += "    <Club " \
                           "CLUB_NAME=\"" + name + "\" " \
                           "CLUB_SHORT_NAME=\"" + abbr + "\" />\n"

        xml_content_ISUCalcFS += "    <Person " \
                                 "PCT_ID=\"" + id + "\" " \
                                 "PCT_EXTDT=\"" + id + "\" " \
                                 "PCT_TYPE=\"CLU\" PCT_STAT=\"A\" " \
                                 "PCT_NAT=\"" + region + "\" " \
                                 "PCT_CNAME=\"" + name + "\" " \
                                 "PCT_SNAME=\"" + abbr + "\" " \
                                 "PCT_CSNAM=\"" + abbr + "\" " \
                                 "PCT_PLNAME=\"" + name + "\" " \
                                 "PCT_PSNAME=\"" + name + "\" " \
                                 "PCT_TLNAME=\"" + name + "\" " \
                                 "PCT_TSNAME=\"" + name + "\" " \
                                 "PCT_S1NAME=\"" + name + "\" " \
                                 "PCT_S2NAME=\"" + name + "\" " \
                                 "PCT_S3NAME=\"" + name + "\" " \
                                 "PCT_S4NAME=\"" + name + "\" " \
                                 "PCT_GENDER=\"M\" PCT_ACCSTA=\" \" PCT_COMPOF=\"a\" />\n"

if err:
    print("Errors while processing... No output files are generated.")
    exit(1)

xml_content_FSM += "</Clubs>\n"
xml_content_ISUCalcFS += "  </Club_List>\n" \
                      "</ISUCalcFS>\n"

with codecs.open(xml_output_file_path_FSM, 'w', 'utf-8') as fo:
    fo.write(xml_content_FSM)

with codecs.open(xml_output_file_path_ISUCalcFS, 'w', 'utf-8') as fo:
    fo.write(xml_content_ISUCalcFS)
