# 05/2/2024 -- Version 1.0
import re
import pandas as pd
import requests
import warnings

# Function to check if a list is empty. If empty, the dataframe will contain a single row displaying "No results."
# Otherwise, the dataframe is created and populated with the corresponding list. 
def empty_list_check(list_name, df_name, df_num):
    if len(list_name) == 0:
        list_name.append("No results.")
    df_num[df_name] = pd.Series(list_name)

# Function to format the width of each column equal to the length of the longest string in each individual column.
def format_columns(df_num, sheet_name):
    for column in df_num:
        column_length = max(df_num[column].astype(str).map(len).max(), len(column))
        col_idx = df_num.columns.get_loc(column)
        writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)

# Function to remove brackets and "'" from a string.
def remove_brackets(list_string):
    return str(list_string).replace('[','').replace(']','').replace("'",'')

################################################## MAIN ##################################################
warnings.simplefilter(action='ignore', category=FutureWarning)

# Retrieve date from user to locate specific URL for that date, then go to URL and retrieve contents.
URL_date = input("Enter month and year in YYMM format (example: 2106 for June 2021).\nIf there are multiple lists within the same month,\nbe sure to also include the letter for the individual list you are interested in\n(such as 01a, 01b, or 01c for multiple lists in January):\n")
r = requests.get('https://classweb.org/approved/' + str(URL_date) + '.html')
contents = r.text

# Create empty lists
old_num_list = []           # list of old class numbers with captions that contain "CANCEL"
old_caption_list = []       # list of old captions that contain "CANCEL"
all_num_list = []           # list of all class numbers
all_cap_list = []           # list of all captions

# Go through file line-by-line, assigned to all_lines
all_lines = re.findall('.*', contents)

# Populate all_num_list and all_cap_list
for line in all_lines:
    # Locate ALL classification numbers first, and append to all_num_list
    all_num = re.findall('(?<=width="25%">)(.*?)(?=<)', line)
    all_num = remove_brackets(all_num)
    if(len(all_num)):
        all_num_list.append(all_num)
    # Locate ALL captions first, and append to all_cap_list
    temp_caption = re.findall('(?<=width="25%">)(.*?)(?=</tr>)', line)
    for caption in temp_caption:
        if(len(caption)):
            all_caption = re.findall('(?<=">)(.*?)(?=<)', caption)
            all_caption = remove_brackets(all_caption)
            all_cap_list.append(all_caption)

# Create a list of the most "final" cancelled classification numbers. These are numbers in parantheses (). 
# These need to be isolated because they contain the final "see ___" reference to the updated classification number.
cancelled_num_list = []     # list of cancelled classification numbers with ()
for num in all_num_list:
    index = all_num_list.index(num)
    caption = all_cap_list[index]
    if "(" in num and "CANCEL" not in caption:
        num = num.replace('(','').replace(')','')
        cancelled_num_list.append(num)

# Create a list of cancelled captions and a list of new classification numbers.
cancelled_cap_list = []     # list of cancelled captions
new_num_list = []           # list of updated classification numbers
for num in cancelled_num_list:                          # Go through each number in cancelled_num_list.
    num = "(" + num + ")"
    index = all_num_list.index(num)                     # Retrieve the index of that number as it appears in all_num_list.
    cancelled_cap = all_cap_list[index]                 # Use that index to find the caption associated with the old number.
    if "CANCEL" not in cancelled_cap:
        cancelled_cap_list.append(cancelled_cap)            # Add that caption to the list.
        while "see" not in all_cap_list[index]:             # Find the "see ____" line for the cancelled number 
            index=index+1                                   # by iterating through all_cap_list until "see" is found.
        new_num = all_cap_list[index]                       # Assign new_num to this line containing "see ____".
        new_num = re.findall('(?<=see )(.*)', new_num)      # Isolate the actual classification number after "see ____".
        new_num = remove_brackets(new_num)                  # Format the number and add it to the new_num_list.
        if "CANCEL" in new_num or "TABLE" in new_num:       
            new_num_list.append(new_num.split()[0])
        else:
            new_num_list.append(new_num)

