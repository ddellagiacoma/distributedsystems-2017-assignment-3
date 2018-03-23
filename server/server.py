# coding=utf-8
#------------------------------------------------------------------------------------------------------
# TDA596 Labs - Server Skeleton
# server/server.py
# Input: Node_ID total_number_of_ID
# Student Group: 37
# Student name: Daniele Dellagiacoma
#------------------------------------------------------------------------------------------------------
# Import various libraries
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler # Socket specifically designed to handle HTTP requests
import sys # Retrieve arguments
from urlparse import parse_qs # Parse POST data
from httplib import HTTPConnection # Create a HTTP connection, as a client (for POST requests to the other vessels)
from urllib import urlencode # Encode POST content into the HTTP header
from codecs import open # Open a file
from threading import  Thread # Thread Management
import time # Various time-related functions
import operator # Functions corresponding to the intrinsic operators of Python
#------------------------------------------------------------------------------------------------------

# Global variables for HTML templates
board_frontpage_footer_template = ""
board_frontpage_header_template = ""
boardcontents_template = ""
entry_template = ""

#------------------------------------------------------------------------------------------------------
# Static variables definitions
PORT_NUMBER = 80
STUDENT_NAME = "Daniele Dellagiacoma"
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
class BlackboardServer(HTTPServer):
#------------------------------------------------------------------------------------------------------
	def __init__(self, server_address, handler, node_id, vessel_list):
		# Call the super init
		HTTPServer.__init__(self, server_address, handler)
		# Create the dictionary of values
		self.store = {}
		# Keep a variable of the next id to insert
		self.current_key = -1
		# Our own ID (IP is 10.1.0.ID)
		self.vessel_id = vessel_id
		# The list of other vessels
		self.vessels = vessel_list
		# Logical clock of the server
		self.clock = 0
		# Pending requests queue
		self.queue = []
		# Keep tack of the first and last time the server received a POST request
		self.request_time = {'first':True, 'first_request':0, 'last_request':0}
#------------------------------------------------------------------------------------------------------
	# Add a value received to the store
	def add_value_to_store(self, value, id):
		# Add the value to the store
		self.store[id] = value
#------------------------------------------------------------------------------------------------------
	# Modify a value received in the store
	def modify_value_in_store(self, key, value):
		# Modify a value in the store if it exists
		if key in self.store:
			self.store[key] = value
			return True
		else:
			return False
#------------------------------------------------------------------------------------------------------
	# Delete a value received from the store
	def delete_value_in_store(self, key):
		# Delete a value in the store if it exists
		if key in self.store:
			del self.store[key]
			return True
		else:
			return False
#------------------------------------------------------------------------------------------------------
	# Contact a specific vessel with a set of variables to transmit to it
	def contact_vessel(self, vessel_ip, path, entry, delete, clock):
		# The Boolean variable that will be returned
		success = False
		# The variables must be encoded in the URL format, through urllib.urlencode
		post_content = urlencode({'entry': entry, 'delete': delete, 'clock': clock, 'id': self.vessel_id})
		# The HTTP header must contain the type of data transmitted, here URL encoded
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		# Try to catch errors when contacting the vessel
		try:
			# Contact vessel:PORT_NUMBER since they all use the same port
			# Set a timeout to 30 seconds, after which the connection fails if nothing happened
			connection = HTTPConnection("%s:%d" % (vessel_ip, PORT_NUMBER), timeout = 30)
			# Only use POST to send data (PUT and DELETE not supported)
			action_type = "POST"
			# Send the HTTP request
			connection.request(action_type, path, post_content, headers)
			# Retrieve the response
			response = connection.getresponse()
			# Check the status, the body should be empty
			status = response.status
			# If it receive a HTTP 200 - OK
			if status == 200:
				success = True
		# Catch every possible exceptions
		except Exception as e:
			print("Error while contacting %s" % vessel_ip)
			# Print the error given by Python
			print(e)

		# Return whether it succeeded or not
		return success
#------------------------------------------------------------------------------------------------------
	# Send a received value to all the other vessels of the system
	def propagate_value_to_vessels(self, path, entry, delete, clock):
		# Increment clock value
		self.clock = self.clock + 1
		# Iterate through the vessel list
		for vessel in self.vessels:
			# Should not send it to our own IP, or it would create an infinite loop of updates
			if vessel != ("10.1.0.%s" % self.vessel_id):
				# Try again until the request succeed
				while (True):
					if self.contact_vessel(vessel, path, entry, delete, clock):
						break
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# This class implements the logic when a server receives a GET or POST request
# It can access to the server data through self.server.*
# i.e. the store is accessible through self.server.store
# Attributes of the server are SHARED accross all request hqndling/ threads!
class BlackboardRequestHandler(BaseHTTPRequestHandler):
#------------------------------------------------------------------------------------------------------
	# Fill the HTTP headers
	def set_HTTP_headers(self, status_code = 200):
		# Set the response status code (200 if OK, something else otherwise)
		self.send_response(status_code)
		# Set the content type to HTML
		self.send_header("Content-type", "text/html")
		# Close headers
		self.end_headers()
