# in4SIT to ICS

A python script to convert your online in4sit timetable to a ics file which you can then import to you preffered calendar app.

## Preparations

<code>pip install -r requirements.txt</code>

## Usage

1. go to in4sit
2. go to course management and click on "My weekly schedule"
3. click on list view
4. now press F12 or right click and click on "inspect" or "inspect this page" (normally at the very bottom)
5. in the newly opened window, click on the "arrow in a box" symbol (its called "select an item on the page to inspect")
6. select the "table" element which includes all modules (id=ACE_width)
7. copy the element as html content and paste it into the table.html file
8. run the python scrit <code>python3 in4sit-to-ics.py </code>
9. if all worked you can now use the .ics file to import the lessons to you preferred calendar