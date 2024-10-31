import csv
import json

# global vars
numTechElectives = 3 # how many tech electives are required?
majorCSVpath = "CS_Major_Requirements" #TODO: update this 

coursesToDo = []
coursesDone  = []

coreReqs = []
majorReqs = []
HSAreqs = []
totalReqs = []

####### sample data, not extensive ######
inputCourses = [
    "CSCI005",
    "CSCI060",
    "MATH019",
    "WRIT001",
    "PHYS023"]
coreReqs = [
    ["MATH019"],
    ["CSCI005", "CSCI042"],
    ["PHYS023"],
    ["CORE099"],
    ["CHEM024"],
    ["WRIT001"]]
HSAReqs = [
    ["HSA10"],
    ["WRIT001"],
    ["HSABreadth"],
    ["HSADepth"],
    ["WritInt"]]

##### function definitions

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

def checkReqsMet(inputList, reqsList):
    """ TODO: ADD FULL DOCSTRING HERE
    """
    # inputList is a flat list
    # reqsList is a list of lists
    for subset in reqsList:
        met = any(course in subset for course in inputList)
        if met:
            coursesDone.append(subset)
        else:
            coursesToDo.append(subset)

def checkReqsMet(inputList):
    # inputList is a
    # reqsList is a list of lists
    for section in totalReqs:
        for subset in section:
            met = any(course in subset for course in inputList)
            if met and not(subset in coursesDone):
                coursesDone.append(subset)
            if not(met) and not(subset in coursesToDo):
                coursesToDo.append(subset)

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

def printNice(inputList):
    for i in inputList:
        print(i)


####### code runs ######

majorReqs = csvToLoL(majorCSVpath)
checkReqsMet(inputCourses, majorReqs)

print("Courses Done is", coursesDone)
print("Courses ToDo is", coursesToDo)

filterByArea("CSCI")

def getTotalReqs(majorReqs, coreReqs, HSAReqs):
    totalReqs.append(coreReqs)
    totalReqs.append(majorReqs)
    totalReqs.append(HSAReqs)

#creating the total reqs
getTotalReqs(majorReqs, coreReqs, HSAReqs)

print("Courses Done is", coursesDone)
print("Courses ToDo is", coursesToDo) #not pretty, so lets make it pretty

#functions to allow for nice print out
print("Courses Done:") 
printNice(coursesDone)
print("Courses To Do:") 
printNice(coursesToDo)

#this doesn't give us much information about the courses still left to do
#so lets add a filter to check major/core/HSA etc
majorReqsDone =[]
majorReqsToDo = []
coreReqsDone = []
coreReqsToDo = []
HSAReqsDone = []
HSAReqsToDo = []

def filterReqs(inputList, areaFilter):
    reqsList = []
    toDoList = []
    doneList = []
    if areaFilter == "Core":
        reqsList = coreReqs
        toDoList = coreReqsToDo
        doneList = coreReqsDone
    if areaFilter == "Major":
        reqsList = majorReqs
        toDoList = majorReqsToDo
        doneList = majorReqsDone
    if areaFilter == "HSA":
        reqsList = HSAReqs
        toDoList = HSAReqsToDo
        doneList = HSAReqsDone
    for subset in reqsList:
        met = any(course in subset for course in inputList)
        if met and not(subset in doneList):
                  doneList.append(subset)
        if not(met) and not(subset in toDoList):
                  toDoList.append(subset)


#applying the filters
filterReqs(inputCourses, "HSA")
filterReqs(inputCourses, "Core")
filterReqs(inputCourses, "Major")

print("HSA Reqs Met:")
printNice(HSAReqsDone)
print("HSA Reqs Not Met:")
printNice(HSAReqsToDo)
print("Core Reqs Met:")
printNice(coreReqsDone)
print("Core Reqs Not Met:")
printNice(coreReqsToDo)
print("Major Reqs Met:")
printNice(majorReqsDone)
print("Major Reqs Not Met:")
printNice(majorReqsToDo)