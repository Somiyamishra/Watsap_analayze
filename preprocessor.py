import re
import pandas as pd

def preprocess(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2})'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Adjust length mismatch
    if len(dates) != len(messages[1::2]):
        min_length = min(len(dates), len(messages[1::2]))
        dates = dates[:min_length]
        messages = messages[:min_length * 2]

    df = pd.DataFrame({'message_date': dates, 'user_message': messages[1::2]})
    df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %H:%M', errors='coerce')

    df['user'] = df['user_message'].str.extract(r'([\w\W]+?):\s', expand=True)
    df['message'] = df['user_message'].str.replace(r'^[\w\W]+?:\s', '', regex=True)
    df['user'] = df['user'].fillna('group_notification')
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df
