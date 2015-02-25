import sys
import re
import time
import datetime
from datetime import date

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
		if self.birt != None:
			birtDate = datetime.datetime.strptime(self.birt, "%d %b %Y").date()
			curDate = date.today()
			return curDate.year - birtDate.year - ((curDate.month, curDate.day) < (birtDate.month, birtDate.day))
			
class GedF:
	def __init__(self, pointer):
		self.pointer = pointer
		self.marr = None
		self.husb = None
		self.wife = None
		self.chil = None
		self.div = None



class GedList:

	def __init__(self, filename):
		self.tagchecks = {"INDI":0, "NAME":1, "SEX":1, "BIRT":1, "DEAT":1, "FAMC":1, "FAMS":1, "FAM":0, "MARR":1, "HUSB":1, "WIFE":1, "CHIL":1, "DIV":1, "DATE":2, "TRLR":0, "NOTE":0}
		self.list={}

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
								tempged.chil = spl2[2]
							
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

	# 	ret = ""

	# 	return ret

	def getKey(self, item):
		if 'F' in item:
			return int("999999"+item.translate(None, "@F"))
		else:
			return int("0"+item.translate(None,"@I"))
		
	def printList(self):
		sorted_x = sorted(self.list.keys(), None, key=self.getKey)				
		for sorted_key in sorted_x:		
			for key, value in self.list.iteritems():
 						if re.search("@I.+", key) and key == sorted_key:
 							print key + " " + value.firstname + " " + value.lastname
					 	elif re.search("@F.+", key) and key == sorted_key:
					 		husb = self.list[value.husb]
					 		wife = self.list[value.wife]
					 		print key + " Husband: " + husb.firstname + " " + husb.lastname + " Wife: " + wife.firstname + " " + wife.lastname
							
	def parentMarriage(self):
		for id, item in self.list.iteritems():
			if re.search("@I.+", id):
				testFail = False
				if item.fams != None and item.famc != None:
					spouseId = self.list[item.fams].wife if self.list[item.fams].husb == id else self.list[item.fams].husb
					parentId1 = self.list[item.famc].wife
					parentId2 = self.list[item.famc].husb
					
					if parentId1 == spouseId:
						testFail = True
						print item.firstname + " " + item.lastname + " is married to their parent " + self.list[parentId1].firstname + " " + self.list[parentId1].lastname + " -- Failed"
					elif parentId2 == spouseId:
						testFail = True
						print item.firstname + " " + item.lastname + " is married to their parent " + self.list[parentId2].firstname + " " + self.list[parentId2].lastname + " -- Failed"
						
				if testFail == False:
					print item.firstname + " "  + item.lastname + " not married to parent -- Passed"
			
	def minorMarriage(self):
		for id, item in self.list.iteritems():
			if re.search("@I.+", id):
				testFail = False
				if item.fams != None:
					spouseId = self.list[item.fams].wife if self.list[item.fams].husb == id else self.list[item.fams].husb
					
					if self.list[spouseId].getAge() < 18:
						testFail = True
						print item.firstname + " " + item.lastname + " is married to a minor " + self.list[spouseId].firstname + " " + self.list[spouseId].lastname + " -- Failed"
						
				if testFail == False:
					print item.firstname + " " + item.lastname + " not married to minor -- Passed"
						
		
			

#and now for the main

g = GedList("gedcoms/us16.ged")
#g.printList()
g.parentMarriage()
g.minorMarriage()

