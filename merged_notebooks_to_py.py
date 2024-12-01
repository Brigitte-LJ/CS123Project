import csv
import json
import mmap
import re

### GLOBAL VARIABLES ###

# CSV files may be downloaded from the README.md file.
coreCSVpath = "Core_Requirements_CS_123.csv"
majorCSVpath = "CS_Major_Requirements_CS_123.csv"
hsaCSVpath = "HSA_Requirements_CS_123.csv"

# We will use this dictionary to store and update our requirement data.
# It is initialized as blank, and is populated by calling defineReqsDict().
totalReqsDict = {
    "core": None,
    "major": None,
    "hsa": None,
    "coreDone": [],
    "coreToDo": [],
    "majorDone": [],
    "majorToDo": [],
    "hsaDone": [],
    "hsaToDo": []
}

# TODO: should be a dictionary for each major?
numTechElectives = 3 # how many tech electives are required?

### SAMPLE DATA ###
inputCourses = [
    "CSCI005",
    "CSCI060",
    "MATH019",
    "WRIT001",
    "PHYS023"
    ]

############### TUTORIAL SECTION 1 ###############

def csvToLoL(csvpath):
  """ input: file path to a CSV of course requirements, CSV formatted as shown below
              major	techel	coursecode	sublist
              CSCI  n       CSCI070     2
              CSCI  y       MATH164     3

      output: a list of lists, such that one course in each sublist must be taken
            example: [["CSCI042, "CSCI060"], ["CSCI070]]]
            indicates requirement of (CS 42 OR CS 60) AND CS 70
  """
  reqs = []
  with open(csvpath) as f:
    reader = csv.reader(f)
    next(reader)
    i=0
    nonTechElectives = []
    techElectives = []
    for row in reader:
      coursecode = row[0]
      if row[2] == "y": # tech elective case
        techElectives.append(coursecode)
      else:
        if int(row[-2])==i: # our CSV data is a string, and "0" =/= 0
          nonTechElectives.append(coursecode)
        else:
          reqs.append(nonTechElectives)
          nonTechElectives = []
          nonTechElectives.append(coursecode)
          i += 1
    for i in range(numTechElectives):
      reqs.append(techElectives) # deal with Tech Electives last
    return reqs

def defineReqsDict(reqsDict):
    """ input: n/a
        output: populates totalReqsDict with area requirements,
                area courses Done, and area courses To Do
    """
    reqsDict["core"] = csvToLoL(coreCSVpath)
    reqsDict["major"] = csvToLoL(majorCSVpath)
    reqsDict["hsa"] = csvToLoL(hsaCSVpath)
    return reqsDict

def checkAreaReqsMet(reqsDict, inputList, area):
    """ inputs: reqsDict is the ongoing tally of requirements
                area is "hsa", "major", or "core"
                inputList is a flat list of strings containing course codes
        outputs:updates the corresponding areaCoursesDone and 
                areaCoursesToDo lists
    """
    areaReqsList = reqsDict[area]
    for subset in areaReqsList:
        met = any(course in subset for course in inputList)
        if met:
            reqsDict[f"{area}Done"].append(subset)
        else: 
            reqsDict[f"{area}ToDo"].append(subset)
    return reqsDict

def checkTotalReqsMet(reqsDict, inputList):
    """ takes in and updates reqsDict
    """
    reqsDict = checkAreaReqsMet(reqsDict, inputList, "core")
    reqsDict = checkAreaReqsMet(reqsDict, inputList, "major")
    reqsDict = checkAreaReqsMet(reqsDict, inputList, "hsa")
    return reqsDict


def sample_run_1():
   """ like main, but I don't necessarily want to call every time I run the file"""
   global totalReqsDict
   totalReqsDict = defineReqsDict(totalReqsDict)
   totalReqsDict = checkTotalReqsMet(totalReqsDict, inputCourses)
   print("Core Courses Done is", totalReqsDict["coreDone"])
   print("Core Courses ToDo is", totalReqsDict["coreToDo"])
   print("Major Courses Done is", totalReqsDict["majorDone"])
   print("Major Courses ToDo is", totalReqsDict["majorToDo"])
   print("HSA Courses Done is", totalReqsDict["hsaDone"])
   print("HSA Courses ToDo is", totalReqsDict["hsaToDo"])

      

############## TUTORIAL SECTION 2 ################

# Returns a list of all available courses in course-area.json with specified area
def filterByArea(area):
  """ TODO: ADD DOCSTRING HERE
  """
  with open("course-area.json", 'r') as file: # Open the JSON file
      course_data = json.load(file)  # Load the JSON data from the file into list

  output = []
  for course in course_data:  # Print all courses that have the attribute of area
    if area in set(course["course_areas"]):
      courseOnly = course["course_code"][:-2].strip() # Remove campus signature & whitespaces
      output.append(courseOnly) # add course into final list
  return output # return list of all courses in parameter area.

