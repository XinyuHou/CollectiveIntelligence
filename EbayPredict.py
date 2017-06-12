import httplib
from xml.dom.minidom import parse, parseString, Node

devKey = '9a139841-31c3-4562-b3ad-285ccde838e1'
appKey = 'XinyuHou-MyCollec-SBX-3090330f6-4bb783e7'
certKey = 'SBX-090330f659d5-15f6-4c5f-95eb-e7bf'
userToken = 'AgAAAA**AQAAAA**aAAAAA**dTYOWQ**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GlAZOCpA2dj6x9nY+seQ**xzAEAA**AAMAAA**lPVF/NjD6xZ8mFYBP4P/t7TQ1p9NgeK/oEHMFrDdQ/5Jo7CgvhDCLWMvuMx/vskFpRLqJBzwZMrAlfYKkznWZaxUWsENK524m1+l+T58/HLpwnA9JZzJhCcmz7w0tYaDoJ3ehtkdvTYMqty12Z9cpeVqvPp6OGpcUX0F40c1Cl3IsjMifNjIf6kuigsa1bL5qBA+8MslF678rnnJ431QuoBhcnkZRnjWqtW3qe3rIa2g+LJT+aSAdStnbKY36wFb510+7bNxCCUAAzzsa3wg+o3ISF4xDMosEyuA+wHhA7cI+XwSaJZPeWIvnX9PujyptvFzZSMclY1PAOJUaSUaK+rxvwHAu5zFJ9/zWcwH8FUN6o6p6aEz/GuD3zpwsKyJChGzT4EEKt9v0M6lslTAVTMnIFRFWFc2/yXVvCh6mwkF/Lfw6YcJL+T5Fo1mZ9heqyXSnw2s1IEI6MxRBDl6ezGeEsfduU/uv8nOQagpSMCPYGNtP152Hds8oqKCRkgDDi8SC2VY21BM9yQCSrn3X61J2/59yty8nELH+fEpLyX5SgQRN3mdh21cM135g3xrDc3GGAwI1hksbM6AIvfvC8oxfb8HPAxo8XHpT7t2IDru3D5RrOxOxdisL+Gza+626viAJUhzfCVM8VNqTI8FgQaK5YvPnMdD3mgL1yX1CnHpPEher5YPDtJnYlXErNaUFPXcNDo4IYxxJ6YkHgIR1VyfdrjvcW2jfFTlUw53pd+YigUJpMTXGH0g6J3LMa03'
serverUrl = 'api.ebay.com'

def getHeaders(apiCall, siteID = '0', compatabilityLevel = '433'):
	headers = {
		"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
		"X-EBAY-API-DEV-NAME": devKey,
		"X-EBAY-API-APP-NAME": appKey,
		"X-EBAY-API-CERT-NAME": certKey,
		"X-EBAY-API-CALL-NAME": apiCall,
		"X-EBAY-API-SITEID": siteID,
		"Content-Type": "text/xml"
	}

	return headers

def sendRequest(apiCall, xmlParameters):
	connection = httplib.HTTPSConnection(serverUrl)
	connection.request("POST", '/ws/api.dll', xmlParameters, getHeaders(apiCall))

	response = connection.getresponse()

	if response.status != 200:
		print 'Error sending request:' + response.reason
	else:
		data = response.read()
		connection.close()

	return data

def getSingleValue(node, tag):
	nl = node.getElementsByTagName(tag)
	if len(nl) > 0:
		tagNode = nl[0]
		if tagNode.hasChildNodes():
			return tagNode.firstChild.nodeValue

	return '-1'

def doSearch(query, categoryID=None, page = 1):
	xml = "<?xml version='1.0' encoding='utf-8'?>"+\
		"<findItemsAdvancedRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
		"<RequesterCredentials><eBayAuthToken>" +\
		userToken +\
		"</eBayAuthToken></RequesterCredentials>" + \
		"<Pagination>"+\
		  "<EntriesPerPage>200</EntriesPerPage>"+\
		  "<PageNumber>"+str(page)+"</PageNumber>"+\
		"</Pagination>"+\
		"<keywords>" + query + "</keywords>"
	if categoryID != None:
		xml += "<CategoryID>" + str(categoryID) + "</CategoryID>"

	xml += "</findItemsAdvancedRequest>"

	data = sendRequest('findItemsAdvanced', xml)
	response = parseString(data)
	itemNodes = response.getElementsByTagName('Item')
	results = []
	print data
	for item in itemNodes:
		itemId = getSingleValue(item, 'ItemID')
		itemTitle = getSingleValue(item, 'Title')
		itemPrice = getSingleValue(item, 'CurrentPrice')
		itemEnds = getSingleValue(item, 'EndTime')

		results.append((itemId, itemTitle, itemPrice, itemEnds))

	return results

def getCategory(query='',parentID=None,siteID='0'):
  lQuery = query.lower()
  xml = "<?xml version='1.0' encoding='utf-8'?>"+ \
		"<findItemsAdvancedRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+ \
		"<RequesterCredentials><eBayAuthToken>" + \
		userToken + \
		"</eBayAuthToken></RequesterCredentials>"+ \
		"<DetailLevel>ReturnAll</DetailLevel>"+ \
		"<ViewAllNodes>true</ViewAllNodes>"+ \
		"<CategorySiteID>" + siteID + "</CategorySiteID>"
  if parentID == None:
	xml += "<LevelLimit>1</LevelLimit>"
  else:
	xml += "<CategoryParent>" + str(parentID) + "</CategoryParent>"
  xml += "</findItemsAdvancedRequest>"
  data = sendRequest('findItemsAdvanced', xml)
  categoryList = parseString(data)
  catNodes = categoryList.getElementsByTagName('Category')
  for node in catNodes:
	catId = getSingleValue(node, 'CategoryID')
	name = getSingleValue(node, 'CategoryName')
	if name.lower().find(lQuery) != -1:
	  print catId, name


