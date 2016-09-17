import csv
from PIL import Image, ImageFont, ImageDraw
import re
import requests

COORDINATES = [[]]
# changes master schedule into list of lists
with open('MasterScheduleF16.csv', 'r') as f:
	reader = csv.reader(f)
	master_list = list(reader)
	for x in master_list:
		try:
			y = int(x[1])
			if int(x[3]) > 7:
				master_list.remove(x)
		except ValueError:
			master_list.remove(x)


# takes in course name and section number and returns a class in the master schedule
def class_search(course_name, section_number):
	print(course_name, section_number, master_list[1])
	for x in master_list:
		if course_name in x[0] and str(int(section_number)) in x[1]:
			return x
	raise ValueError("Can't find course.")

def meeting_times(course):
	times = []
	days = course[4]
	if '+' in course[3]:
		periods = [int(x) for x in course[3].split('+')]
	else:
		periods = [int(course[3])]
	print(periods, course[3], course)
	periods_to_special_timeslots = {
		1 : 1,
		2 : 3,
		3 : 2,
		4 : 5,
		5 : 7,
		6 : 9,
		7 : 6
	}
	periods_to_timeslots = {
		1 : 1,
		2 : 2,
		3 : 4,
		4 : 5,
		5 : 6,
		6 : 7,
		7 : 8
	}
	for period in periods:
		modified_days = days
		if modified_days[0] == 'M':
			times.append((1, periods_to_timeslots[period]))
			modified_days = modified_days[1:]
		if modified_days[0] == 'T' and modified_days[1] != 'h':
			times.append((2, periods_to_timeslots[period]))
			modified_days = modified_days[1:]
		if modified_days[0] == 'W':
			times.append((3, periods_to_special_timeslots[period]))
			if modified_days[1] == 'e':
				times.append((3, periods_to_special_timeslots[period] + 1))
				modified_days = modified_days[5:]
			else:
				modified_days = modified_days[1:]
		if modified_days[:2] == 'Th':
			times.append((4, periods_to_special_timeslots[period]))
			if modified_days[2] == 'e':
				times.append((4, periods_to_special_timeslots[period] + 1))
				modified_days = modified_days[6:]
			else:
				modified_days = modified_days[2:]
		if len(modified_days) >= 1 and modified_days[0] == 'F':
			times.append((5, periods_to_timeslots[period]))
			modified_days = modified_days[1:]		
	return times

def print_class(course, img):
	font = ImageFont.truetype("DroidSans-Bold.ttf", 13)
	course_name = course[0].split(':')[0] + '/' + course[1]
	draw = ImageDraw.Draw(img)
	days_to_xs = {
		1 : 35,
		2 : 189,
		3 : 343,
		4 : 491,
		5 : 632,
	}
	periods_to_ys = {
		1 : 199,
		2 : 280,
		3 : 371,
		4 : 454,
		5 : 540,
		6 : 624,
		7 : 710,
		8 : 792,
		9 : 875,
		10 : 958
	}
	for x, y in meeting_times(course):
		print(x, y)
		if y == 10:
			draw.text((days_to_xs[x], 958), course_name, font = font, fill = (0, 0, 0))
			draw.text((days_to_xs[x], 967), course[2], font = font, fill = (0, 0, 0))
			draw.text((days_to_xs[x], 980), course[5], font = font, fill = (0, 0, 0))
		else:
			draw.text((days_to_xs[x], periods_to_ys[y]), '\n'.join([course_name, course[2], course[5]]), font = font, fill = (0, 0, 0))

def iCal_to_Courses(url):
	r = requests.get(url)
	text = r.text
	lines = text.split('\r\n')
	activities = []
	for x in lines:
		if '2016-17T1' in x:
			activities.append(x)
	activities = list(set(activities))
	courses = activities[:]
	for x in activities:
		if 'SUMMARY:ASM' in x:
			courses.remove(x)
		elif 'SUMMARY:ATH' in x:
			courses.remove(x)
		elif 'SUMMARY:WD' in x:
			courses.remove(x)
		elif 'NON-CREDIT Private Lessons' in x:
			courses.remove(x)
		elif 'SUMMARY:ADV' in x:
			courses.remove(x)
	course_name_section = []
	for x in courses:
		course_name_section.append((x[8:14], x[26:28]))
	return course_name_section


def final_schedule(url):
	courses = iCal_to_Courses(url)
	print(courses)
	img = Image.open("NewBlankSchedule.png")
	for x, y in courses:
		print_class(class_search(x, y), img)
	img.save('Jungwoo_Schedule.png')
	img.show()
# final_schedule("https://unify-ext.andover.edu/extranet/Student/OpenCalendar?key=Hm60oiTt8C43LQFmJrTE6A%3D%3D&langue=US")
final_schedule("https://unify-ext.andover.edu/extranet/Student/OpenCalendar?key=8mrVFC5z54AhIIUOnJ%2B%2BxQ%3D%3D&langue=US")
# final_schedule([("PHD200", '1'), ("CHM610", '2'), ("ENG200", '12'), ("SPA300", '5'), ("MTH650", '3'),])
#final_schedule([('CHM550', '1'), ('CHI420', '1'), ('PHR300', '1'), ('CSC450', '1'), ('ENG200', '12'), ('MTH360', '2'), ('Lunch', '6')])
# final_schedule("https://unify-ext.andover.edu/extranet/Student/OpenCalendar?key=2EEUHz3FSCAuPcGKkY8UeA%3D%3D&langue=US")