from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import arrow  # Arrow is used internally by the ics library

def convert_date_format(date_str):
    return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')

def convert_to_utc(date_str, time_str):
    # Combine date and time, assume Singapore Time (UTC+8)
    local_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
    # Convert to UTC by subtracting 8 hours
    utc_time = local_time - timedelta(hours=8)
    return utc_time

# Function to extract event data from HTML
def extract_event_data(soup):
    events = []
    
    # Find all module sections by their unique header class
    module_sections = soup.find_all('table', class_='PSGROUPBOXWBO')

    for module_section in module_sections:
        # Get the module title from the header
        header_title = module_section.find('td', class_='PAGROUPDIVIDER').get_text(strip=True)

        # Find all rows corresponding to the class schedule within this module
        rows = module_section.select('tr[id^="trCLASS_MTG_VW$"]')

        # Track previous values for reuse
        previous_class_number = None
        previous_section = None
        previous_component = None

        for row in rows:
            columns = row.find_all('td')
            if columns:
                class_number = columns[0].get_text(strip=True) or previous_class_number
                section = columns[1].get_text(strip=True) or previous_section
                component = columns[2].get_text(strip=True) or previous_component
                days_times = columns[3].get_text(strip=True)
                room = columns[4].get_text(strip=True)
                instructor = columns[5].get_text(strip=True)
                date_range = columns[6].get_text(strip=True)
                
                # Extract date and time info
                start_date, end_date = date_range.split(' - ')
                day, start_time, _, end_time = days_times.split(' ')
                start_date = convert_date_format(start_date)
                end_date = convert_date_format(end_date)

                # Convert times to UTC
                start_datetime_utc = convert_to_utc(start_date, start_time)
                end_datetime_utc = convert_to_utc(end_date, end_time)

                # Store current values for reuse in case the next row is missing them
                previous_class_number = class_number
                previous_section = section
                previous_component = component

                # Create event dictionary
                event = {
                    'title': header_title,
                    'class_number': class_number,
                    'section': section,
                    'lection-type': component,
                    'days': day,
                    'start_time': start_datetime_utc,
                    'end_time': end_datetime_utc,
                    'room': room,
                    'instructor': instructor
                }
                events.append(event)
    
    return events

# Function to create ICS file from extracted data
def create_ics_file(events, output_file):
    cal = Calendar()

    for event in events:
        e = Event()
        # Use the header title for the event name and combine it with the lection-type/component and section
        e.name = f"{event['title']} - {event['lection-type']} {event['section']}"
        e.begin = arrow.get(event['start_time']).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        e.end = arrow.get(event['end_time']).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        e.location = event['room']
        e.description = f"Instructor: {event['instructor']}\nClass Number: {event['class_number']}\nLection-Type: {event['lection-type']}"
        cal.events.add(e)

    with open(output_file, 'w') as f:
        f.writelines(cal)

# Example Usage
html_file = 'table.html'  # The HTML file containing your calendar data
output_file = 'events.ics'   # The ICS file to be generated

with open(html_file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

events = extract_event_data(soup)
create_ics_file(events, output_file)
print(f"ICS file {output_file} created successfully!")


class_titles = [event['title'] for event in events]
class_counts = {title: class_titles.count(title) for title in set(class_titles)}

for title, count in class_counts.items():
    print(f"{title}: {count} occurrences")