# Takes in an array of already taken course codes
# Returns a dictionary containing only the taken course 
# tagged with HSAs and their corresponding credit value
#    # ex) input = ["HIST055  CM", "CSCI140  HM", "ART 005  PO", "DANC051  PO", "ART 060  HM", 
#                   "MUS 175 JM", "MUS 175 JM"]
#    # output = {'HIST055  CM': '1.0', 'ART 005  PO': '1.0', 'DANC051  PO': '0.5', 
#                'ART 060  HM': 0.5, 'MUS 175 JM': 1.0}
# parameter muddHumTrue can be set as True to get an output consisting only of courses tagged 
# as mudd hums, False otherwise
def tidyHSA(coursesDone, muddHumTrue):
    with open("course-area.json", 'r') as file: # Open the JSON file containing area data
        courseArea = json.load(file)
    
    with open("course-section.json", 'r') as file: # Open the JSON file containing credit data
        courseSection = json.load(file)
    
    HSAcredits = {} # initialize empty final returned dictionary
    allTakenData = [] # initialize empty list storing taken courses & area data immediately below
    tempList = [] # initialize empty tempList used to store filtered data temporarily
    
    # Filter through courseArea for taken courses
    # Add taken courses and their corresponding area data into allTakenData
    for course in coursesDone:
        allTakenData.extend(list(filter(lambda x: x["course_code"] == course, courseArea)))
   
    # Filter through allTakenData
    # Add only courses which are tagged with HSAs into HSAcredits as keys with empty values
    if (muddHumTrue): # include only mudd hums with the tag 4HSA
        for taken in allTakenData:
            if ('4HSA' in taken["course_areas"]):
                tempList.append(taken)
        allTakenData = tempList
    else: # include only HSAs with either the tag 4HSS or 4HSA or both
        for taken in allTakenData:
            if ('4HSS' in taken["course_areas"]) or ('4HSA' in taken["course_areas"]):
                tempList.append(taken)
        allTakenData = tempList

    
    # For each HSA taken, find and set its credit amount as the value corresponding to
    # its course code in a key-value pair within the HSAcredits dictionary
    for taken in allTakenData:
        for course in courseSection:
            if (taken["course_code"] in course["courseSectionId"]):
                if (taken["course_code"] in HSAcredits): # same course taken more than once 
                    HSAcredits.update({taken["course_code"]: (HSAcredits[taken["course_code"]] 
                    + float(course["creditHours"]))}) # increment credit amount on the same key
                else: 
                    HSAcredits.update({taken["course_code"]: float(course["creditHours"])})
    
    # If the HSA taken is at Mudd, convert its credit value to the 5C credit value
    # i.e. Divide all mudd credits by 3.
    for HSA in HSAcredits:
        if ("HM" not in HSA):
            HSAcredits[HSA] =  float(HSAcredits[HSA]) * 3.0
    
    # Special case where Mudd students need 3 semester for one full course of MUS 175 
    # while other students need only 2 semesters for one full course (This tutorial is 
    # specified toward mudd students)
    if ('MUS 175  JM' in HSAcredits):
        HSAcredits['MUS 175  JM'] = (2 * HSAcredits['MUS 175  JM']) / 3
        
        
    return HSAcredits

# Takes in an array of already taken course codes
# Returns true if breadth is fulfilled, false if otherwise.
# Breadth is fulfilled if there are at least 5 full courses taken in 5 different areas. 
# (a full course is 1.0 cr (assuming mudd is converted))

def checkBreadth(niceHSAs):
    uniqueArea = {}

    for HSA in niceHSAs:
        if HSA[0:4] not in uniqueArea:
            uniqueArea[HSA[0:4]] = float(niceHSAs[HSA])
        else:
            uniqueArea[HSA[0:4]] += float(niceHSAs[HSA])
    fullCourse = 0
    for credit in uniqueArea.values():
        if credit >= 1.0:
            fullCourse += 1

    return (fullCourse >= 5) # There are at least 5 full courses taken in 5 unique areas

# Takes in an array of already taken course codes
# Returns true if depth is fulfilled, false if otherwise.
# Depth is fulfilled if there are at least 4 full courses taken in one areas. 
# (a full course is 1.0 cr (assuming mudd is converted))
def checkDepth(niceHSAs):
    uniqueArea = {}
    
    for HSA in niceHSAs:
        if HSA[0:4] not in uniqueArea:
            uniqueArea[HSA[0:4]] = float(niceHSAs[HSA])
        else:
            uniqueArea[HSA[0:4]] += float(niceHSAs[HSA])
    print("Concentration:", max(uniqueArea, key=uniqueArea.get)) # optional, print the area that the student currently has the most credits completed for(i.e. most likely concentration).
    return (max(uniqueArea.values()) >= 4.0) # there are at least 4.0 credits earned in one area
                                             # (indicating four full courses with the 5C 1.0 scale)