#------------------------------------------------------------------------------------------------------
	# POST request must be parsed through urlparse.parse_QS, since the content is URL encoded
	def parse_POST_request(self):
		post_data = ""
		# Parse the response, the length of the content is needed
		length = int(self.headers['Content-Length'])
		# Parse the content using parse_qs
		post_data = parse_qs(self.rfile.read(length), keep_blank_values = 1)
		# Return the data
		return post_data
#------------------------------------------------------------------------------------------------------	
#------------------------------------------------------------------------------------------------------
# Request handling - GET
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a GET request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_GET(self):
		print("Receiving a GET on path %s" % self.path)
		#print("Server clock %s" % self.server.clock)
		#print(self.server.queue)
		print("First request received (s): %s" % self.server.request_time['first_request'])
		print("Last request received (s): %s" % self.server.request_time['last_request'])


		# Check which path was requested and call the right logic based on it
		# At this time, the GET request can only be "/" or "/board"
		if self.path == "/" or self.path == "/board":
			self.do_GET_Index()
		else:
			# In any other case 
			self.wfile.write("The requested URL does not exist on the server")
#------------------------------------------------------------------------------------------------------
# GET logic - specific path: "/" or "/board"
#------------------------------------------------------------------------------------------------------
	def do_GET_Index(self):

		try:
			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)
			# Call the method that handle the pending requests of the server
			self.handle_pending_requests()

			# Go over the entries already stored in the server to produce the boardcontents part
			# The stored entries are sorted by key to show data in the same order to all the servers 
			allEntries_template = ""
			for key in sorted(self.server.store):
				allEntries_template = allEntries_template + entry_template % ("board/" + key, key, self.server.store[key])

			# Construct the full page by combining all the parts
			html_reponse = board_frontpage_header_template + boardcontents_template % ("10.1.0." + str(self.server.vessel_id) + ":" + str(PORT_NUMBER), allEntries_template) + board_frontpage_footer_template % STUDENT_NAME

			# Write the HTML file on the browser
			self.wfile.write(html_reponse)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print(e)
			# Write the error given by Python on the browser
			self.wfile.write("The following problem has been encountered: " + str(e) + "\n. Please try to refresh the page. \n")
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)
#------------------------------------------------------------------------------------------------------
	# This function is called to check if there are requests that have not been satisfied yet
	# E.g. An hosts receives an update to delete/modify a message from the blackboard, but that message has not even arrived yet on that host
	def handle_pending_requests(self):
		
		# Sort the queue to satisfy the requests in the same order in which they have been submitted
		self.server.queue.sort(key = operator.itemgetter(0))
		# Varible used to keep track of the requests that have not been satisfied yet
		remaining = []
		
		# Go over all the pending requests in the queue
		for entry in self.server.queue:
			if entry[3] == "0":
				# Call the method to modify a value received in the server store
				if not (self.server.modify_value_in_store(entry[1], entry[2])):
					# Keep the request in the queue if it is not satisfied yet
					remaining.append(entry)
			elif entry[3] == "1":
				# Call the method to delete the value with the corresponding id from the server store 
				if not (self.server.delete_value_in_store(entry[1])):
					# Keep the request in the queue if it is not satisfied yet
					remaining.append(entry)

		# Keep only the requests that have not been satisfied
		self.server.queue = remaining
