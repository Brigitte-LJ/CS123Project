import csv
import pprint
import pdb
fall_24_path = "course.txt"
    
def make_prereq_dict(course_txt_path):
    """
    """
    prereq_dict = {}
    with open(course_txt_path, encoding="utf8") as file:
        data = file.read().replace('\n', ' ')
        courses = data.split("|#|")
        for course in courses:
            course = course.lower()
            if "prerequisite" in course:
                coursecode = course.split("|")[0][:-3] # remove campus code from end
                prereqs = course.split("prerequisite")[1]
                prereqs = clean_prereq_string(prereqs)
                prereq_dict[coursecode] = prereqs
            else:
                continue
    return prereq_dict

def clean_prereq_string(prereqs):
    if prereqs[:3] == "s: ": 
        prereqs = prereqs[3:]
    elif prereqs[:2] == ": ": 
        prereqs = prereqs[2:]
    elif prereqs[:4] == "(s) ": 
        prereqs = prereqs[4:]
    elif prereqs[:2] == "s:":
        prereqs = prereqs[2:]
    return prereqs