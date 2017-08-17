#!/usr/bin/env python

import os, requests, json, ConfigParser, csv
from codecs import encode

config = ConfigParser.ConfigParser()
config.read("local_settings.cfg")

dictionary = {"baseURL": config.get("ArchivesSpace", "baseURL"), "repository":config.get("ArchivesSpace", "repository"), "user": config.get("ArchivesSpace", "user"), "password": config.get("ArchivesSpace", "password")}
repositoryBaseURL = "{baseURL}/repositories/{repository}".format(**dictionary)
resourceURL = "{baseURL}".format(**dictionary)

# authenticates the session
auth = requests.post("{baseURL}/users/{user}/login?password={password}&expiring=false".format(**dictionary)).json()
headers = {"X-ArchivesSpace-Session":auth["session"]}

spreadsheet = os.path.join(config.get("Destinations", "directory"), config.get("Destinations", "filename"))
	
def get_note_contents(resource, array, note_type):
	notes = resource["notes"]
	content_list = []
	for note in notes:
		try:
			if note["type"] == note_type:
				if note["jsonmodel_type"] == "note_singlepart":
					content_list.append(note["content"].encode('utf-8'))
				else:
					content_list.append(note["subnotes"][0]["content"].encode('utf-8'))
		except:
			pass
	return " | ".join(content_list)

def get_values(resource, array, value):
	value_types = []
	for item in resource[array]:
		if item[value]:
			value_types.append(item[value])
		else:
			value_types.append("false")
	return " | ".join(value_types)

def get_single_value(resource, key):
	d = resource
	if key in d:
		return d.get(key)
	else:
		return "false"

def get_values_list(resource, array, value):
	value_types = []
	for item in resource[array]:
		if item[value]:
			value_types.append(item[value])
		else:
			value_types.append("false")
	return value_types

def makeRow(resource):
	global row
	row = []
	publish = get_single_value(resource, "publish")
	title = get_single_value(resource, "title").encode('utf-8')
	resource_id = get_single_value(resource, "id_0")
	extent = get_values(resource, "extents", "number")
	date_labels = get_values(resource, "dates", "label")
	language = get_single_value(resource, "language")
	repository = get_single_value(resource, "repository")
	level = get_single_value(resource, "level")

	agent = get_values(resource, "linked_agents", "role")
	subjects = get_values_list(resource, "subjects", "ref")
	
	scope = get_note_contents(resource, "notes", "scopecontent")
	access = get_note_contents(resource, "notes", "accessrestrict")
	abstract = get_note_contents(resource, "notes", "abstract")
	bioghist = get_note_contents(resource, "notes", "bioghist")

	ead_id = get_single_value(resource, "ead_id")
	ead_location = get_single_value(resource, "ead_location")
	finding_aid_author = get_single_value(resource, "finding_aid_author")
	finding_aid_date  = get_single_value(resource, "finding_aid_date")
	finding_aid_description_rules  = get_single_value(resource, "finding_aid_description_rules")
	finding_aid_filing_title = get_single_value(resource, "finding_aid_filing_title")
	finding_aid_language = get_single_value(resource, "finding_aid_language")
	finding_aid_title = get_single_value(resource, "finding_aid_title")

	required_values = title, publish, resource_id, level, extent, language
	required_notes = abstract, bioghist, scope, access
	required_ead = ead_id, ead_location, finding_aid_title, finding_aid_author, finding_aid_date, finding_aid_description_rules, finding_aid_filing_title, finding_aid_language

	for item in required_values:
		if item != "false": 
			row.append(item)
		else:
			row.append("false")	

	if repository:
		response = requests.get(repositoryBaseURL, headers=headers).json()
		row.append(response["name"])
	else:
		row.append("false")		

	# need at least one creation date
	if 'creation' in date_labels:
		row.append(date_labels)
	else:
		row.append("false")


	# need at least one creator
	if "creator" in agent:
		creator_list = []
		for item in resource["linked_agents"]:
			response = requests.get(resourceURL + item["ref"], headers=headers).json()
			for item in response["names"]:
				creator_list.append(item["sort_name"])
		row.append(", ".join(creator_list).encode('utf-8'))
	else:
		row.append("false")

	# add archives west browsing terms if exist (need at least one)
	# for ref in subjects:
	# 	print resourceURL+ref
	# 	#print requests.get(resourceURL + ref, headers=headers).json()
	source_list = [requests.get('http://localhost:8089' + ref).json()['source'] for ref in subjects]
	if 'Archives West Browsing Terms' in source_list:
		sub_list = []
		for ref in subjects:
			subject = requests.get(resourceURL + ref, headers=headers).json()
			if subject['source'] == 'Archives West Browsing Terms':
				sub_list.append(subject['title'])
		row.append(", ".join(sub_list).encode('utf-8'))
	else:
		row.append("false")
	
	# add notes if exist						
	for item in required_notes:
		if item:
			row.append(item)
		else:
			row.append("false")

	for item in required_ead:
		if item != "false": 
			row.append(item)
		else:
			row.append("false")	
	
	print "Writing resource ", resource_id,"..."	

