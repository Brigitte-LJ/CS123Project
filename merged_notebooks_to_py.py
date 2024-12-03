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
    "core": ["PHYS023", "PHYS024", "CSCI005", "WRIT001", "HSA10", "PE001"],
    "major": ["CSCI0060", "CSCI0070", "MATH072"],
    "hsa": ["BREADTH001", "BREADTH002", "DEPTH01"],
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
inputCourses = []

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
    reqsDict[f"{area}Done"] = []
    reqsDict[f"{area}ToDo"] = []
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

#sample_run_1()

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

# Define Example List of Taken Courses ##
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


#defining our Outputs, which are the way IPyWidgets can best display and interact with text
outputCourseList = widgets.Output()
outputReqsListTotal = widgets.Output()
outputCoreList = widgets.Output()
outputMajorList = widgets.Output()
outputHSAList = widgets.Output()
outputSemesters = widgets.Output()


#Creating our text boxes
courseTextBox = widgets.Text(    
    value='',
    placeholder='Add a course',
    description='Course List:',
    disabled=False    
)

#Creating our buttons
addCourseButton = widgets.Button(description='Enter Course',
    disabled=False,
    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click me')


removeCourseButton = widgets.Button(
    description="Remove Course",
    disabled=False,
    button_style="danger"
)

updateReqButton = widgets.Button(
   description="Update!",
   disabled=False,
   button_style="info"
)

#defining our interaction functions
def on_add_clicked(b):
    if courseTextBox.value != '':
        inputCourses.append(courseTextBox.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)

def on_remove_click(b):
    if inputCourses != []: 
        for i in [semester1, semester2, semester3, semester4, semester5, semester6, semester7, semester8]:
            if inputCourses[-1] in i:
                i.remove(inputCourses[-1])
        inputCourses.remove(inputCourses[-1])
    outputCourseList.clear_output()
    outputSemester1.clear_output()
    outputSemester2.clear_output()
    outputSemester3.clear_output()
    outputSemester4.clear_output()
    outputSemester5.clear_output()
    outputSemester6.clear_output()
    outputSemester7.clear_output()
    outputSemester8.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    with outputSemester1:
        print('Courses in Semester 1:', semester1)
    with outputSemester2:
        print('Courses in Semester 2:', semester2)
    with outputSemester3:
        print('Courses in Semester 3:', semester3)
    with outputSemester4:
        print('Courses in Semester 4:', semester4)
    with outputSemester5:
        print('Courses in Semester 5:', semester5)
    with outputSemester6:
        print('Courses in Semester 6:', semester6)
    with outputSemester7:
        print('Courses in Semester 7:', semester7)
    with outputSemester8:
        print('Courses in Semester 8:', semester8)


def on_update_clicked(b):
    updatedReqsDict = checkTotalReqsMet(totalReqsDict, inputCourses)  
    outputReqsListTotal.clear_output()
    outputCoreList.clear_output()
    outputMajorList.clear_output()
    outputHSAList.clear_output()
    coreItemsDone = [widgets.Label(value=f"{i}") for i in updatedReqsDict["coreDone"]]
    HSAItemsDone = [widgets.Label(str(i)) for i in updatedReqsDict["hsaDone"]]
    majorItemsDone = [widgets.Label(str(i)) for i in updatedReqsDict["majorDone"]]    
    coreItemsToDo = [widgets.Label(value=f"{i}") for i in updatedReqsDict["coreToDo"]]
    HSAItemsToDo = [widgets.Label(str(i)) for i in updatedReqsDict["hsaToDo"]]
    majorItemsToDo = [widgets.Label(str(i)) for i in updatedReqsDict["majorToDo"]]    
    with outputReqsListTotal:
        print("Core Remaining: ", updatedReqsDict["coreToDo"])
        print("Major Remaining: ", updatedReqsDict["majorToDo"])
        print("HSA Remaining: ", updatedReqsDict["hsaToDo"])
    with outputCoreList:
        labels = [widgets.Label(value="Core Done"), widgets.Label(value="Core To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        #print(updatedReqsDict)
        display(widgets.GridBox([widgets.VBox(coreItemsDone), widgets.VBox(coreItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))
    with outputMajorList:
        labels = [widgets.Label(value="Major Requirements Done"), widgets.Label(value="Major Requirements To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        #print(updatedReqsDict)
        display(widgets.GridBox([widgets.VBox(majorItemsDone), widgets.VBox(majorItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))
    with outputHSAList:
        labels = [widgets.Label(value="HSA Requirements Done"), widgets.Label(value="HSA Requirements To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        #print(updatedReqsDict)
        display(widgets.GridBox([widgets.VBox(HSAItemsDone), widgets.VBox(HSAItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))


#telling the buttons which function to call when clicked
updateReqButton.on_click(on_update_clicked)
addCourseButton.on_click(on_add_clicked)
removeCourseButton.on_click(on_remove_click)

#Setting up initial conditions
with outputCourseList:
    print("Current Courses: ", inputCourses)

with outputReqsListTotal:
        print("Core Remaining: ", totalReqsDict["coreToDo"])
        print("Major Remaining: ", totalReqsDict["majorToDo"])
        print("HSA Remaining: ", totalReqsDict["hsaToDo"])

with outputHSAList:
        HSAItemsDone = [widgets.Label(str(i)) for i in totalReqsDict["hsaDone"]]
        HSAItemsToDo = [widgets.Label(str(i)) for i in totalReqsDict["hsaToDo"]]
        labels = [widgets.Label(value="HSA Requirements Done"), widgets.Label(value="HSA Requirements To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        display(widgets.GridBox([widgets.VBox(HSAItemsDone), widgets.VBox(HSAItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))


with outputCoreList:
        coreItemsDone = [widgets.Label(value=f"{i}") for i in totalReqsDict["coreDone"]]
        coreItemsToDo = [widgets.Label(value=f"{i}") for i in totalReqsDict["coreToDo"]]
        labels = [widgets.Label(value="Core Done"), widgets.Label(value="Core To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        #print(updatedReqsDict)
        display(widgets.GridBox([widgets.VBox(coreItemsDone), widgets.VBox(coreItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))

with outputMajorList:
        majorItemsDone = [widgets.Label(str(i)) for i in totalReqsDict["majorDone"]]    
        majorItemsToDo = [widgets.Label(str(i)) for i in totalReqsDict["majorToDo"]]   
        labels = [widgets.Label(value="Major Requirements Done"), widgets.Label(value="Major Requirements To Do")]
        display(widgets.GridBox(labels, layout=widgets.Layout(
        grid_template_columns="repeat(2, auto)",  # Three items per row
        grid_gap="20px",  # Space between rows and columns
        padding="10px")))
        #print(updatedReqsDict)
        display(widgets.GridBox([widgets.VBox(majorItemsDone), widgets.VBox(majorItemsToDo)], layout=widgets.Layout(grid_template_columns="repeat(2, auto)", grid_gap="40px", padding="10px")))

outputSemester1 = widgets.Output()
outputSemester2 = widgets.Output()
outputSemester3 = widgets.Output()
outputSemester4 = widgets.Output()
outputSemester5 = widgets.Output()
outputSemester6 = widgets.Output()
outputSemester7 = widgets.Output()
outputSemester8 = widgets.Output()
semester1 = []
semester2 = []
semester3 = []
semester4 = []
semester5 = []
semester6 = []
semester7 = []
semester8 = []

with outputSemester1:
    print('Courses in Semester 1:', semester1)
with outputSemester2:
    print('Courses in Semester 2:', semester2)
with outputSemester3:
    print('Courses in Semester 3:', semester3)
with outputSemester4:
    print('Courses in Semester 4:', semester4)
with outputSemester5:
    print('Courses in Semester 5:', semester5)
with outputSemester6:
    print('Courses in Semester 6:', semester6)
with outputSemester7:
    print('Courses in Semester 7:', semester7)
with outputSemester8:
    print('Courses in Semester 8:', semester8)

#Gives us our different semester edits

semesterBox1 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox2 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox3 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox4 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox5 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox6 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox7 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  
semesterBox8 = widgets.Text(
    placeholder='Search and Add Classes',
    options=inputCourses,
    description='',
    ensure_option=True,
    disabled=False)  


semesters = [
widgets.VBox([semesterBox1, outputSemester1]),
widgets.VBox([semesterBox2, outputSemester2]),
widgets.VBox([semesterBox3, outputSemester3]),
widgets.VBox([semesterBox4, outputSemester4]),
widgets.VBox([semesterBox5, outputSemester5]),
widgets.VBox([semesterBox6, outputSemester6]),
widgets.VBox([semesterBox7, outputSemester7]),
widgets.VBox([semesterBox8, outputSemester8])
]

# # Function to handle the selection
def on_value_change1(change):
    if semesterBox1.value != '':  # Ensure the input is not empty
        semester1.append(semesterBox1.value)
        inputCourses.append(semesterBox1.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester1.clear_output()
    with outputSemester1:
        print('Courses in Semester 1:', semester1)
    
    semesterBox1.value = ''

def on_value_change2(change):
    if semesterBox2.value != '':  # Ensure the input is not empty
        semester2.append(semesterBox2.value)
        inputCourses.append(semesterBox2.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester2.clear_output()
    with outputSemester2:
        print('Courses in Semester 2:', semester2)
    semesterBox2.value = ''

def on_value_change3(change):
    if semesterBox3.value != '':  # Ensure the input is not empty
        semester3.append(semesterBox3.value)
        inputCourses.append(semesterBox3.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester3.clear_output()
    with outputSemester3:
        print('Courses in Semester 3:', semester3)
    semesterBox3.value = ''

def on_value_change4(change):
    if semesterBox4.value != '':  # Ensure the input is not empty
        semester4.append(semesterBox4.value)
        inputCourses.append(semesterBox4.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester4.clear_output()
    with outputSemester4:
        print('Courses in Semester 4:', semester4)
    semesterBox4.value = ''

def on_value_change5(change):
    if semesterBox5.value != '':  # Ensure the input is not empty
        semester5.append(semesterBox5.value)
        inputCourses.append(semesterBox5.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester5.clear_output()
    with outputSemester5:
        print('Courses in Semester 5:', semester5)
    semesterBox5.value = ''

def on_value_change6(change):
    if semesterBox6.value != '':  # Ensure the input is not empty
        semester6.append(semesterBox6.value)
        inputCourses.append(semesterBox6.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester6.clear_output()
    with outputSemester6:
        print('Courses in Semester 6:', semester6)
    semesterBox6.value = ''

def on_value_change7(change):
    if semesterBox7.value != '':  # Ensure the input is not empty
        semester7.append(semesterBox7.value)
        inputCourses.append(semesterBox7.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester7.clear_output()
    with outputSemester7:
        print('Courses in Semester 7:', semester7)
    semesterBox7.value = ''

def on_value_change8(change):
    if semesterBox8.value != '':  # Ensure the input is not empty
        semester8.append(semesterBox8.value)
        inputCourses.append(semesterBox8.value)
    outputCourseList.clear_output()
    with outputCourseList:
        print("Current Courses:", inputCourses)
    outputSemester8.clear_output()
    with outputSemester8:
        print('Courses in Semester 8:', semester8)
    semesterBox8.value = ''

semesterBox1.on_submit(on_value_change1)
semesterBox2.on_submit(on_value_change2)
semesterBox3.on_submit(on_value_change3)
semesterBox4.on_submit(on_value_change4)
semesterBox5.on_submit(on_value_change5)
semesterBox6.on_submit(on_value_change6)
semesterBox7.on_submit(on_value_change7)
semesterBox8.on_submit(on_value_change8)

#Creating the display and layout of each widget and output
#In this case, it is in tabs to navigate, and then place widgets inside in the tabs within a Box 
tab_contents = [
widgets.VBox([courseTextBox,
              widgets.HBox([addCourseButton, removeCourseButton]), 
              outputCourseList, 
              updateReqButton,
              outputReqsListTotal]), 
widgets.VBox([updateReqButton, outputCoreList]),
widgets.VBox([updateReqButton, outputMajorList]),
widgets.VBox([updateReqButton, outputHSAList]),
widgets.VBox([courseTextBox,
              widgets.HBox([addCourseButton, removeCourseButton]), 
              outputCourseList,
              widgets.Accordion(semesters, titles=('Semester 1', "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8")),
])]
tab = widgets.Tab()
tab.children = tab_contents
tab.titles = ["Overview of Courses", "Core", "Major", "HSA", "Semester Layout"]
tab