#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
# Request handling - POST
#------------------------------------------------------------------------------------------------------
	# This function contains the logic executed when this server receives a POST request
	# This function is called AUTOMATICALLY upon reception and is executed as a thread!
	def do_POST(self):
		print("Receiving a POST on %s" % self.path)
		# Variable used to measure the time that the server takes to reach consistency
		if (self.server.request_time['first']):
			self.server.request_time['first'] = False
			self.server.request_time['first_request'] = time.time()
		else:
			self.server.request_time['last_request'] = time.time()

		try:
			# Variable used to check if the message needs to be propagated to the other servers
			retransmit = False
			# Call the method to parse the data received from the POST request
			# Save the data in a dictionary, e.g. {'entry':['new Value'], 'delete':['0'], 'clock:['3'], 'id':['1']}
			parameters = self.parse_POST_request()

			# Check which path was requested and call the right logic based on it
			path_segments = (self.path).split("/")
			if len(path_segments) > 1:
				# The POST requests with path "/board..." and "/propagate..." work at the same way (i.e. add, modify or delete a value in the server store)
				# The difference is that a POST request with path "/board..." will be retransmitted to the other servers
				# whereas a POST request with path "/propagate..." won't be retransmitted to avoid infinite loops
				if path_segments[1] == "board":
					# Increment clock value
					self.server.clock = self.server.clock + 1
					# Call the method to add, modify or delete a value in the server store
					self.do_POST_Parameters(parameters, path_segments, str(self.server.clock) + "." + str(self.server.vessel_id))
					retransmit = True
				elif path_segments[1] == "propagate":
					# Adjust clock value and increment it
					self.server.clock = max(self.server.clock, int(parameters['clock'][0])) + 1
					# Call the method to add, modify or delete a value in the server store
					self.do_POST_Parameters(parameters, path_segments, parameters['clock'][0] + "." + parameters['id'][0])

			# Set the response status code to 200 (OK)
			self.set_HTTP_headers(200)

		# Catch every possible exception
		except Exception as e:
			# Print error given by Python on the server console
			print(e)
			# Set retransimit to False avoiding the further propagation of other errors
			retransmit = False
			# Set the response status code to 400 (Bad Request)
			self.set_HTTP_headers(400)

		# If True the message needs to be propagate to the other servers
		if retransmit:
			# do_POST send the message only when the function finishes
			# Create threads to do some heavy computation
			# Check if it is a add request or a modify/delete request
			if 'delete' in parameters:
				thread = Thread(target=self.server.propagate_value_to_vessels, args=(self.path.replace("board","propagate"), parameters['entry'][0], parameters['delete'][0], self.server.clock))
			else:
				# If delete is not present in parameters (i.e. when a new value is inserted)
				# delete is passed as None and it will not be used
				thread = Thread(target=self.server.propagate_value_to_vessels, args=(self.path.replace("board","propagate"), parameters['entry'][0], None, self.server.clock))
			# Kill the process if we kill the server
			thread.daemon = True
			# Start the thread
			thread.start()
#------------------------------------------------------------------------------------------------------
# POST Logic - specific path: "/board..." or "/propagate..."
#------------------------------------------------------------------------------------------------------
	def do_POST_Parameters(self, parameters, path_segments, id):
		# Call the function to adjust entry ID
		id = self.adjust_id(id)

		# If the path is exactly "/board" or "/propagate"
		if len(path_segments) == 2:
			# Call the method to add the value received in the server store
			self.server.add_value_to_store(parameters['entry'][0], id)
		# If the path is "/board/*" or "/propagate/*" where * is the id of the entry
		elif len(path_segments) == 3:
			if (parameters['delete'][0]) == "0":
				# Call the method to modify a value received in the server store
				if not (self.server.modify_value_in_store(path_segments[2], parameters['entry'][0])):
					# Append request to the queue if the value is not present in the store yet
					self.server.queue.append(tuple([id, path_segments[2], parameters['entry'][0], parameters['delete'][0]]))
			elif parameters['delete'][0] == "1":
				# Call the method to delete the value with the corresponding id from the server store 
				if not (self.server.delete_value_in_store(path_segments[2])):
					# Append request to the queue if the value is not present in the store yet
					self.server.queue.append(tuple([id, path_segments[2], parameters['entry'][0], parameters['delete'][0]]))
#------------------------------------------------------------------------------------------------------
	# This function is used to be sure that all IDs will have the same leghth
	# in this way they can be easily sorted in the subsequent stages (if more 0s or a different method to create the IDs are needed, it is necessary to change only this function)
	def adjust_id(self, id):
		# E.g. 1.4 -> 001.4
		if (len(id)) == 3:
			id = "00" + id
		# E.g. 12.3 -> 012.3
		elif (len(id)) == 4:
			id = "0" + id
		return id
#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------
# Execute the code
if __name__ == '__main__':

	try:
		# Open all the HTML files
		file_header = open("server/board_frontpage_header_template.html", 'rU')
		file_boardcontents = open("server/boardcontents_template.html", 'rU')
		file_entry = open("server/entry_template.html", 'rU')
		file_footer = open("server/board_frontpage_footer_template.html", 'rU')
		
		# Read the templates from the corresponding HTML files
		board_frontpage_header_template = file_header.read()
		boardcontents_template = file_boardcontents.read()
		entry_template = file_entry.read()
		board_frontpage_footer_template = file_footer.read()

		# Close all the HTML template files
		file_header.close()
		file_boardcontents.close()
		file_entry.close()
		file_footer.close()

	except Exception as e:
		print("Problem with the HTML template files: %s" % e)

	vessel_list = []
	vessel_id = 0

	# Checking the arguments
	if len(sys.argv) != 3: # 2 args, the script and the vessel name
		print("Arguments: vessel_ID number_of_vessels")
	else:
		# We need to know the vessel IP
		vessel_id = int(sys.argv[1])
		# Write the other vessels IP, based on the knowledge of their number
		for i in range(1, int(sys.argv[2]) + 1):
			# Add server itself, test in the propagation
			vessel_list.append("10.1.0.%d" % i)

	# Create server
	server = BlackboardServer(('', PORT_NUMBER), BlackboardRequestHandler, vessel_id, vessel_list)
	print("Starting the server on port %d" % PORT_NUMBER)

	# Run server
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()
		print("Stopping Server")
#------------------------------------------------------------------------------------------------------