def main():
	#User input to refine functionality of script 
	print ""
	print "Welcome to DACSspace!\n"
	print "I'll ask you a series of questions to refine how the script works.\n"
	print "If you want to use the default value for a question press the ENTER key.\n"
	unpublished_response = raw_input("Do you want DACSspace to include unpublished resources? y/n (default is n): ")
	uniqueid_response = raw_input("Do you want to further limit the script by a specific resource id? If so, enter a string that must be present in the resource id (enter to skip): ")
	
	#Getting list of resources
	resourceIds = requests.get(repositoryBaseURL + "/resources?all_ids=true", headers=headers)
	
	#Creating csv
	writer = csv.writer(open(spreadsheet, "wb"))
	column_headings = ["title", "publish", "resource", "level", "extent", "date", "language", "repository", "creation_date", "creator", "aw_subjects", "abstract", "bioghist", "scope", "restrictions", 'ead_id', 'ead_location', 'finding_aid_title', 'finding_aid_author', 'finding_aid_date', 'finding_aid_description_rules', 'finding_aid_filing_title', 'finding_aid_language']
	writer.writerow(column_headings)

	#Checking ALL resources
	if unpublished_response == ("y"):
		if uniqueid_response:
			print "Evaluating all resources containing", uniqueid_response,"in their resource ID"
			for resourceId in resourceIds.json():
				resource = (requests.get(repositoryBaseURL + "/resources/" + str(resourceId), headers=headers)).json()	
				if uniqueid_response in resource["id_0"]:
					makeRow(resource)
					writer.writerow(row)
				else:
					pass
		else:
			print "Evaluating all resources"
			for resourceId in resourceIds.json():
				resource = (requests.get(repositoryBaseURL + "/resources/" + str(resourceId), headers=headers)).json()	
				makeRow(resource)
				writer.writerow(row)
				
	#Checking ONLY published resources
	elif not unpublished_response or unpublished_response == ("n"):
		if uniqueid_response:
			print "Evaluating only published resources containing", uniqueid_response,"in their resource ID"
			for resourceId in resourceIds.json():
				resource = (requests.get(repositoryBaseURL + "/resources/" + str(resourceId), headers=headers)).json()	
				if resource["publish"] and uniqueid_response in resource["id_0"]:
					makeRow(resource)
					writer.writerow(row)
				else:
					pass
		else:
			print "Evaluating published resources"
			for resourceId in resourceIds.json():
				resource = (requests.get(repositoryBaseURL + "/resources/" + str(resourceId), headers=headers)).json()	
				if resource["publish"]:
					makeRow(resource)
					writer.writerow(row)
				else:
					pass
	else:
		print "Invalid response, please try again"

main()
