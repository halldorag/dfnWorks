""" Functions and Scripts for dfnGen """

__author__ = "Jeffrey Hyman"
__version__ = "1.0"
__maintainer__ = "Satish Karra and Jeffrey Hyman"
__email__ = "jhyman@lanl.gov"

import re, os, sys, glob, time
from shutil import copy, rmtree
import numpy as np
import matplotlib.pylab as plt
from scipy.integrate import odeint 


def dfnGen_parse_input(input_file, output_file='input_clean.dat'):
	"""
					## Input Format Requirements ##

	    1. Each parameter must be defined on its own line (seperate by newline '\n')
	    2. A parameter (key) MUST be separated from its value by a colon ':' (ie. --> key: value)
		- Values may also be placed on lines after the 'key:' (ie. --> key: \n value)
	    3. Comment Format:  On a line containg // or /*, nothing after */ or // will be processed
				but text before a comment will be processed 
			       // Single line comment
			       /* Multline
				  comment */ This will NOT be processed
				This WILL be processed
	 
	"""

	## BIG TODO s -----
		## ==== Problems ==== ##
	## 11. Multiple keys on one line
	## 15. check # values (famprob: {.5,.5} {.3, .3., .4})
	params = { 'esd':[],'insertUserRectanglesFirst':[],'keepOnlyLargestCluster':[],'rmin':[],
	'rAngleOption':[],'boundaryFaces':[],'userRectanglesOnOff':[],'printRejectReasons':[],'numOfLayers':[],
	'RectByCood_Input_File_Path':[],'eLogMean':[],'rExpMin':[],'lengthCorrelatedAperture':[],'ebetaDistribution':[],
	'tripleIntersections':[],'layers':[],'stdAperture':[],'ealpha':[],'constantPermeability':[],'rLogMax':[],
	'rLogMean':[],'nFamRect':[],'etheta':[],'eLogMax':[],'rphi':[],'outputAllRadii':[],
	'r_p32Targets':[],'permOption':[],'userRecByCoord':[],'userEllipsesOnOff':[],'UserEll_Input_File_Path':[],
	'rExpMean':[],'rbetaDistribution':[],'aperture':[],'emax':[],'eExpMean':[],'e_p32Targets':[],'eLayer':[],
	'domainSizeIncrease':[],'h':[],'outputFinalRadiiPerFamily':[],'rbeta':[],'rLogMin':[],'edistr':[],'domainSize':[],
	'eExpMin':[],'ekappa':[],'rLayer':[],'seed':[],'constantAperture':[],'stopCondition':[],'enumPoints':[],
	'meanAperture':[],'eLogMin':[],'easpect':[],'rtheta':[],'rdistr':[],
	'UserRect_Input_File_Path':[],'rconst':[],'rExpMax':[],'ignoreBoundaryFaces':[],
	'visualizationMode':[],'outputAcceptedRadiiPerFamily':[],'apertureFromTransmissivity':[],'rsd':[],'ebeta':[],
	'nFamEll':[],'econst':[],'raspect':[],'eAngleOption':[],'emin':[],'ephi':[],'rmax':[],'famProb':[],'disableFram':[],
	'ralpha':[],'nPoly':[],'rejectsPerFracture':[],'rkappa':[],'eExpMax':[], 'forceLargeFractures':[], 'outputTriplePoints':[]} 

	unfoundKeys={'stopCondition','nPoly','outputAllRadii','outputAllRadii','outputFinalRadiiPerFamily',
	'outputAcceptedRadiiPerFamily','domainSize', 'numOfLayers', 'layers', 'h', 
	'tripleIntersections', 'printRejectReasons', 'disableFram', 'visualizationMode', 'seed', 'domainSizeIncrease',
	'keepOnlyLargestCluster', 'ignoreBoundaryFaces', 'boundaryFaces', 'rejectsPerFracture', 'famProb', 'insertUserRectanglesFirst',
	'nFamEll', 'eLayer', 'edistr', 'ebetaDistribution', 'e_p32Targets', 'easpect', 'enumPoints', 'eAngleOption', 'etheta', 'ephi',
	'ebeta', 'ekappa', 'eLogMean', 'esd', 'eLogMin', 'eLogMax', 'eExpMean', 'eExpMin', 'eExpMax', 'econst', 'emin', 'emax',
	'ealpha', 'nFamRect', 'rLayer', 'rdistr', 'rbetaDistribution', 'r_p32Targets', 'raspect', 'rAngleOption', 'rtheta', 'rphi',
	'rbeta', 'rkappa', 'rLogMean', 'rsd', 'rLogMin', 'rLogMax', 'rmin', 'rmax', 'ralpha', 'rExpMean', 'rExpMin', 'rExpMax',
	'rconst', 'userEllipsesOnOff', 'UserEll_Input_File_Path', 'userRectanglesOnOff', 'UserRect_Input_File_Path', 'userRecByCoord',
	'RectByCood_Input_File_Path', 'aperture', 'meanAperture', 'stdAperture', 'apertureFromTransmissivity', 'constantAperture',
	'lengthCorrelatedAperture', 'permOption', 'constantPermeability', 'forceLargeFractures', 'outputTriplePoints'}

	mandatory = {'stopCondition','domainSize','numOfLayers','outputAllRadii', 'outputFinalRadiiPerFamily',
	'outputAcceptedRadiiPerFamily','tripleIntersections','printRejectReasons',
	'disableFram','visualizationMode','seed','domainSizeIncrease','keepOnlyLargestCluster','ignoreBoundaryFaces',
	'rejectsPerFracture','famProb','insertUserRectanglesFirst','nFamEll','nFamRect','userEllipsesOnOff','userRectanglesOnOff',
	'userRecByCoord','aperture','permOption', 'forceLargeFractures', 'outputTriplePoints'}

	noDependancyFlags = ['outputAllRadii','outputFinalRadiiPerFamily',
	'outputAcceptedRadiiPerFamily','tripleIntersections','printRejectReasons',
	'visualizationMode', 'keepOnlyLargestCluster','insertUserRectanglesFirst', 'forceLargeFractures', 'outputTriplePoints']

	examples = {"Flag":"(0 or 1)", "Float":"(0.5, 1.6, 4.0, etc.)" , "Int":"(0,1,2,3,etc.)"}

	global ellipseFams
	ellipseFams = 0
	global rectFams
	rectFams = 0
	global numLayers
	numLayers = 0
	global minFracSize
	minFracSize = 99999999.9
		## WARNING: Index[0] for the following lists should never be used. See edistr() and rdistr() for clarity.
	global numEdistribs 
	numEdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]  
	global numRdistribs
	numRdistribs = [-1,0,0,0,0] ## [0 = no-op, 1 = # log-normal's, 2 = # Truncated Power Law's, 3 = # Exp's, # constant's]
	global warningFile
	warningFile = open("warningFileDFNGen.txt", 'w')        


	## ====================================================================== ##
	##                              Parsing Functions                         ##
	## ====================================================================== ##
	def extractParameters(line):
		if "/*" in line:
			comment = line
			line = line[:line.index("/*")] ## only process text before '/*' comment
			while "*/" not in comment:
				comment = next(inputIterator) ## just moves iterator past comment

		elif "//" in line:
			line = line[:line.index("//")] ## only process text before '//' comment
			
		return line.strip()


	def findVal(line, key):
		valList = []
		line = line[line.index(":") + 1:].strip()
		if line != "" : valHelper(line, valList, key)

		line = extractParameters(next(inputIterator))
		while ':' not in line:
			line = line.strip()
			if line != "" :
				valHelper(line, valList, key)
			try:
				line = extractParameters(next(inputIterator))
			except StopIteration:
				break
		
		if valList == [] and key in mandatory:
			error("\"{}\" is a mandatory parameter and must be defined.".format(key))
		if key is not None:
			params[key] = valList if valList != [] else [""] ## allows nothing to be entered for unused params 
		if line != "": processLine(line)
			
	## Input: line containing a paramter (key) preceding a ":" 
	## Returns: key -- if it has not been defined yet and is valid
	##          None -- if key does not exist
	##          exits -- if the key has already been defined to prevent duplicate confusion        
	def findKey(line):
		key = line[:line.index(":")].strip()
		if key in unfoundKeys:
			unfoundKeys.remove(key)
			return key
		try:
			params[key]
			error("\"{}\" has been defined more than once.".format(key))
		except KeyError:
			warning("\"" + key + "\" is not one of the valid parameter names.")

	def processLine(line):
		if line.strip != "":
			key = findKey(line)
			if key != None: findVal(line, key)   


	## ====================================================================== ##
	##                              Verification                              ##
	## ====================================================================== ##
	## Note: Always provide EITHER a key (ie "stopCondition") 
	##         OR inList = True/False (boolean indicating val being checked is inside a list) 

	## Input: value - value being checked
	##        key - parameter the value belongs to
	##        inList - (Optional)
	def verifyFlag(value, key = "", inList = False):
		if value is '0' or value is '1':
			return int(value)
		elif inList:
			return None
		else:
			error("\"{}\" must be either '0' or '1'".format(key))

	def verifyFloat(value, key = "", inList = False, noNeg = False):
		if type(value) is list:
			error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
		try:
			if noNeg and float(value) < 0:
				error("\"{}\" cannot be a negative number.".format(key))
			return float(value)
		except ValueError:
			if inList: return None
			else:
				error("\"{}\" contains an unexpected character. Must be a single "\
				      "floating point value (0.5, 1.6, 4.0, etc.)".format(key))
				
				
	def verifyInt(value, key = "", inList = False, noNeg = False):
		if type(value) is list:
			error("\"{}\" contains curly braces {{}} but should not be a list value.".format(key))
		try:
			if noNeg and int(re.sub(r'\.0*$', '', value)) < 0:
				error("\"{}\" cannot be a negative number.".format(key))
			return int(re.sub(r'\.0*$', '', value)) ## regex for removing .0* (ie 4.00 -> 4)
		except ValueError:
			if inList: return None
			else:
				error("\"{}\" contains an unexpected character. Must be a single "\
				      "integer value (0,1,2,3,etc.)".format(key))
				
	## Verifies input list that come in format {0, 1, 2, 3}
	##
	## Input:  valList - List of values (flags, floats, or ints) corresponding to a parameter
	##         key - the name of the parameter whose list is being verified
	##         verificationFn - (either verifyFlag, verifyFloat or verifyInt) checks each list element 
	##         desiredLength - how many elements are supposed to be in the list
	##         noZeros - (Optional) True for lists than cannot contain 0's, False if 0's are ok  
	##         noNegs - (Optional) True for lists than cannot contain negative numbers, False otherwise
	## Output: returns negative value of list length to indicate incorrect length and provide meaningful error message
	##         Prints error and exits if a value of the wrong type is found in the list
	##         returns None if successful
	##
	def verifyList(valList, key, verificationFn, desiredLength, noZeros=False, noNegs=False):
		if valList == ['']: return 0
		if type(valList) is not list:
			error("\"{}\"'s value must be a list encolsed in curly brackets {{}}.".format(key))
		if desiredLength != 0 and len(valList) != desiredLength:
			return -len(valList)
		for i, value in enumerate(valList):
			value = value.strip() 
			verifiedVal = verificationFn(value, inList = True)
			if verifiedVal == None:
				listType = re.sub('Integer', 'Int', re.sub(r'verify', '', verificationFn.__name__)) ## 'verifyInt' --> 'Integer'
				error("\"{}\" must be a list of {}s {}. Non-{} found in "\
				      "list".format(key, listType, examples[listType], listType))
			if noZeros and verifiedVal == 0:
				error("\"{}\" list cannot contain any zeroes.".format(key))
			if noNegs and isNegative(float(verifiedVal)):
				error("\"{}\" list cannot contain any negative values.".format(key)) 
			valList[i] = verifiedVal 
	       

	## def verifyNumValsIs(length, key):f
	       ##  if len(params[key]) != length:
		    ##     error("ERROR: ", "\"" + param + "\"", "should have", length, "value(s) but", len(params[key]), "are defined.")
		     ##    sys.exit()                
		

	## ====================================================================== ##
	##                              Helper Functions                          ##
	## ====================================================================== ##

	## '{1,2,3}' --> [1,2,3]
	def curlyToList(curlyList):
		return re.sub("{|}", "", curlyList).strip().split(",")

	## [1,2,3] --> '{1,2,3}'   for writing output
	def listToCurly(strList):
		 curl = re.sub(r'\[','{', strList)
		 curl = re.sub(r'\]','}', curl)
		 curl = re.sub(r"\'", '', curl)
		 return curl 

	def hasCurlys(line, key):
		if '{' in line and '}' in line: return True 
		elif '{' in line or '}' in line: 
			error("Line defining \"{}\" contains a single curly brace.".format(key))
		return False

	## Use to get key's value in params. writing always false  
	def valueOf(key, writing = False):
		if (not writing) and (len(params[key]) > 1):
			error("\"{}\" can only correspond to 1 list. {} lists have been defined.".format(key, len(params[key])))
		try:    
			val = params[key][0]
			if val == '' or val == []:
				error("\"{}\" does not have a value.".format(key))
			return val
		except IndexError:
			error("\"{}\" has not been defined.".format(key)) ## Include assumptions (ie no Angleoption -> degrees?)

	def getGroups(line, valList, key):
		curlyGroup = re.compile('({.*?})')
		groups = re.findall(curlyGroup, line)
		for group in groups:
			line = line.replace(group, '', 1) ## only delete first occurence
			valList.append(curlyToList(group))
			
		if line.strip() != "":
			error("Unexpected character found while parsing \"{}\".".format(key))

	def valHelper(line, valList, key):
		if hasCurlys(line, key):
			getGroups(line, valList, key)
		else:
			valList.append(line)
		
	def error(errString):
		print("\nERROR --- " + errString)
		print("\n----Program terminated while parsing input----\n")
		sys.exit(1)

	def warning(warnString):
		global warningFile
		print("WARNING --- " + warnString)
		warningFile.write("WARNING --- " + warnString + "\n")

	def isNegative(num): 
		return True if num < 0 else False

	## Makes sure at least one polygon family has been defined in nFamRect or nFamEll
	##      OR that there is a user input file for polygons. 
	def checkFamCount():
		userDefExists = (valueOf('userEllipsesOnOff') == '1') |\
			       (valueOf('userRectanglesOnOff') == '1') |\
			       (valueOf('userRecByCoord') == '1')
		
		if ellipseFams + rectFams <= 0 and not userDefExists:
			error("Zero polygon families have been defined. Please create at least one family "\
			      "of ellipses/rectagnles, or provide a user-defined-polygon input file path in "\
			      "\"UserEll_Input_File_Path\", \"UserRect_Input_File_Path\", or "\
			      "\"RectByCood_Input_File_Path\" and set the corresponding flag to '1'.")

	## scales list of probabilities (famProb) that doesn't add up to 1
	## ie [.2, .2, .4] --> [0.25, 0.25, 0.5]        
	def scale(probList):
		total = sum(probList)
		scaled = [float("{:.6}".format(x/total)) for x in probList]
		warning("'famProb' probabilities did not add to 1 and have been scaled accordingly "\
			"for their current sum, {:.6}. Scaled {} to {}".format(total, probList, scaled))
		return [x/total for x in probList]                

	def zeroInStdDevs(valList):
		for val in valList:
			if float(val) == 0: return True
		
	def checkMinMax(minParam, maxParam, shape):
		for minV, maxV in zip(valueOf(minParam), valueOf(maxParam)):
			if minV == maxV:
				error("\"{}\" and \"{}\" contain equal values for the same {} family. "\
				      "If {} and {} were intended to be the same, use the constant distribution "\
				      "(4) instead.".format(minParam, maxParam, shape, minParam, maxParam, ))
			if minV > maxV:
				error("\"{}\" is greater than \"{}\" in a(n) {} family.".format(minParam, maxParam, shape))
				sys.exit()

	def checkMean(minParam, maxParam, meanParam):
		for minV, meanV in zip(valueOf(minParam), valueOf(meanParam)):
			if minV > meanV: 
				warning("\"{}\" contains a min value greater than its family's mean value in "\
				      "\"{}\". This could drastically increase computation time due to increased "\
				      "rejection rate of the most common fracture sizes.".format(minParam, meanParam))
		for maxV, meanV in zip(valueOf(maxParam), valueOf(meanParam)):
			if maxV < meanV: 
				warning("\"{}\" contains a max value less than its family's mean value in "\
				      "\"{}\". This could drastically increase computation time due to increased "\
				      "rejection rate of the most common fracture sizes.".format(maxParam, meanParam))

	def checkMinFracSize(valList):
		global minFracSize
		for val in valList:
			if val < minFracSize: minFracSize = val
		
			

	## ===================================================================== ##
	##                      Mandatory Parameters                             ##
	## ===================================================================== ##

	## Each of these should be called in the order they are defined in to accomadate for dependecies 
	def nFamEll():
		global ellipseFams 
		## verifyNumValsIs(1, 'nFamEll')
		ellipseFams = verifyInt(valueOf('nFamEll'), 'nFamEll', noNeg = True)
		if ellipseFams == 0:
			warning("You have set the number of ellipse families to 0, no ellipses will be generated.")

	def nFamRect():
		global rectFams
		## verifyNumValsIs(1, 'nFamRect')
		rectFams = verifyInt(valueOf('nFamRect'), 'nFamRect', noNeg = True)
		if rectFams == 0:
			warning("You have set the number of rectangle families to 0, no rectangles will be generated.")

	def stopCondition():
		## verifyNumValsIs(1, 'stopCondition')
		if verifyFlag(valueOf('stopCondition'), 'stopCondition') == 0: 
			nPoly()
		else:
			p32Targets()


	def checkNoDepFlags():
		for flagName in noDependancyFlags:
			verifyFlag(valueOf(flagName), flagName)
		

	## domainSize MUST have 3 non-zero values to define the 
	## size of each dimension (x,y,z) of the domain 
	def domainSize():
		errResult = verifyList(valueOf('domainSize'), 'domainSize', verifyFloat, desiredLength = 3,
				       noZeros = True, noNegs=True)
		if errResult != None:
			error("\"domainSize\" has defined {} value(s) but there must be 3 non-zero "\
			      "values to represent x, y, and z dimensions".format(-errResult))

	def domainSizeIncrease():
		errResult = verifyList(valueOf('domainSizeIncrease'), domainSizeIncrease, verifyFloat, desiredLength = 3)
		if errResult != None:
			error("\"domainSizeIncrease\" has defined {} value(s) but there must be 3 non-zero "\
			      "values to represent extensions in the x, y, and z dimensions".format(-errResult))

		for i,val in enumerate(valueOf('domainSizeIncrease')):
			if val >= valueOf('domainSize')[i]/2:
				error("\"domainSizeIncrease\" contains {} which is more than half of the domain's "
				      "range in that dimension. Cannot change the domain's size by more than half of "
				      "that dimension's value defined in \"domainSize\". This risks collapsing or "
				      "doubling the domain.".format(val))

	def numOfLayers():
		global numLayers
		numLayers = verifyInt(valueOf('numOfLayers'), 'numOfLayers', noNeg = True)
		if numLayers > 0:
			if numLayers != len(params['layers']):
				error("\"layers\" has defined {} layers but \"numLayers\" was defined to "\
				      "be {}.".format(len(params['layers']), numLayers))
			else: layers()

	def layers():
		halfZdomain = params['domainSize'][0][2]/2.0  ## -index[2] becaue domainSize = [x,y,z]
							      ## -center of z-domain at z = 0 so 
							      ##  whole Zdomain is -zDomainSize to +zDomainSize
		for i, layer in enumerate(params['layers']):
			errResult = verifyList(layer, "layer #{}".format(i+1), verifyFloat, desiredLength = 2)
			if errResult != None:
				error("\"layers\" has defined layer #{} to have {} element(s) but each layer must "\
				      "have 2 elements, which define its upper and lower bounds".format(i+1, -errResult))
			if params['layers'].count(layer) > 1:
				error("\"layers\" has defined the same layer more than once.")
			minZ = layer[0]
			maxZ = layer[1]
			if minZ <= -halfZdomain and maxZ <= -halfZdomain:
				error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
				      "below the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
				      "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
				      "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))
			if minZ >= halfZdomain and maxZ >= halfZdomain:
				error("\"layers\" has defined layer #{} to have both upper and lower bounds completely "\
				      "above the domain's z-dimensional range ({} to {}). At least one boundary must be within "\
				      "the domain's range. The domain's range is half of 3rd value in \"domainSize\" "\
				      "(z-dimension) in both positive and negative directions.".format(i+1, -halfZdomain, halfZdomain))

	     
	def disableFram():
		if verifyFlag(valueOf('disableFram'), 'disableFram') == 0:
			h()

	def seed():
		val = verifyInt(valueOf('seed'), 'seed', noNeg = True)
		if val == 0:
			warning("\"seed\" has been set to 0. Random generator will use current wall "\
				"time so distribution's random selection will not be as repeatable. "\
				"Use an integer greater than 0 for better repeatability.")
		params['seed'][0] = val
		

	def ignoreBoundaryFaces():
		if verifyFlag(valueOf('ignoreBoundaryFaces'), 'ignoreBoundaryFaces') == 0:
			boundaryFaces()

	def rejectsPerFracture():
		val = verifyInt(valueOf('rejectsPerFracture'), 'rejectsPerFracture', noNeg = True)
		if val == 0:
			val = 1
			warning("changing \"rejectsPerFracture\" from 0 to 1. Can't ensure 0 rejections.")

		params['rejectsPerFracture'][0] = val 
		
	def famProb():
		errResult = verifyList(valueOf('famProb'), 'famProb', verifyFloat,
				       desiredLength = ellipseFams + rectFams, noZeros = True, noNegs = True)
		if errResult != None:
			error("\"famProb\" must have {} (nFamEll + nFamRect) non-zero elements,"\
			      "one for each family of ellipses and rectangles. {} probabiliies have "\
			      "been defined.".format(ellipseFams + rectFams, -errResult))

		probList = [float(x) for x in valueOf('famProb')]
		if sum(probList) != 1:
			scale(probList)

	def userDefined():
		userEs = "userEllipsesOnOff"
		userRs = "userRectanglesOnOff"
		recByCoord = "userRecByCoord"
		ePath = "UserEll_Input_File_Path"
		rPath = "UserRect_Input_File_Path"
		coordPath = "RectByCood_Input_File_Path"
		invalid = "\"{}\" is not a valid path."

		if verifyFlag(valueOf(userEs), userEs) == 1 and not os.path.isfile(valueOf(ePath)):
			error(invalid.format(ePath))
		if verifyFlag(valueOf(userRs), userRs) == 1 and not os.path.isfile(valueOf(rPath)):
			error(invalid.format(rPath))
		if verifyFlag(valueOf(recByCoord), recByCoord) == 1 and not os.path.isfile(valueOf(coordPath)):
			error(invalid.format(coordPath))    

	def aperture():
		apOption = verifyInt(valueOf('aperture'), 'aperture')

		if apOption == 1:
			if verifyFloat(valueOf('meanAperture'), 'meanAperture', noNeg=True) == 0:
				error("\"meanAperture\" cannot be 0.")
			if verifyFloat(valueOf('stdAperture'), 'stdAperture', noNeg=True) == 0:
				error("\"stdAperture\" cannot be 0. If you wish to have a standard deviation "\
				      "of 0, use a constant aperture instead.") 

		elif apOption == 2:
			verifyList(valueOf('apertureFromTransmissivity'), 'apertureFromTransmissivity', 
				   verifyFloat, desiredLength = 2, noNegs=True)
			if valueOf('apertureFromTransmissivity')[0] == 0:
				error("\"apertureFromTransmissivity\"'s first value cannot be 0.")
			if valueOf('apertureFromTransmissivity')[1] == 0:
				warning("\"apertureFromTransmissivity\"'s second value is 0, which will result in a constant aperature.")

		elif apOption == 3:
			if verifyFloat(valueOf('constantAperture'), 'constantAperture', noNeg=True) == 0:
				params['constantAperture'][0] = 1e-25
				warning("\"constantAperture\" was set to 0 and has been changed "\
				      "to 1e-25 so fractures have non-zero thickness.")

		elif apOption == 4:
			verifyList(valueOf('lengthCorrelatedAperture'), 'lengthCorrelatedAperture', 
				   verifyFloat, desiredLength = 2, noNegs=True)
			if valueOf('lengthCorrelatedAperture')[0] == 0:
				error("\"lengthCorrelatedAperture\"'s first value cannot be 0.")
			if valueOf('lengthCorrelatedAperture')[1] == 0:
				warning("\"lengthCorrelatedAperture\"'s second value is 0, which will result in a constant aperature.") 
				
		else:
			error("\"aperture\" must only be option 1 (log-normal), 2 (from transmissivity), "\
			      "3 (constant), or 4 (length correlated).")

	def permeability():
		if verifyFlag(valueOf('permOption'), 'permOption') == 1:
			if verifyFloat(valueOf('constantPermeability'), 'constantPermeability') == 0:
				params['constantPermeability'][0] = 1e-25
				warning("\"constantPermeability\" was set to 0 and has been changed "\
				      "to 1e-25 so fractures have non-zero permeability.")
			    

	## ========================================================================= ##
	##                      Non-Mandatory Parameters                             ##
	## ========================================================================= ##

	def nPoly():
		val = verifyInt(valueOf('nPoly'), 'nPoly', noNeg = True)
		if val == 0: error("\"nPoly\" cannot be zero.")
		params['nPoly'][0] = val

	def p32Targets():
		global ellipseFams, rectFams
		errResult = None if (ellipseFams == 0) else verifyList(valueOf('e_p32Targets'), 'e_p32Targets', \
							      verifyFloat, desiredLength =  ellipseFams, noNegs=True, noZeros=True)
		if errResult != None:
			error("\"e_p32Targets\" has defined {} p32 values but there is(are) {} ellipse family(ies). "\
			      "Need one p32 value per ellipse family.".format(-errResult, ellipseFams))

		errResult = None if (rectFams == 0) else verifyList(valueOf('r_p32Targets'), "r_p32Targets", \
							    verifyFloat, desiredLength =  rectFams, noNegs=True, noZeros=True)
		if errResult != None:
			error("\"r_p32Targets\" has defined {} p32 value(s) but there is(are) {} rectangle "\
			      "family(ies). Need one p32 value per rectangle family)".format(-errResult, rectFams))

	def f(theta, t, a, b):
		return 1.0/np.sqrt( (a*np.sin(theta))**2 + (b*np.cos(theta)**2))

	def h_shapeCheck(aspect, minRadius, num_points=4):
		# Major and Minor Axis of Ellipse
		## aspect = 1.0 ## param
		r = minRadius

		## TODO check > 3h 
		a = aspect
		b = 1.0

		# approximation of total arclength
		c = np.pi*(a + b)*(1.0 + (3.0*  ((a - b)/(a + b))**2)/(10. + np.sqrt(4. - 3.* ((a - b)/(a + b))**2)))

		#number of points
		n = num_points
		# expected arclength
		ds = c/n

		# array of steps
		steps = np.linspace(0,c,n+1)
		# Numerically integrate arclength ODE
		theta = odeint(f, 0, steps, args=(a, b), rtol = 10**-10)

		# Convert theta to x and y
		x = a*r*np.cos(theta)
		y = b*r*np.sin(theta)

		# Check Euclidean Distance between consectutive points
		h_min = 99999999999
		for i in range(1,n):
			for j in range(i,n):
				if (i != j):
					h_current =np.sqrt((x[i] - x[j])**2 + (y[i] - y[j])**2) 
					if (h_current < h_min):
						h_min = h_current

		return h_min

	def comparePtsVSh(prefix, hval):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		aspectList = params[prefix+"aspect"][0]
		numPointsList = None

		if shape == "ellipse":
			numPointsList = params['enumPoints'][0]
			
		## indicies for each list as we check for ellipse generating features less than h
		numLog = 0
		numTPL = 0
		numEXP = 0
		numConst = 0
		numAspect = 0

		for distrib in params[prefix+'distr'][0]:
			if distrib in [1,2,3,4]:
				if distrib == 1:
					minRad = params[prefix+'LogMin'][0][numLog]
					numLog += 1
				elif distrib == 2:
					minRad = params[prefix+'min'][0][numTPL]
					numTPL += 1
				elif distrib == 3:
					minRad = params[prefix+'ExpMin'][0][numEXP]
					numEXP += 1
				elif distrib == 4:
					minRad = params[prefix+'const'][0][numConst]
					numConst += 1  
				if shape == "ellipse":
					hmin = h_shapeCheck(float(aspectList[numAspect]), float(minRad), int(numPointsList[numAspect]))
				else:
					hmin = h_shapeCheck(float(aspectList[numAspect]), float(minRad)) ## dont need numPoints for rectangle, default 4

				if hmin < (3 * hval):
					error(shape + " family #{} has defined a shape with features too small for meshing. Increase the aspect "\
						     "ratio or minimum radius so that no 2 points of the polygon create a line of length less "\
						     "than 3h".format(numAspect+1))
				     
				numAspect += 1 ## this counts the family number 

	def h():
		val = verifyFloat(valueOf('h'), 'h', noNeg=True)
		if val == 0: error("\"h\" cannot be 0.")
		if val < minFracSize/1000.0 and ellipseFams + rectFams > 0: ####### NOTE ----- future developers TODO, delete the 
									    ## "and ellipseFams + rectFams > 0" once you are also
									    ## checking the userInput Files for minimums that could be 
									    ## "minFracSize".  "minFracSize" is initialized to 99999999 so if no 
									    ## ellipse/rect fams are defined and the only polygons come from user 
									    ## Input, the warning message says the min Frac size is 99999999 
									    ## since it never gets reset by one of the distribution minima.  
			warning("\"h\" (length scale) is smaller than one 1000th of the minimum "\
			      "fracture size ({}). The generated mesh will be extremely fine and will likely be "\
			      "computationally exhausting to create. Computation may take longer than usual.".format(minFracSize))
		if val > minFracSize/10.0:
			warning("\"h\" (length scale) is greater than one 10th of the minimum "\
			      "fracture size ({}). The generated mesh will be very coarse and there will likely "\
			      "be a high rate of fracture rejection.".format(minFracSize))

		comparePtsVSh('e',val)
		comparePtsVSh('r',val)
		
		params['h'][0] = val


	## Must be a list of flags of length 6, one for each side of the domain
	## ie {1, 1, 1, 0, 0, 1} represents --> {+x, -x, +y, -y, +z, -z}
	## DFN only keeps clusters with connections to domain boundaries set to 1
	def boundaryFaces():
		errResult = verifyList(valueOf('boundaryFaces'), 'boundaryFaces', verifyFlag, 6)
		if errResult != None:
			error("\"boundaryFaces\" must be a list of 6 flags (0 or 1), {} have(has) been defined. Each flag "\
			      "represents a side of the domain, {{+x, -x, +y, -y, +z, -z}}.".format(-errResult))

	def enumPoints():
		errResult = verifyList(valueOf('enumPoints'), 'enumPoints', verifyInt, 
				       desiredLength=ellipseFams, noZeros=True, noNegs=True)
		if errResult != None:
			error("\"enumPoints\" has defined {} value(s) but there is(are) {} families of ellipses. Please "\
			      "define one enumPoints value greater than 4 for each ellipse family.".format(-errResult, ellipseFams))
		for val in valueOf("enumPoints"):
			if val <= 4:
				error("\"enumPoints\" contains a value less than or equal to 4. If 4 points were intended, "\
				      "define this family as a rectangle family. No polygons with less than 4 verticies are acceptable.")


	## ========================================================================= ##
	##                      Generalized Mandatory Params                         ##
	## ========================================================================= ##
		    ###                                                ### 
		    ###        Prefix MUST be either 'e' or 'r'        ### 
		    ###                                                ###  
		    ### ============================================== ###        


	def aspect(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		paramName = prefix + "aspect"

		errResult = verifyList(valueOf(paramName), paramName, verifyFloat, 
				desiredLength = numFamilies, noZeros = True, noNegs = True)
		if errResult != None:
			error("\"{}\" has defined {} value(s) but there is(are) {} {} families. Please define one "\
			      "aspect ratio for each family.".format(paramName, -errResult, numFamilies, shape))

	def angleOption(prefix):
		paramName = prefix + "AngleOption"
		verifyFlag(valueOf(paramName), paramName)

	def layer(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		paramName = prefix + "Layer"

		errResult = verifyList(valueOf(paramName), paramName, verifyInt, desiredLength = numFamilies)
		if errResult != None:
			error("\"{}\" has defined {} layer(s) but there is(are) {} {} families. "\
			      "Need one layer per {} family. Layers are numbered by the order they "\
			      "are defined in 'layers' parameter. Layer 0 is the whole domain."\
			      .format(paramName, -errResult, numFamilies, shape, shape))

		for layer in valueOf(paramName):
			if isNegative(int(layer)):
				error("\"{}\" contains a negative layer number. Only values from 0 to "\
				      "{} (numOfLayers) are accepted. Layer 0 corresponds to the entire"\
				      "domain.".format(paramName, numLayers))
			if int(layer) > numLayers:
				error("\"{}\" contains value '{}' but only {} layer(s) is(are) defined. Make sure the "\
				      "layer numbers referenced here are found in that same postion in \"layers\" "\
				      "parameter.".format(paramName, layer, numLayers))

	def thetaPhiKappa(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		paramNames = [prefix + name for name in ["theta", "phi", "kappa"]]
		errString = "\"{}\" has defined {} angle(s) but there is(are) {} {} family(ies)."\
			    "Please defined one angle for each {} family."
		
		for param in paramNames:
			errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = numFamilies)
			if errResult != None:
				error(errString.format(param, -errResult, numFamilies, shape, shape))


	## ========================================================================= ##
	##                        Generalized Distributions                          ##
	## ========================================================================= ##
		    ###                                                ### 
		    ###        Prefix MUST be either 'e' or 'r'        ### 
		    ###                                                ### 
		    ### ============================================== ###        

	## Verifies both the "ebetaDistribution" and "rBetaDistribution". If either contain any flags
	## indicating contant angle (1) then the corresponding "ebeta" and/or "rbeta" parameters are 
	## also verified. 
	def betaDistribution(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		paramName = prefix + "betaDistribution"

		errResult = verifyList(valueOf(paramName), paramName, verifyFlag, desiredLength = numFamilies)
		if errResult != None:
			error("\"{}\" has defined {} value(s) but there is(are) {} {} family(ies). Need one "\
			      "flag (0 or 1) per {} family.".format(paramName, -errResult, numFamilies, shape, shape))

		numBetas = valueOf(paramName).count(1) ## number of 1's in list
		if numBetas == 0: return

		betaParam = prefix + "beta"
		errResult = verifyList(valueOf(betaParam), betaParam, verifyFloat, desiredLength = numBetas)
		if errResult != None:
			error("\"{}\" defined {} constant angle(s) but {} flag(s) was(were) set to 1 "\
			      "in {}. Please define one constant angle (beta value) for each flag set "\
			      "to 1 in \"{}\"".format(betaParam, -errResult, numBetas, paramName, paramName))


	## Verifies "edistr" and "rdistr" making sure one disrtibution is defined per family and
	## each distribution is either 1 (log-normal), 2 (Truncated Power Law), 3 (Exponential), or 4 (constant).
	## 
	## Stores how many of each distrib are in use in numEdistribs or numRdistribs lists  
	def distr(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		distribList = numEdistribs if prefix is 'e' else numRdistribs
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		paramName = prefix + "distr"

		errResult = verifyList(valueOf(paramName), paramName, verifyInt, desiredLength = numFamilies)
		if errResult != None:
			error("\"{}\" has defined {} distributions but there are {} {} families. " \
				"Need one distribution per family (1 = lognormal, 2 = Truncated Power Law, "
				"3 = Exponential, or 4 = constant).".format(paramName, -errResult, numFamilies, shape)) 
		try:
			for dist in valueOf(paramName):
				if int(dist) <= 0: raise IndexError()
				distribList[int(dist)] += 1  
		except IndexError:
			error("\"{}\" contains '{}' which is not a valid distribution option. " \
			       "Only values 1 through 4 can define a family's distribution (1 = lognormal, " \
			       "2 = Truncated Power Law, 3 = Exponential, or 4 = constant).".format(paramName, dist))


	# prefix- "e" or "r"
	## Verifies all logNormal Paramters for ellipses and Rectangles        
	def lognormalDist(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		distribList = numEdistribs if prefix is 'e' else numRdistribs
		paramNames = [prefix + name for name in ["LogMean", "sd", "LogMin", "LogMax"]]
		errString = "\"{}\" has defined {} value(s) but {} lognormal distrbution(s) was(were) " \
			    "defined in \"{}\". Please define one value for each lognormal (distrib. #1) family."

		for param in paramNames:
			zTmp = True if "sd" not in param else False  ## Turns off noZeros check only for 'sd' for better error msg
			errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[1],
						noZeros = zTmp, noNegs = True)         
			if errResult != None:
				error(errString.format(param, -errResult, distribList[1], prefix+'distr'))

		sdParam = prefix + "sd"
		if zeroInStdDevs(valueOf(sdParam)): 
			error("\"{}\" list contains a standard deviation of 0. If this was intended, " \
				"use the constant distribution (4) instead. Otherwise, make sure \"{}\" " \
				"only contains values greater than 0.".format(sdParam, sdParam))

		checkMinMax(prefix+"LogMin", prefix+"LogMax", shape)
		checkMean(prefix+"LogMin", prefix+"LogMax", prefix+"LogMean")
		checkMinFracSize(valueOf(prefix+"LogMin"))

	## Truncated Power Law Distribution
	def tplDist(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		distribList = numEdistribs if prefix is 'e' else numRdistribs
		paramNames = [prefix + name for name in ["min", "max", "alpha"]]
		errString = "\"{}\" has defined {} value(s) but {} truncated power-law distrbution(s) was(were) " \
			    "defined in \"{}\". Please define one value for each truncated power-law (distrib. #2) family."

		for param in paramNames:
			errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[2], 
						noZeros = True, noNegs = True)
			if errResult != None:
				error(errString.format(param, -errResult, distribList[2], prefix+'distr'))
				
		checkMinMax(prefix+"min", prefix+"max", shape)
		checkMinFracSize(valueOf(prefix+"min"))
		

	def exponentialDist(prefix):
		shape = "ellipse" if prefix is 'e' else "rectangle"
		distribList = numEdistribs if prefix is 'e' else numRdistribs
		paramNames = [prefix + name for name in ["ExpMean", "ExpMin", "ExpMax"]]
		errString = "\"{}\" has defined {} value(s) but {} exponential distrbution(s) was(were) " \
			    "defined in \"{}\". Please define one value for each exponential (distrib. #3) family."

		for param in paramNames:
			errResult = verifyList(valueOf(param), param, verifyFloat, desiredLength = distribList[3], 
						noZeros = True, noNegs = True)
			if errResult != None:
				error(errString.format(param, -errResult, distribList[3], prefix+'distr'))
				
		checkMinMax(prefix+"ExpMin", prefix+"ExpMax", shape)
		checkMean(prefix+"ExpMin", prefix+"ExpMax", prefix+"ExpMean")
		checkMinFracSize(valueOf(prefix+"ExpMin"))

	def constantDist(prefix):
		paramName = prefix + "const"
		numFamilies = ellipseFams if prefix is 'e' else rectFams
		distribList = numEdistribs if prefix is 'e' else numRdistribs

		errResult = verifyList(valueOf(paramName), paramName, verifyFloat, desiredLength = distribList[4],
					 noZeros = True, noNegs = True)
		if errResult != None:
			error("\"{}\" has defined {} value(s) but {} constant distrbution(s) was(were) " \
			      "defined in \"{}\". Please define one value for each family with a constant (distrib. "\
			      "#4) distribution.".format(paramName, -errResult, distribList[4], prefix + 'distr'))
	     
		checkMinFracSize(valueOf(paramName))
		

	## ========================================================================= ##
	##                      Main for I/O Checkin and Writing                     ##
	## ========================================================================= ##

	def checkIOargs(ioPaths):
		try:
			ioPaths["input"] = sys.argv[1]
		except IndexError:
			error("Please provide an input file path as the first command line argument.\n"\
			      "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")

		try:
			ioPaths["output"] = sys.argv[2]
		except IndexError:
			ioPaths["output"] = "polishedOutput.txt"
			warning("No output path has been provided so output will be written to "\
				"\"polishedOutput.txt\" in your current working directory.")

	def parseInput():
		for line in inputIterator:
			line = extractParameters(line) ## this strips comments
			if (line != "" and ":" in line):
				processLine(line)
		needed = [unfound for unfound in unfoundKeys if unfound in mandatory]
		if needed != []:
			errString = ""
			for key in needed: errString += "\t\"" + key + "\"\n"
			error("Missing the following mandatory parameters: \n{}".format(errString))    
	 
	    
	def verifyParams():
		firstPriority = [nFamEll, nFamRect, stopCondition, domainSize, numOfLayers, 
				 seed, domainSizeIncrease, ignoreBoundaryFaces, rejectsPerFracture, 
				 userDefined, checkFamCount, checkNoDepFlags, famProb]
		generalized = [layer, aspect, angleOption, thetaPhiKappa, betaDistribution, distr]
		distribs = [lognormalDist, tplDist, exponentialDist, constantDist]
		checkLast = [disableFram, aperture, permeability]
		
		for paramFunc in firstPriority: paramFunc()

		if rectFams > 0:
			for paramFunc in generalized: paramFunc('r')  
		if ellipseFams > 0:
			enumPoints()
			for paramFunc in generalized: paramFunc('e')              

		for i, paramFunc in enumerate(distribs):
			if numEdistribs[i+1] > 0: paramFunc('e') ## only call if there have been 1+ of a distrib defined
			if numRdistribs[i+1] > 0: paramFunc('r') ## +1 for reason stated in list instantiation above
			
		for paramFunc in checkLast: paramFunc()

	def writeBack():
		for param in params:
			if param == 'layers':
				writer.write(param + ': ')
				for layer in params['layers']:
					writer.write(listToCurly(str(layer)) + " ")
				writer.write('\n')    
			elif type(valueOf(param, writing=True)) is list:
				curl = listToCurly(str(valueOf(param, writing = True)))
				writer.write(param + ': ' + curl + '\n')
			else:
				writer.write(param + ': ' + str(valueOf(param, writing=True)) + '\n')              
		
	     
	ioPaths = {"input":"", "output":""}
	try:
		ioPaths["input"] = input_file
	except IndexError:
		error("Please provide an input file path as the first command line argument.\n"\
		      "    $ python3 inputParser.py [inputPath] [outputPath (Optional)]")
	try:
		ioPaths["output"] = output_file
	except IndexError:
		ioPaths["output"] = "polishedOutput.txt"
		warning("No output path has been provided so output will be written to "\
			"\"polishedOutput.txt\" in your current working directory.")
	try:
		reader = open(ioPaths["input"], 'r')
		writer = open(ioPaths["output"], 'w')
		inputIterator = iter(reader)
	except FileNotFoundError:
		error("Check that the path of your input file is valid.")
       
	parseInput()
	verifyParams()
	writeBack()

def dfnGen_output_report(radiiFile = 'radii.dat', famFile ='families.dat', transFile='translations.dat', rejectFile = 'rejections.dat'):

	"""
	Notes
	1. Set the number of histogram buckets (bins) by changing numBuckets variable in his graphing functions
	2. Also change number of x-values used to plot lines by changing numXpoints variable in appropriate funcs
	3. Set show = True to show plots immediately and still make pdf
	4. NOTE future developers of this code should ass functionality for radiiList of size 0. 

	"""

	from scipy.stats import norm, lognorm, powerlaw
	from matplotlib.ticker import FormatStrFormatter
	from matplotlib.backends.backend_pdf import PdfPages
	import matplotlib.pyplot as plt
	import matplotlib.mlab as mlab
	import numpy as np
	import scipy, sys, math, re

	families = {'all':[], 'notRemoved':[]} ## families['all'] contains all radii.   
					       ## families['notRemoved'] contains all non-isolated fractures. 
					       ##   Isolated fracs get removed from DFN and have 'R' at end  
					       ##   of input file line
					       ## families['1','2','3' etc] correspond to a polyFam object\

	outputPDF = PdfPages('output_report.pdf') ## TODO to make this cmd line option --> outputPDF = PdfPages(sys.argv[5])
	show = False ## Set to true for showing plots immediately instead of having to open pdf. Still makes pdf

	class polyFam:
		def __init__(self, globFamNum, radiiList, distrib, infoStr, parameters):
			self.globFamNum = globFamNum
			self.radiiList = radiiList
			self.distrib = distrib
			self.infoStr = infoStr
			self.parameters = parameters

		def printPolyFam(self):
			print("famNum:\n", self.globFamNum)
			print("\nradiiList:\n",self.radiiList)
			print("\ndistrib:\n", self.distrib)
			print("\ninfoStr:\n", self.infoStr)
			print("\nparameters:\n", self.parameters)
			print("\n\n")
		       

	## Rejection File line format:   "118424 Short Intersections" --> {"Short Intersections": 118424}
	def graphRejections(rejectFile):
		if len(sys.argv) < 5: return ## Dont provide rejection plot if no rejection file
		rejects = {}
		plt.subplots()

		for line in rejectFile:
			num = int(line[:line.index(" ", 0)]) ## number comes before first space in line
			name = line[line.index(" ", 0) + 1:].strip() ## name comes after first space
			midSpaceIndex = 1
			while midSpaceIndex < len(name) / 2 and " " in name[midSpaceIndex+1:]: ## cut long names in half
				midSpaceIndex = name.index(" ", midSpaceIndex + 1)
			name = name[:midSpaceIndex] + "\n" + name[midSpaceIndex+1:]
			rejects[name] = num
		
		totalRejects = float(sum(rejects.values())) 
		figWidth = max(rejects.values()) * 1.25 ## make width 25% bigger than biggest val
		labelOffset = figWidth * 0.02 if figWidth != 0 else 0.05   
		offset = 2
		h = 0.35   # height of horiz bar (vertical thickness)

		horizBar = plt.barh(np.arange(len(rejects)) + offset, rejects.values(), height=h, align='center')
		plt.yticks(np.arange(len(rejects)) + offset, rejects.keys(), fontsize=6)
		plt.title("Rejection Reasons", fontsize=18)
		plt.xlim(xmin=0, xmax=figWidth if figWidth != 0 else 1)        

		for bar in horizBar:
			width = bar.get_width()
			if width != 0:
				label = '{0:d}\n{1:.2f}%'.format(int(width), width / totalRejects * 100)
			else: label = 0
			plt.text(bar.get_width()+labelOffset, bar.get_y()+h/2.0, label, va='center', fontsize=10)

		plt.gcf().subplots_adjust(right=0.98)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()


	## Histogram making helper function for graphTranslations()
	def transHist(prefix, allList, unRemovedList):
		plt.subplots()
		numBuckets = 20
		minSize = min(allList)
		maxSize = max(allList)
		plt.hist(allList, bins=numBuckets, color='b', range=(minSize, maxSize), alpha=0.7, 
			 label='All Fractures\n(Connected and Unconnected')
		plt.hist(unRemovedList, bins=numBuckets, color='r', range=(minSize, maxSize), alpha=0.7, 
			 label='Non-isolated fractures (connected)')
		plt.title(prefix + "-Position Distribution")
		plt.xlabel("Fracture Position (Spatial Coordinate)")
		plt.ylabel("Number of Fractures")
		plt.legend(loc="upper center")
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

	## Graphs position of fractures as histogram for x, y and z dimensions
	## Input file format:    Xpos Ypos Zpos (R) [R is optional, indicates it was removed due to isolation]
	def graphTranslations():
		xAll = []
		xUnremoved = []
		yAll = []
		yUnremoved = []
		zAll = []
		zUnremoved = []

		for line in transFile:
			line = line.split(" ")
			try:
				xAll.append(float(line[0]))
				yAll.append(float(line[1]))
				zAll.append(float(line[2].strip()))
				if len(line) < 4:           ## no 'R' at end of line 
					xUnremoved.append(float(line[0]))
					yUnremoved.append(float(line[1]))
					zUnremoved.append(float(line[2].strip()))                 
			except ValueError:
				continue

		transHist('X', xAll, xUnremoved)
		transHist('Y', yAll, yUnremoved)
		transHist('Z', zAll, zUnremoved)
		

	def collectFamilyInfo():
		famObj = polyFam(0, [], 0, "", {})
		possibleParams = ["Mean", "Standard Deviation", "Alpha", "Lambda"]
		bounds = ["Minimum Radius", "Maximum Radius"]

		for line in famFile:
			if line.strip() == "":
				if famObj.distrib == "Constant":
					famObj.infoStr += "\nConstant distribution, only contains one radius size.\n"\
							   "No distribution graphs will be made for this family."

				famObj = polyFam(0, [], 0, "", {}) ## create new famObj for next family
			
			else:   ## append all info to info sting 
				famObj.infoStr += line

			if "Global Family" in line:
				## input format:     Global Family 1
				famNum = line[line.index("y") + 1:].strip()
				famObj.globFamNum = famNum
				families[famNum] = famObj
			elif "Distribution:" in line:
				## input format:     Distribution: "distribution name"
				famObj.distrib = line[line.index(":") + 1:].strip()
			elif ":" in line and line[:line.index(":")].strip() in possibleParams:
				## if one of the distribution param names is in the line, 
				##   match the name to the value and store in parameters attribute
				## Mean: 0.5 ----> famObj.parameters["Mean"] = 0.5
				paramList = line.split(":")
				famObj.parameters[paramList[0].strip()] = float(paramList[1].strip())
			elif ":" in line and line[:line.index(":")].strip() in bounds:
				## get min/max radius & convert 10m -> 10
				paramList = line.split(":")            
				famObj.parameters[paramList[0]] = float(re.sub("m", "", paramList[1]).strip())

			## ======== Jeffrey, this is where you can add the family building parser code ====== #
			## elif ":" in line:
			##          paramList = line.split(":")
			##          family parameter name = paramList[0]
			##          parameter value = paramList[1]
			## 
			## Just add all necessary attributes to the polyFam class and you should be good to go

		## Also add each object to global and not Removed if not empty
		## input file's line format:   xRadius yRadius Family# Removed (Optional)

		for line in radiiFile:
			try:
				elems = line.split(' ')
				radius = float(elems[0])
				famNum = elems[2].strip()
				families['all'].append(radius)
				if len(elems) < 4:              ## len = 4 when 'R' is on line
					families['notRemoved'].append(radius)
				if famNum not in families: 
					families[famNum].radiiList = [radius]
				else:
					families[famNum].radiiList.append(radius)
			except ValueError:
				continue

		for fam in families:
			if fam != 'all' and fam != 'notRemoved':
				pass # families[fam].printPolyFam()


	############# Histogram & PDF ##############
	## histogram of sizes (from data) and PDF (from input parameters
	## returns histHeights (height of all hist bars) for plotting cdf
	##         & list of x values of binCenters (also for cdf)
	def histAndPDF(radiiSizes, pdfArray, xmin, xmax, xVals):
		numBuckets = 100
		fig, histo = plt.subplots()
		### fig = plt.figure(figsize=(8., 6.), dpi=500)  ## comment out if you dont want pdf
		## histo = plt.ax_stack()

		## plot hist, set xtick labels
		histHeights, binEdges, patches = histo.hist(radiiSizes, numBuckets, normed=1, color='r',
									alpha=0.75, label='Empirical data')
		binCenters = [((binEdges[x] + binEdges[x+1]) / 2.0) for x in range(len(binEdges)-1)] ## need for cdf
			     ## ^ -1 to prevent Index Error when calculating last bin Center
		histo.set_xticks(binEdges)
		histo.locator_params(tight = True, axis = 'x', nbins = numBuckets/8.0) ## num of axis value labels
		histo.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
		
		## now plot pdf over histogram
		plt.plot(xVals, pdfArray, 'k', linewidth=4, label='Analytical PDF from input parameters')
		plt.xlabel("Fracture Radius")
		plt.ylabel("Probability Density")
		plt.legend()
		plt.grid()
		plt.tight_layout()
		plt.subplots_adjust(top=0.87)

		return histHeights, binCenters

	############# CDF ##############
	## 2 cdfs, analytical (from pdf from given mu and sigma) and empirical (from histogram)
	def cdfs(histHeights, binCenters, pdf, xmin, xmax, xVals):
		plt.subplots()
		analyticCDF = 1. * np.cumsum(pdf) / sum(pdf)      
		empiricalCDF = 1. * np.cumsum(histHeights) / sum(histHeights) ## need these to correspond to xVals
		plt.plot(xVals, analyticCDF, 'b', label='Analytic CDF (from input)')
		plt.plot(binCenters, empiricalCDF, 'r', label='Empirical CDF (from data)')
		plt.title("CDF of Empirical Data & Analytical PDF from Input Parameters")
		plt.legend(loc="lower right")
		plt.xlabel("Fracture Size")
		plt.ylabel("Probability Density")
		plt.grid()
		plt.tight_layout()
		plt.subplots_adjust(top=0.9)

	############# Q & Q  ##############
	## histogram values (x) vs. analytical PDF values (y) & a line showing ideal 1 to 1 ratio
	def qq(trueVals, histHeights):
		fig, ax = plt.subplots()
		qq = plt.scatter(histHeights, trueVals, c='r', marker='o', 
				 label="x=Empirical value\ny=Analtical PDF value")
		minMax = [np.min([min(trueVals), min(histHeights)]),  # min of both axes
			  np.max([max(trueVals), max(histHeights)])]  # max of both axes
		plt.plot(minMax, minMax, 'k-', alpha=0.75, zorder=0, label="y/x = 1") ## 1 to 1 ratio for reference
		plt.legend(loc="lower right")
		plt.title("Q-Q Plot of Data vs.Analytical Distrbution At Same Point (Bin Center)")
		plt.xlabel("Probability Density of Data")
		plt.ylabel("Probability Density on Analytical PDF")
		plt.grid()
		plt.tight_layout()
		plt.subplots_adjust(top=0.9)

	def lognormCDF(x, mu, sigma):
		return 0.5 + (0.5 * scipy.special.erf( (np.log(x) - mu) / (np.sqrt(2) * sigma) ) )
	       
	def graphLognormal(famObj):
		numXpoints = 1000
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		mu, sigma = famObj.parameters["Mean"], famObj.parameters["Standard Deviation"]
		normConstant = 1.0
		try:       
			normConstant = 1.0 / (lognormCDF(xmax, mu, sigma) - lognormCDF(xmin, mu, sigma))
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
			pass  
		lognormPDFVals = [x * normConstant for x in lognorm.pdf(xVals, sigma, loc=mu)]

		histHeights, binCenters = histAndPDF(famObj.radiiList, lognormPDFVals, xmin, xmax, xVals) 
		plt.title("Histogram of Obtained Radii Sizes & Lognormal Distribution PDF."\
			  "\nFamily #" + famObj.globFamNum)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, lognormPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		trueVals = [lognorm.pdf(binCenters[i], sigma, loc=mu) for i in range(len(binCenters))]
		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()
	  
	      
	def powLawPDF(normConst, xmin, x, a):
		return normConst * ( (a*(xmin**a)) / float(x**(a+1)) ) 

	def powLawCDF(x, xmin, a):
		return 1 - ( (xmin / float(x))**a ) 

	def graphTruncPowerLaw(famObj):
		numBuckets = 100
		numXpoints = 1000
		alpha = famObj.parameters["Alpha"]
		radiiSizes = famObj.radiiList
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		normConst = 1.0
		try:
			normConst = 1.0 / (powLawCDF(xmax, xmin, alpha) - powLawCDF(xmin, xmin, alpha))
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
			pass        
		powLawPDFVals = [powLawPDF(normConst, xmin, x, alpha) for x in xVals]

		histHeights, binCenters = histAndPDF(radiiSizes, powLawPDFVals, xmin, xmax, xVals)
		plt.title("Histogram of Obtained Radii Sizes & Truncated Power Law Distribution PDF."\
			  "\n Family #" + famObj.globFamNum)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, powLawPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		trueVals = [powLawPDF(normConst, xmin, binCenters[i], alpha) for i in range(len(binCenters))]

		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()



	def expPDF(normConst, eLambda, x):
		return normConst * eLambda * np.e**(-eLambda*x)

	def expCDF(eLambda, x):
		return 1 - (np.e**(-eLambda*x))
		
	def graphExponential(famObj):
		numXpoints = 1000
		numBuckets = 100
		radiiSizes = famObj.radiiList
		eLambda = famObj.parameters["Lambda"]
		xmin = min(famObj.radiiList) ##parameters["Minimum Radius"] Use list max because distrib doesnt always get
		xmax = max(famObj.radiiList) ##parameters["Maximum Radius"]   the desired max value.
		xVals = np.linspace(xmin, xmax, numXpoints)
		normConst = 1.0
		try:
			normConst = 1.0 / ( expCDF(eLambda, xmax) - expCDF(eLambda, xmin) )
		except ZeroDivisionError: ## happens when there is only one fracture in family so ^ has 0 in denominator
			pass          
		expPDFVals = [expPDF(normConst, eLambda, x) for x in xVals]

		histHeights, binCenters = histAndPDF(radiiSizes, expPDFVals, xmin, xmax, xVals)
		plt.title("Histogram of Obtained Radii Sizes & Exponential Distribution PDF."\
			  "\nFamily #" + famObj.globFamNum) 
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		cdfs(histHeights, binCenters, expPDFVals, xmin, xmax, xVals)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()

		trueVals = [expPDF(normConst, eLambda, binCenters[i]) for i in range(len(binCenters))]
		qq(trueVals, histHeights)
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()


	def graphConstant(famObj):
		#print("  Family #" + famObj.globFamNum + " is a constant distribution and only contains one radius size.")
		pass

	def graphAllAndNotRemoved():
		numBuckets = 50
		allList = families['all'] 
		unRemovedList = families['notRemoved']
		minSize = min(allList)
		maxSize = max(allList)
		twentiethOfWidth = (maxSize - minSize) * 0.05
		fig, ax = plt.subplots()
		histCount, bins, patches = plt.hist(allList, bins=numBuckets, color='b', range=(minSize, maxSize), 
				  alpha=0.7, label='All Fractures\n(Connected and Unconnected')

		binWidth = bins[1]-bins[0]
		figHeight = max(histCount) * 1.2 ## need room to show vals above bars
		ax.set_xticks(bins)
		ax.locator_params(tight = True, axis = 'x', nbins = numBuckets/5.0) ## num of axis value labels
		ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

		## if no fractures removed, there's no point in using the same 2 histograms, 
		if len(allList) != len(unRemovedList):
			plt.hist(unRemovedList, bins=numBuckets, color='r', range=(minSize, maxSize), alpha=0.7,
				  label='Non-isolated fractures (connected)')

		## Add y values above all non-zero histogram bars        
		for count, x in zip(histCount, bins):
			if count != 0:
				ax.annotate(str(count), xy=(x, count + (figHeight*0.03)), 
					    rotation='vertical', va='bottom')
		       
		plt.ylim(ymin=0, ymax=figHeight)
		plt.xlim(xmin=minSize-twentiethOfWidth, xmax=maxSize+twentiethOfWidth)
		plt.gcf().subplots_adjust(right=0.98)
		plt.title("Fractures Sizes From All Families")
		plt.xlabel("Fracture Radius")
		plt.ylabel("Number of Fractures")
		plt.legend()
		plt.savefig(outputPDF, format='pdf')
		if show: plt.show()
			
		
	def graphDistribs():
		famNum = 1
		updateStr = "Graphing Family #{} which contains {} fractures."
		graphDistFuncs = {"Lognormal" : graphLognormal,              ## dict of graph functions
				  "Truncated Power-Law" : graphTruncPowerLaw,
				  "Exponential" : graphExponential,
				  "Constant" : graphConstant }
		
		try: 
			while famNum > 0:
				famObj = families[str(famNum)]
				print(updateStr.format(famObj.globFamNum, len(famObj.radiiList)))

				## give info string from families file its own figure
				fig = plt.figure()
				fig.text(.1,.2,famObj.infoStr, fontsize=15, bbox=dict(facecolor='red', alpha=0.5))
				plt.savefig(outputPDF, format='pdf')

				## then graph info 
				graphDistFuncs[famObj.distrib](famObj) ## families' keys are strings
				plt.close("all")
				famNum += 1
		except KeyError: ## throws key error when we've finished the last family number
			pass

	collectFamilyInfo()
        graphTranslations()
        graphDistribs()
        graphAllAndNotRemoved()
        graphRejections()

        outputPDF.close()
        
def dfnGen_make_working_directory(jobname):
    try:
        os.mkdir(jobname)
	os.mkdir(jobname + '/radii')
	os.mkdir(jobname + '/intersections')
	os.mkdir(jobname + '/polys')
    except OSError:
	print '\nFolder ', jobname, ' exists'
	keep = raw_input('Do you want to delete it? [yes/no] \n')
	if keep == 'yes':
		print 'Deleting', jobname 
		rmtree(jobname)
		print 'Creating', jobname 
		os.mkdir(jobname)	
		os.mkdir(jobname + '/radii')
		os.mkdir(jobname + '/intersections')
		os.mkdir(jobname + '/polys')
	elif keep == 'no':
		print 'Exiting Program'
		exit() 
	else:
		print 'Unknown Response'
		print 'Exiting Program'
		exit()
	
def dfnGen_check_input(dfnGen_run_file):

	print '--> Checking input file'	
	copy(dfnGen_run_file, './input.dat')
	dfnGen_parse_input('input.dat')
	print '--> Checking input file complete'	

def dfnGen_create_network(jobname, dfnGen_run_file):
	
	print '--> Running DFNGEN'	
	# copy input file into job folder	
	cmd = '${DFNGENC_PATH}/./main  input_clean.dat ' + jobname
	os.system(cmd)
	if os.path.isfile(jobname+"/params.txt") is False:
	#if os.path.isfile("params.txt") is False:
		print '--> Generation Failed'
		print '--> Exiting Program'
		exit()
	else:
		print '--> Generation Succeeded'

def dfnGen_mesh_network(nCPU):

	print '--> Meshing Network'	
	copy(os.environ['PYTHON_SCRIPTS']+'/dfnGen_meshing.py','dfnGen_meshing.py')
	os.system('$python_dfn dfnGen_meshing.py ' + str(nCPU)) 
	print '--> Meshing Network Complete'	

