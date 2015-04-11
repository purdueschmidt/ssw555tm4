import sys
import re
import time
import datetime
from datetime import date
from __builtin__ import str
from inspect import ismethod

def stringToDate(str):
    if str is not None:
        return datetime.datetime.strptime(str, "%d %b %Y").date()
    else:
        return str

class GedI: 
    def __init__(self, pointer):
        self.pointer = pointer
        self.firstname = None
        self.lastname = None
        self.sex = None
        self.birt= None
        self.deat = None
        self.famc = None
        self.fams = None
        
    def getAge(self):
        if self.birt is not None:
            birtDate = stringToDate(self.birt)
            curDate = date.today()
            return curDate.year - birtDate.year - ((curDate.month, curDate.day) < (birtDate.month, birtDate.day))
            
class GedF:
    def __init__(self, pointer):
        self.pointer = pointer
        self.marr = None
        self.husb = None
        self.wife = None
        self.chil = []
        self.div = None



class GedList:

    def __init__(self, filename):
        self.tagchecks = {"INDI":0, "NAME":1, "SEX":1, "BIRT":1, "DEAT":1, "FAMC":1, "FAMS":1, "FAM":0, "MARR":1, "HUSB":1, "WIFE":1, "CHIL":1, "DIV":1, "DATE":2, "TRLR":0, "NOTE":0}
        self.list={}
        numFamily = 0

        f = open(filename,'r')

        lines = f.readlines()

        i = 0;

        while i < len(lines):
            
            line = lines[i]

            spl = line.split()

            if spl[1] == "TRLR":
                break

            #don't even bother if it's not a valid tag
            elif not self.checkTag(spl):
                i+=1
                continue

            #outer loop only cares about level 0
            elif spl[0] != '0':
                i+=1
                continue

            #it's good
            else:
                if spl[2] == "INDI":
                    tempged = GedI(spl[1])
                    while True:
                        #get the next line until the end of the new entity
                        try:
                            nextl = lines[i+1]
                        except IndexError:
                            i+=1

                        spl2 = nextl.split()
                        #do all the normal error checking stuff
                        if not self.checkTag(spl2):
                            i+=1
                            continue

                        elif spl2[0] == '0':
                            break
                        #here's where the magic happens
                        else:
                            #print nextl
                            if spl2[1] == "NAME":
                                tempged.firstname = spl2[2]
                                tempged.lastname = spl2[3].translate(None, "/")
                            elif spl2[1] == "BIRT" or spl2[1] == "DEAT":
                                dateline = lines[i+2].split()
                                if spl2[1] == "BIRT":
                                    dateline[2] = "0" + dateline[2] if int(dateline[2]) < 10 else dateline[2]
                                    tempged.birt = dateline[2] + " " + dateline[3] + " " + dateline[4]
                                else:
                                    dateline[2] = "0" + dateline[2] if int(dateline[2]) < 10 else dateline[2]
                                    tempged.deat = dateline[2] + " " + dateline[3] + " " + dateline[4]
                                i += 1  #Skip an extra line since we read 2
                            elif spl2[1] == "SEX":
                                tempged.sex = spl2[2]
                            elif spl2[1] == "FAMC":
                                tempged.famc = spl2[2]
                            elif spl2[1] == "FAMS":
                                tempged.fams = spl2[2]
                        i += 1
                    self.list[tempged.pointer] = tempged
                    # print "Added " + tempged.pointer + " to list"
                    
                elif spl[2] == "FAM":
                    tempged = GedF(spl[1])
                    while True:
                        #get the next line until the end of the new entity
                        try:
                            nextl = lines[i+1]
                        except IndexError:
                            i+=1

                        spl2 = nextl.split()
                        #do all the normal error checking stuff
                        if not self.checkTag(spl2):
                            i+=1
                            continue

                        elif spl2[0] == '0':
                            break
                        #here's where the magic happens
                        else:
                            if spl2[1] == "HUSB":
                                tempged.husb = spl2[2]
                            elif spl2[1] == "WIFE":
                                tempged.wife = spl2[2]
                            elif spl2[1] == "CHIL":
                                tempged.chil.append(spl2[2])
                            elif spl2[1] == "MARR" or spl2[1] == "DIV":
                                dateline = lines[i+2].split()
                                if spl2[1] == "MARR":
                                    dateline[2] = "0" + dateline[2] if int(dateline[2]) < 10 else dateline[2]
                                    tempged.marr = dateline[2] + " " + dateline[3] + " " + dateline[4]
                                else:
                                    dateline[2] = "0" + dateline[2] if int(dateline[2]) < 10 else dateline[2]
                                    tempged.div = dateline[2] + " " + dateline[3] + " " + dateline[4]
                            
                        i += 1
                    # print "Added " + tempged.pointer + " to list"
                    self.list[tempged.pointer] = tempged



    def checkTag(self, spl):

        lnum = int(spl[0])

        if lnum ==0:
            if len(spl) ==2:
                tag = spl[1]
            else:
                tag = spl[2]

        else:
            tag = spl[1]
        
        if tag not in self.tagchecks:
            return False

        else:
            if self.tagchecks[tag] == lnum:
                return True

            else:
                return False

    # def __str__(self):

    #   ret = ""

    #   return ret

    def getKey(self, item):
        if 'F' in item:
            return int("999999"+item.translate(None, "@F"))
        else:
            return int("0"+item.translate(None,"@I"))

        
    def testPrintList(self):
        sorted_x = sorted(self.list.keys(), None, key=self.getKey)              
        for sorted_key in sorted_x:     
            for key, value in self.list.iteritems():
                        if re.search("@I.+", key) and key == sorted_key:
                            print key + " " + value.firstname + " " + value.lastname
                        elif re.search("@F.+", key) and key == sorted_key:
                            husb = self.list[value.husb]
                            wife = self.list[value.wife]
                            print key + " Husband: " + husb.firstname + " " + husb.lastname + " Wife: " + wife.firstname + " " + wife.lastname
                            
    def testParentMarriage(self):
        # note: in python 3, iter() is the exact same as iteritems(). https://stackoverflow.com/questions/10458437/what-is-the-difference-between-dict-items-and-dict-iteritems
        for id, item in self.list.iteritems():
            if re.search("@I.+", id):
                if item.fams is not None and item.famc is not None:
                    spouseId = self.list[item.fams].wife if self.list[item.fams].husb == id else self.list[item.fams].husb
                    parentId1 = self.list[item.famc].wife
                    parentId2 = self.list[item.famc].husb
                    
                    if parentId1 == spouseId:
                        print "Error: " + item.firstname + " " + item.lastname + " is married to their parent " + self.list[parentId1].firstname + " " + self.list[parentId1].lastname
                    elif parentId2 == spouseId:
                        print "Error: " + item.firstname + " " + item.lastname + " is married to their parent " + self.list[parentId2].firstname + " " + self.list[parentId2].lastname
            
    def testMinorMarriage(self):
        for id, item in self.list.iteritems():
            if re.search("@I.+", id):
                if item.fams is not None:
                    spouseId = self.list[item.fams].wife if self.list[item.fams].husb == id else self.list[item.fams].husb
                    
                    if self.list[spouseId].getAge() < 18:
                        print "Error: " + item.firstname + " " + item.lastname + " is married to a minor " + self.list[spouseId].firstname + " " + self.list[spouseId].lastname
                        
    def testBirthDeathCheck(self):
        for id, item in self.list.iteritems():
            if "@I" in id:
                if item.deat is None:
                    continue
                birthDate = stringToDate(item.birt)
                deathDate = stringToDate(item.deat)
                if birthDate>deathDate:
                    print "Error: " + item.firstname + " " + item.lastname + " has died before they are born"
                    
    def testChildParentBirthDeathCheck(self):
        childDod = None
        for id, item in self.list.iteritems():
            if "@F" in id:
                fatherDob = stringToDate(self.list.get(item.husb).birt)
                motherDob = stringToDate(self.list.get(item.wife).birt)
                fatherDod = stringToDate(self.list.get(item.husb).deat)
                motherDod = stringToDate(self.list.get(item.wife).deat)

                for child in item.chil:
                    
                    if self.list.get(child).birt:
                        childDob  = stringToDate(self.list.get(child).birt)
                        if childDob < fatherDob or childDob < motherDob:
                            print "Error: " + self.list.get(child).firstname + " " + self.list.get(child).lastname + "'s birth is before their parent's birth."
                        if fatherDod is not None:
                            if childDob > fatherDod:
                                print "Error: " + self.list.get(child).firstname + " " + self.list.get(child).lastname + "'s birth is after their parent's death."
                        if motherDod is not None:
                            if childDob > motherDod:
                                print "Error: " + self.list.get(child).firstname + " " + self.list.get(child).lastname + "'s birth is after their parent's death."

                    if self.list.get(child).deat:
                        childDod  = stringToDate(self.list.get(child).deat)
                        if childDod < fatherDob or childDod < motherDob:    
                            print "Error: " + self.list.get(child).firstname + " " + self.list.get(child).lastname + "'s death is before their parent's birth."
                                    
    def testTimeLine(self):
        timelinelist = {}
        for id, item in self.list.iteritems():
            if "@I" in id:
                if item.birt is not None:
                    birthday = stringToDate(item.birt)
                    timelinelist[birthday] = item.firstname + " " + item.lastname + " was born on " + str(birthday)
                if item.deat is not None:
                    deathday = stringToDate(item.deat)
                    timelinelist[deathday] = item.firstname + " " + item.lastname + " died on " + str(deathday)
            elif "@F" in id:
                if item.marr is not None:
                    marrday = stringToDate(item.marr)
                    husband = self.list.get(item.husb)
                    wife = self.list.get(item.wife)
                    timelinelist[marrday] = husband.firstname + " " + husband.lastname + " and " + wife.firstname + " " + wife.lastname + " were married on " +str(marrday)
                if item.div is not None:
                    divday =stringToDate(item.div)
                    timelinelist[divday] = husband.firstname + " " + husband.lastname + " and " + wife.firstname + " " + wife.lastname + " got divorced on " + str(divday)

        sorted_x = [value for (key, value) in sorted(timelinelist.items())]

        for event in sorted_x:
            print event

    def testDeathMarriageCheck(self):
        for id, item in self.list.iteritems():
            if "@F" in id:
                if item.marr:                   
                    marrDate = stringToDate(item.marr)
                    
                    if self.list[item.husb].deat is not None:
                        husbDeathDate=stringToDate(self.list[item.husb].deat)
                        if husbDeathDate < marrDate:
                            print "Error: " + self.list[item.husb].firstname + " " + self.list[item.husb].lastname + " died before marriage"
                        
                    if self.list[item.wife].deat is not None:
                        wifeDeathDate=stringToDate(self.list[item.wife].deat)
                        if wifeDeathDate < marrDate:
                            print "Error: " + self.list[item.wife].firstname + " " + self.list[item.wife].lastname + " died before marriage"
                                            
    def testMarriageBirthCheck(self):
        for id, item in self.list.iteritems():
            if "@F" in id:
                if item.marr:                   
                    marrDate = stringToDate(item.marr)
                    
                    if self.list[item.husb].birt is not None:
                        husbBirthDate=stringToDate(self.list[item.husb].birt)
                        if husbBirthDate > marrDate:
                            print "Error: " + self.list[item.husb].firstname + " " + self.list[item.husb].lastname + " was born after marriage"
                        
                    if self.list[item.wife].birt is not None:
                        wifeBirthDate=stringToDate(self.list[item.wife].birt)
                        if wifeBirthDate > marrDate:
                            print "Error: " + self.list[item.wife].firstname + " " + self.list[item.wife].lastname + " was born after marriage"         
    
    def testDivorceBirthDeathCheck(self):
		for id, item in self.list.iteritems():
			if "@F" in id:
				if item.div:
					divorceDate = stringToDate(item.div)
					
					if self.list[item.husb].birt is not None:
						husbBirthDate=stringToDate(self.list[item.husb].birt)
						if husbBirthDate > divorceDate:
							print "Error: " + self.list[item.husb].firstname + " " + self.list[item.husb].lastname + " was born after his divorce"

					if self.list[item.wife].birt is not None:
						wifeBirthDate=stringToDate(self.list[item.wife].birt)
						if wifeBirthDate > divorceDate:
							print "Error: " + self.list[item.wife].firstname + " " + self.list[item.wife].lastname + " was born after her divorce"		 

					if self.list[item.husb].deat is not None:
						husbDeathDate=stringToDate(self.list[item.husb].deat)
						if husbDeathDate < divorceDate:
							print "Error: " + self.list[item.husb].firstname + " " + self.list[item.husb].lastname + " has died before his divorce"

					if self.list[item.wife].deat is not None:
						wifeDeathDate=stringToDate(self.list[item.wife].deat)
						if wifeDeathDate < divorceDate:
							print "Error: " + self.list[item.wife].firstname + " " + self.list[item.wife].lastname + " has died before her divorce"		 
					
					    	                        
    def testMultipleMarriageCheck(self):
        spouseDict = {}
        for id, item in self.list.iteritems():
            if "@F" in id:
                if item.div is None:
                    if item.husb not in spouseDict:
                        spouseDict[item.husb] = []
                    if item.wife not in spouseDict:
                        spouseDict[item.wife] = []
                    spouseDict[item.husb].append(id)
                    spouseDict[item.wife].append(id)
            
        for key, values in spouseDict.iteritems():
            if len(values) > 1:
                print "Error: " + self.list[key].firstname + " " + self.list[key].lastname + " is in multiple active marriages"
                
    def testAgeLimitCheck(self):
        for id, item in self.list.iteritems():
            if "@I" in id:
                age = item.getAge()
                
                if age > 150:
                    print "Error: " + item.firstname + " " + item.lastname + " is older than 150 years"

    def testWhosAlive(self):
        for id, item in self.list.iteritems():
            if "@I" in id:
                if item.deat is None:
                    print item.firstname + " " + item.lastname + " is currently alive."
    
    def testWidowsAndWidowers(self):
        for id, item in self.list.iteritems():
            if "@F" in id:
                wife = self.list[item.wife]
                husband = self.list[item.husb]
                if wife.deat is not None and husband.deat is None:
                    print husband.firstname + " " + husband.lastname + " is a widower."

                elif husband.deat is not None and wife.deat is None:
                    print wife.firstname + " " + wife.lastname + " is a widow."
                
    def testSiblingMarriage(self):
        for id, item in self.list.iteritems():
            if "@F" in id:
                wife = self.list[item.wife]
                husband = self.list[item.husb]
                wifeFam = wife.famc
                husbandFam = husband.famc

                if wifeFam == husbandFam and wifeFam is not None and husbandFam is not None:
                    print "Anomaly: " + wife.firstname + " " + wife.lastname + " and " + husband.firstname + " " + husband.lastname + " are siblings and married."
                    
    def testTreeVisualization(self):
        topLevelFams = []
        for id, item in self.list.iteritems():
            if "@F" in id:
                #populate list of top level families (parents have null FAMC)
                if self.list[item.wife].famc is None and self.list[item.husb].famc is None:
                    topLevelFams.append(id)

        for id in topLevelFams:
            print "************** Tree for Family " + id + " ********************"
            self.printFamily(id, 0)
            print "**********************************************************"
                
    def printFamily(self, id, tabs):
        if id in self.list:
            tabString = ""
            for i in range(0, tabs):
                tabString += "---"
            father = self.list[self.list[id].husb]
            mother = self.list[self.list[id].wife]
            print tabString + "Father: " + father.firstname + " " + father.lastname
            print tabString + "Mother: " + mother.firstname + " " + mother.lastname
            for child in self.list[id].chil:
                self.printFamily(self.list[child].fams, tabs + 1)

    def testDeadWhileMarried(self):
        for id, item in self.list.iteritems():
            if "@F" in id:
                if item.marr:                    
                    if self.list[item.husb].deat is not None:
                        print self.list[item.husb].firstname + " " + self.list[item.husb].lastname + " is dead while married."
                        
                    if self.list[item.wife].deat is not None:
                        print self.list[item.wife].firstname + " " + self.list[item.wife].lastname + " is dead while married."


    def testBirthdayMonth(self):
        for id, item in self.list.iteritems():
            if "@I" in id:
                birtDate = stringToDate(item.birt)
                if birtDate.month == datetime.datetime.now().month:
                    print item.firstname + " " + item.lastname + " has a birthday this month!"


    def testDeaths(self):
        print "Summary of Deaths:"
        for id, item in self.list.iteritems():
            if "@I" in id:
                if item.deat is not None:
                    print item.firstname + " " + item.lastname + " Born: " + item.birt + " Died: " + item.deat

    def testMotherFather(self):
        for id, item in self.list.iteritems():
            if "@I" in id:
                if item.famc is not None:
                    if (self.list[item.famc].wife is None) or (self.list[self.list[item.famc].wife] is None):
                        print item.firstname + " " + item.lastname + "'s mother does not exist."

                    if self.list[self.list[item.famc].wife].sex != "F":
                        print item.firstname + " " + item.lastname + "'s mother is not female."

                    if (self.list[item.famc].husb is None) or (self.list[self.list[item.famc].husb] is None):
                        print item.firstname + " " + item.lastname + "'s father does not exist."

                    if self.list[self.list[item.famc].husb].sex != "M":
                        print item.firstname + " " + item.lastname + "'s father is not male."
    
    #Runs all the tests, make sure function names start with "test"
    def runTests(self, *args, **kwargs):
        for name in dir(self):
            attribute = getattr(self, name)
            if ismethod(attribute):
                if name[:4] == "test":
                    self.identifyTest(name)
                    attribute(*args, **kwargs)
                    
    def identifyTest(self, name):
        print "\n************** Running Test " + name[4:] + " ********************"
#and now for the main

g = GedList("gedcoms/sprint1.ged")
g.runTests()
#g.testDivorceBirthDeathCheck()