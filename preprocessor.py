import re
import pandas as pd
def preprocess(data):
  pattern= '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
  messages= re.split(pattern,data)[1:]
  dates=re.findall(pattern,data)
  df=pd.DataFrame({'user_message':messages,'message_date':dates})

  # Custom function to parse dates
  from datetime import datetime
  def parse_date(date_str):
    date_str = date_str.strip()  # Remove any leading/trailing whitespace
    for fmt in ('%m/%d/%y, %H:%M -','%d/%m/%y, %H:%M -'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"No valid date format found for {date_str}")

# Apply the custom function to the 'message_date' column
  df['message_date'] = df['message_date'].apply(parse_date)
  df['message_date'] = pd.to_datetime(df['message_date'])

# Convert the parsed dates to the desired format
  df['message_date'] = df['message_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
  df.rename(columns={'message_date':'date'},inplace=True)
  users=[]
  messages=[]
  for message in df['user_message']:
    entry=re.split('([\w\W]+?):\s',message)
    if entry[1:]:
        users.append(entry[1])
        messages.append(entry[2])
    else:
        users.append('group_notification')
        messages.append(entry[0])
  df['user']=users 
  df['message']=messages
  df.drop(columns=['user_message'],inplace=True)
  df['date'] = pd.to_datetime(df['date'])
  df['only_date'] = df['date'].dt.date
  df['year'] = df['date'].dt.year
  df['month_num'] = df['date'].dt.month
  df['month'] = df['date'].dt.month_name()
  df['day'] = df['date'].dt.day
  df['day_name'] = df['date'].dt.day_name()
  df['hour'] = df['date'].dt.hour
  df['minute'] = df['date'].dt.minute
  period = []
  for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

  df['period'] = period
  return df