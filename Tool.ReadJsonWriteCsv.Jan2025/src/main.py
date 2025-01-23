from main_parameters import your_input_dirpath,    your_input_filename,    your_output_dirpath,    your_output_filename,    your_excel_column_headers,    your_excel_column_shortlist
from jgh_read_json_write_csv import read_json_write_csv, read_json_write_pretty_csv



# use either of these functions to read json files and convert them to csv files. choose whichever one you like

# print("")
# print("Testing the following: read_json_write_csv")
# print("")
read_json_write_csv(
    your_input_dirpath, 
    your_input_filename, 
    your_output_dirpath, 
    your_output_filename
)

# print("")
# print("Testing the following: read_json_write_pretty_csv")
# print("")
read_json_write_pretty_csv(
    your_input_dirpath,
    your_input_filename,
    your_output_dirpath,
    your_output_filename,
    your_excel_column_shortlist,
    your_excel_column_headers,
)

