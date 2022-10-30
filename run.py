# run.py
# Suraj Rampure (rampure@ucsd.edu)

import pandas as pd
import numpy as np
import json
import os
import warnings
warnings.simplefilter('ignore')

with open('config.json', 'r') as f:
    config = json.load(f)

seccode_to_secid = {config['sections'][x]['seccode']: x for x in config['sections']}

# Requires a combined roster
def process_roster(roster_path, swaps_path=None, exclude_path=None):
    # pd.read_excel doesn't seem to like the blink roster files, 
    # but they're not too hard to parse manually
    with open(roster_path, 'r') as f:
        roster_str = f.readlines()
    roster_df = pd.DataFrame(map(lambda s: s.split('\t'), roster_str[6:]))
    roster_df.columns = roster_df.iloc[0]
    roster_df = roster_df.iloc[1:]
    roster_df['Email'] = roster_df['Email\n']
    roster_df['Email'] = roster_df['Email'].str.strip('\n')
    roster_df = roster_df.drop(columns='Email\n')[['Sec ID', 'PID', 'Student', 'Email']]

    # Process swaps
    # An "swap" is when a student takes an exam in a different section than they're enrolled in
    if swaps_path:
        swaps = pd.read_csv(swaps_path).set_index('PID')
        for pid, row in swaps.iterrows():
            new_sec_id = seccode_to_secid[row['New']]
            roster_df.loc[roster_df['PID'] == pid, 'Sec ID'] = new_sec_id
            print(row['Name'], 'switched from', seccode_to_secid[row['Original']], 'to', seccode_to_secid[row['New']])

    # We exclude students who are taking the exam in separate rooms for OSD reasons
    if exclude_path:
        exclude = pd.read_csv(exclude_path)['PID'].values

        for pid in exclude:
            if pid not in roster_df['PID'].values:
                print(pid, 'not in roster')

        roster_df = roster_df[~roster_df['PID'].isin(exclude)]

    return roster_df

def process_chart(chart_path, room_name):
    chart_df = pd.read_excel(chart_path)
    chart_df = chart_df.iloc[13:, [7, 2]]
    chart_df.columns = ['seat', 'left']
    chart_df['left'] = chart_df['left'] == 'YES'
    chart_df['room'] = room_name
    return chart_df[['room', 'seat', 'left']]

def create_assignments(section_df, chart_df):
    seed = config['seed']
    np.random.seed(seed)
    
    section_df = section_df.copy()
    chart_df = chart_df.copy()

    # To make sure people aren't assigned to left-handed desks
    # Not always possible
    if (~chart_df['left']).sum() >= section_df.shape[0]:
        chart_df = chart_df[~chart_df['left']]
        
    chart_df = chart_df.sample(frac=1).reset_index(drop=True)
    section_df = section_df.sample(frac=1).reset_index(drop=True)
    
    together = pd.concat([chart_df, section_df], axis=1).iloc[:section_df.shape[0]]
    return together

def process_section(section):
    # get section's information
    section_dict = config['sections'][section]
    
    seccode = section_dict['seccode'] # standard name for section, e.g. "A00"
    room_name = section_dict['room']
    chart_path = section_dict['chart_path']
    
    # process section's chart
    chart_df = process_chart(chart_path, room_name)
    
    # get only the students in this section in the roster
    section_df = roster_df[roster_df['Sec ID'] == section]
        
    # run and return assignments
    section_assignments_df = create_assignments(section_df, chart_df)
    section_assignments_df['Sec ID'] = seccode
    return section_assignments_df

def write_sheets(assignments_df, for_mailing=True, for_posting=True):
    assignments_df = assignments_df[['Sec ID', 'room', 'seat', 'PID', 'Email', 'Student']]

    if not os.path.exists('exports'):
        os.mkdir('exports')

    exports_path = os.path.join("exports", config['exports'])
    if not os.path.exists(exports_path):
        os.mkdir(exports_path)

    if for_mailing:
        save_path = os.path.join(exports_path, 'seating-for-mailing.csv')
        assignments_df.to_csv(save_path, index=False)

    if for_posting:
        save_path = os.path.join(exports_path, 'seating-for-posting.csv')
        assignments_df.drop(columns=['Email', 'Student']).to_csv(save_path, index=False)


if __name__ == '__main__':
    roster_path = config['roster']
    swaps_path = config['swaps'] if 'swaps' in config.keys() else None
    exclude_path = config['exclude'] if 'exclude' in config.keys() else None
    roster_df = process_roster(roster_path, swaps_path, exclude_path)
    assignments_lst = []

    for section in config['sections']:
        assignments_lst.append(process_section(section))

    assignments_df = pd.concat(assignments_lst)
    write_sheets(assignments_df)