# These lists are purely for informational purposes. They contain a list of ALL cancelled captions and numbers,
# not just those with new numbers/captions. 

all_cancelled_nums = []         # List of all cancelled classification numbers
all_cancelled_caps = []         # List of all cancelled captions
referenced_num_list = []        # List of messages to display
contains_reference = []         # List of Y/N to whether or not cancelled number contains a reference already listed in first sheet
for cap in all_cap_list:        # Iterate through all captions, looking for captions that contain the word "CANCEL"
    if "CANCEL" in cap:
        index = all_cap_list.index(cap)
        num = all_num_list[index] 
        if "&nbsp;" not in num:
            all_cancelled_caps.append(cap)
            if "(" in num:
                num = num.replace('(','').replace(')','')
            all_cancelled_nums.append(num)
            if num in cancelled_num_list:
                referenced_num_list.append(num)
                contains_reference.append("Yes")
            else:
                if "see" in cap:
                    num = re.findall('(?<=see )(.*)(?= CANCEL)', cap)
                    num = remove_brackets(num)
                    if num in cancelled_num_list:
                        referenced_num_list.append(num)
                        contains_reference.append("Yes")
                    else:
                        referenced_num_list.append(num)
                        contains_reference.append("Yes, but new reference not in current list")
                else:
                    referenced_num_list.append(num)
                    contains_reference.append("No, final cancellation")

# Create a list of new captions using the list of new classification numbers.
new_cap_list = []
for num in new_num_list:
    if num not in all_num_list:                         # If the number doesn't appear in all_num_list, then the caption isn't here.
        new_cap_list.append("New caption not found on this page.") 
    else:                       
        index = all_num_list.index(num)                 # Locate the index of the new number as it appears in all_num_list.
        new_cap = all_cap_list[index]                   # Assign new_cap to the caption associated with that index in all_cap_list.
        if ("CANCEL" in new_cap) and (num == (all_num_list[index+1])):
            new_cap = all_cap_list[index+1]             # If "CANCEL" is in the line, keep iterating until it doesn't appear.
        elif (new_cap.startswith("For") or new_cap.startswith("Cf.")) and "see" not in new_cap:
            new_cap = all_cap_list[index+1]
        elif "see" in new_cap:
            num = re.findall('(?<=see )(.*)', new_cap)
            num = remove_brackets(num)
        new_cap_list.append(new_cap)             

# Create dataframes
df1 = pd.DataFrame()
empty_list_check(cancelled_num_list, "Old Class Number", df1)
empty_list_check(cancelled_cap_list, "Old Caption", df1)
empty_list_check(new_num_list, "New Class Number", df1)
empty_list_check(new_cap_list, "New Caption", df1)

df2 = pd.DataFrame()
empty_list_check(all_cancelled_nums, "All Cancelled Class Numbers", df2)
empty_list_check(all_cancelled_caps, "All Cancelled Captions", df2)
empty_list_check(referenced_num_list, "Referenced Class Number", df2)
empty_list_check(contains_reference, "Listed in Cutter Sheet?", df2)

df3 = pd.DataFrame()
empty_list_check(all_num_list, "All Class Numbers", df3)
empty_list_check(all_cap_list, "All Captions", df3)
df3 = df3[df3["All Class Numbers"] != "&nbsp;"]

# Write to spreadsheet with column width set to longest caption name
writer = pd.ExcelWriter('~/Desktop/cutter-list-' + str(URL_date) + '.xlsx') 

df1.to_excel(writer, sheet_name='Classification Number Changes', index=False, na_rep='NaN')
format_columns(df1, 'Classification Number Changes')
df2.to_excel(writer, sheet_name='All Cancels', index=False, na_rep='NaN')
format_columns(df2, 'All Cancels')
df3.to_excel(writer, sheet_name='Complete List', index=False, na_rep='NaN')
format_columns(df3, 'Complete List')

writer.close()