# Creates a global dictionary prereqDict containing all course codes as keys and their 
# corresponding prereqs as values
def prereqsToDict():
    global prerequisite_dict # Define a global variable 
    prerequisite_dict = {}
    with open('course.txt', 'r') as f:
        # memory-map the file
        mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        # split the file by |#|, which signify a new course following the symbol |#|
        courses = mmapped_file.read().decode("utf-8").split("|#|") # Creates a list separated by course
    
    courseCodePattern = r"^(.*?)\|\^\|" # use regex to find course code at the beginning of each course string
    prereqPattern = r"Prerequisite.*" # use regex to find the phrase "prerequisite" in the course description 
                                # and grab all from "prerequisite" until the end of the string.
    for course in courses: 
        matchCode = re.search(courseCodePattern, course)
        matchPrereq = re.search(prereqPattern, course, re.IGNORECASE)
        if matchCode and matchPrereq:
            prerequisite_dict.update({matchCode.group(1): matchPrereq.group(0)}) # stores course code as key, course description as value

# Searches the global dictionary prereqDict to find the parameter courseCode and returns its 
# corresponding key (prerequisites).
def checkPrereqFor(courseCode):
    return prerequisite_dict.get(courseCode)

# Return true if there are at least 4 full Mudd Hums taken(12 HM credits/4 5C credits), 
# else, return false
def checkMuddHums(coursesDone):
    muddHums = tidyHSA(coursesDone, True) # Call tidyHSA with the special parameter 
                                          # muddHumTrue = True to get a dictionary 
                                          # of {coursecode:credit} excluding non-mudd hums
    creditSum = 0
    
    for credit in muddHums.values():
        creditSum += float(credit) # sum up all credits earned from mudd hums
    
    print(muddHums) # optional, print all taken mudd hums
    print(creditSum) # optional, print credit sum of all taken mudd hums so far
    return (creditSum >= 12) 

#--# Function calls: #--#

## Define Example List of Taken Courses ##
# done = ["HIST055  CM", "CSCI140  HM", "DANC051  PO", "ANTH190  SC", "ASIA190  PO", 
# "DANC010  PO", "DANC122  PO", "DANC124  PO", "AMST179A HM", "ARCT179A HM", "ART 179S HM", 
# "MUS 175  JM", "MUS 175  JM"]

## Test tidyHSA ##
# niceHSAs = tidyHSA(done, False) # Returns a list of HSAs and their credits
# print(niceHSAs)

## Test checkBreadth & checkDepth ##
# print("Breadth fulfilled:" , checkBreadth(niceHSAs))
# print("Depth(Concentration) fulfilled:" , checkDepth(niceHSAs))

## Test checkMuddHums ##
# print(checkMuddHums(done)) # Returns a list of Mudd HSAs and their credits

## Test prereqsToDict & checkPrereqFor ##
# prereqsToDict()  # only needs to be ran once. (creates a global variable)
# print(checkPrereqFor("PHYS042 LPO"))

############## TUTORIAL SECTION 3 ########################
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from IPython.display import display



coreItemsDone = [widgets.Label(str(i)) for i in totalReqsDict["coreDone"]]
HSAItemsDone = [widgets.Label(str(i)) for i in totalReqsDict["hsaDone"]]
majorItemsDone = [widgets.Label(str(i)) for i in totalReqsDict["majorDone"]]
tab_contents = [widgets.GridBox(coreItemsDone, layout=widgets.Layout(grid_template_columns="repeat(1, 200px)")), 
                widgets.GridBox(majorItemsDone, layout=widgets.Layout(grid_template_columns="repeat(1, 200px)")), 
                widgets.GridBox(HSAItemsDone, layout=widgets.Layout(grid_template_columns="repeat(1, 200px)"))]
#children = [widgets.Text(description=name) for name in tab_contents]
tab = widgets.Tab()
tab.children = tab_contents
tab.titles = ["Core To Do", "Major To Do", "HSA To Do"]
#tab




courseTextBox = widgets.Text(    
    value='',
    placeholder='Add a course',
    description='Course List:',
    disabled=False    
)

addCourseButton = widgets.Button(description='Enter Course',
    disabled=False,
    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click me')

output = widgets.Output()
output2 = widgets.Output()

removeCourseButton = widgets.Button(
   description="Remove",
   disabled=False,
   button_style="danger"
)

def on_add_clicked(b):
    if courseTextBox.value != '':
        inputCourses.append(courseTextBox.value)
    output.clear_output()
    with output:
        print("Course List:", inputCourses)

def on_remove_click(b):
   inputCourses.remove(inputCourses[-1])
   output.clear_output()
   with output:
      print("Course List:", inputCourses)

addCourseButton.on_click(on_add_clicked)
removeCourseButton.on_click(on_remove_click)

updateReqButton = widgets.Button(
   description="Update Requirements",
   disabled=False,
   button_style="info"
)

def on_update_clicked(b):
   checkTotalReqsMet(totalReqsDict, inputCourses)
   output2.clear_output()
   with output2:
    print(totalReqsDict["coreToDo"])
      

updateReqButton.on_click(on_update_clicked)


widgets.VBox([courseTextBox,
              widgets.HBox([addCourseButton, removeCourseButton]), 
              output, 
              updateReqButton,
              output2])