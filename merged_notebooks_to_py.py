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