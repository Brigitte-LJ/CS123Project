import csv
import json
import pdb

# global vars
numTechElectives = 3 # how many tech electives are required?

coreCSVpath = ""
majorCSVpath = "CS_Major_Requirements" #TODO: update this 
hsaCSVpath = ""

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
# see defineReqsDict() for completed dictionary format

####### sample data, not extensive ######

inputCourses = [
    "CSCI005",
    "CSCI060",
    "MATH019",
    "WRIT001",
    "PHYS023"]

sampleData = {
    "coreReqs": [
    ["MATH019"],
    ["CSCI005", "CSCI042"],
    ["PHYS023"],
    ["CORE099"],
    ["CHEM024"],
    ["WRIT001"]],
    
    "hsaReqs": [
    ["HSA10"],
    ["WRIT001"],
    ["HSABreadth"],
    ["HSADepth"],
    ["WritInt"]]
}

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
      coursecode = row[2]
      if row[1] == "y": # tech elective case
        techElectives.append(coursecode)
      else:
        if int(row[-1])==i: # our CSV data is a string, and "0" =/= 0
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
    if coreCSVpath != "":
        reqsDict["core"] = csvToLoL(coreCSVpath)
    else: 
        reqsDict["core"] = sampleData["coreReqs"]
    if majorCSVpath != "":
        reqsDict["major"] = csvToLoL(majorCSVpath)
    else:
        majorReqs = sampleData["majorReqs"]
    if hsaCSVpath != "":
        reqsDict["hsa"] = csvToLoL(hsaCSVpath)
    else: 
        reqsDict["hsa"] = sampleData["hsaReqs"]

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

def printNice(inputList):
    for i in inputList:
        print(i)

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


# Takes in an array of already taken course codes
# Returns a dictionary containing only the taken course 
# tagged with HSAs and their corresponding credit value
# ex) input = ["HIST055  CM", "CSCI140  HM", "ART 005  PO", "DANC051  PO", "ART 060  HM"]
# output = {'HIST055  CM': '1.0', 'ART 005  PO': '1.0', 'DANC051  PO': '0.5', 'ART 060  HM': 0.5}

def filterHSA(coursesDone):
    # First, filter out all non-HSAS, we can find out whether or not a course is an HSA by looking in the course-area.json file. 
    with open("course-area.json", 'r') as file: # Open the JSON file containing area data
        courseArea = json.load(file)
    
    with open("course-section.json", 'r') as file: # Open the JSON file containing credit data
        courseSection = json.load(file)
    
    HSAcredits = {}
    allTakenData = []

    # Filter through courseArea for taken courses
    # Add taken courses and their corresponding area data into allTakenData
    for course in coursesDone:
        allTakenData.extend(list(filter(lambda x: x["course_code"] == course, courseArea)))
    
    # Filter through allTakenData
    # Add only courses which are tagged with HSAs into HSAcredits as keys with empty values
    for taken in allTakenData:
        if ('4HSS' in taken["course_areas"]) or ('4HSA'in taken["course_areas"]):
            HSAcredits[taken["course_code"]] = ""

    # For each HSA taken, find and set its credit amount as the value corresponding to
    # its course code in a key-value pair within the HSAcredits dictionary
    for HSA in HSAcredits:
        for course in courseSection:
            if (HSA in course["courseSectionId"]):
                HSAcredits[HSA] = course["creditHours"]
    
    # If the HSA taken is at Mudd, convert its credit value to the 5C credit value
    # i.e. Divide all mudd credits by 3.
    for HSA in HSAcredits:
        if ("HM" in HSA):
            HSAcredits[HSA] =  float(HSAcredits[HSA]) / 3.0
        
    return HSAcredits

# Takes in an array of already taken course codes
# Returns true if breadth is fulfilled, false if otherwise.
# Breadth is fulfilled if there are at least 5 full courses taken in 5 different areas. 
# (a full course is 1.0 cr (assuming mudd is converted))

def checkBreadth(niceHSAs):
    completeArea = []
    count = 0
    halves = {}
    for HSA in niceHSAs:
        # credit is 1.0 and area is not complete:
        if ((float(niceHSAs[HSA]) == 1.0) and (HSA[0:5] not in completeArea)):
            count+=1
            completeArea.extend(HSA[0:5])
        # credit is 0.5 and area is not complete:
        elif (float(niceHSAs[HSA]) == 0.5 and (HSA[0:5] not in completeArea)):
            # There have been no previous 0.5 courses in this area:
            if (HSA[0:5] not in halves):
                halves[HSA[0:5]] = 0.5
            # There has been a previous 0.5 course in this area:
            elif (halves[HSA[0:5]] == 0.5):
                count+=1
                completeArea.extend(HSA[0:5]) # 0.5 + 0.5 = a full course, add to completeArea
                halves[HSA[0:5]] = 1.0
    return (count >= 5)


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


#Function calls:
# done = ["HIST055  CM", "CSCI140  HM", "DANC051  PO", "ANTH190  SC", "ASIA190  PO", "DANC010  PO", "DANC122  PO", "DANC124  PO"]
# niceHSAs = filterHSA(done)
# print("Breadth fulfilled:" , checkBreadth(niceHSAs))
# print("Depth(Concentration) fulfilled:" , checkDepth(niceHSAs))
      

############## TUTORIAL SECTION 2 ################

def filterByArea(area):
  """ TODO: ADD DOCSTRING HERE
  """
  with open("course-area.json", 'r') as file: # Open the JSON file
      course_data = json.load(file)  # Load the JSON data from the file into list

  output = []
  for course in course_data:  # Print all courses that have the attribute of area
    if area in set(course["course_areas"]):
      courseOnly = course["course_code"][:-2].strip() # Remove two-lettered campus signature, remove whitespaces
      output.append(courseOnly) # add course into final list
  return output # return list of all courses in parameter area.



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