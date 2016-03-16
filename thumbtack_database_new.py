#Nirav Chitkara, 2/19/2016
#Thunmbtack Simple Database Challenge

import sys


class DataBase(object):

	#helper functions
	def __init__(self, node = None):
		#initializer that takes one parameter that defaults to None unless specified

		#current node's data store
		self.data_store = {}
		#current node's value count store
		self.value_count = {}
		#current node's previous node
		self.previous_node = node

	def get_data_store(self):
		#getter function that returns the current node's data store
		return self.data_store

	def get_value_count(self):
		#getter function that returns the current node's value count store
		return self.value_count

	def get_previous_node(self):
		#getter function that returns the current node's previous node
		return self.previous_node

	def get_value(self, key):
		#return the value for the key if it exists
		
		#check to see if the key is in the current node's data
		if key in self.data_store:
			if self.data_store[key] != None:
				return self.data_store[key]
			else: 
				return None

		#if key not in current' nodes data, return the value for the key from the previous node's data or None
		if self.previous_node != None:
			return self.previous_node.get_value(key)
		else:
			return None

	def get_count(self, value):
		#return the count for the value passed if it exists

		#check to see if the value is in the current node's value data store 
		#if it is and isn't None return it otherwise return 0
		if value in self.value_count:
			if self.value_count[value] != None:
				return self.value_count[value]
			else:
				return 0
		#if value not in current node's value count, then check the previous node if one exists
		#if the value is not None then return it otherwise return 0
		if self.previous_node != None:
			if self.previous_node.get_value_count()[value] != None:
				return self.previous_node.get_value_count()[value]
			else:
				return 0

	def decrement_count(self, value):
		#decrement the count of the given value

		#if the value is equal to None then don't do anything
		if value == None:
			return
		#if the value count is greater than 0 then subtract 1 from it 
		if self.value_count[value] > 0:
			self.value_count[value] -= 1

	def increment_count(self, value):
		#increment the count of the given value

		#if the value doesn't exist in the value count store then set it to 1 otherwise increase it by 1
		if value not in self.value_count:
			self.value_count[value] = 1
		else:
			self.value_count[value] += 1

	def merge(self):
		#merge the values in the current node's data store with the previous node's store
		#also merge the current node's value count store with the previous node's store

		for key in self.data_store:
			self.previous_node.get_data_store()[key] = self.data_store[key]
		for value in self.value_count:
			self.previous_node.get_value_count()[value] = self.value_count[value]

	#command functions

	def SET(self, key, value):
		#set the value to the key in the current node's data store if the value doesn't exist

		#first if we're in a transaction block and the key doesn't exist in the current block's data
		#check to make sure the key in the previous node's data doesn't already have the value
		#if so, do nothing
		if self.previous_node != None:
			if key not in self.data_store and value == self.previous_node.get_value(key):
				return

		#check if the key is not in the data store, and store it with the value if not
		#increment the value count for that value
		if key not in self.data_store:
			self.data_store[key] = value
			self.increment_count(value)

		#if the key has a value already and its not equal to the new value passed in then change the values
		#decrement the count of the old value and increment the count of the new value
		elif value != self.data_store[key]:
			old = self.data_store[key]
			self.data_store[key] = value
			self.increment_count(value)
			self.decrement_count(old)

		else: return

	def GET(self, key):
		#get the value from the data store if it exists
		return self.get_value(key)

	def UNSET(self, key):
		#remove the key from the data store (set to None) and decrement the value count

		#check if the previous node value exists for the current node
		#if so, retrieve the value from it's data store for the given key and the value count for that value
		#store copy in the current node's respective data store and value count
		if self.previous_node != None:
			value = self.previous_node.get_value(key)
			self.data_store[key] = value
			self.value_count[value] = self.previous_node.get_count(value)
		
		#if the key is in the current node's data store, retrieve the value
		#if the value is not None then decrement it's count and consequently set the key to None (instead of outright deleting)
		if key in self.data_store:
			cval = self.data_store[key]
			if cval != None:
				self.decrement_count(cval)
				self.data_store[key] = None
		#if the key doesn't exist at all, do nothing
		else:
			return

	def NUMEQUALTO(self, value):
		#return the value count for the specified value
		return self.get_count(value)


def main():

	#create a new db object
	db = DataBase(None)
	#set this to the current variable
	current = db

	#try to get input from the user unless there's a KeyboardInterrupt Error
 	while 1:
 		try:
 			message = raw_input().split()
 		except (KeyboardInterrupt):
 			break
 		else:
	 		command = message[0].upper()
			arguments = message[1:]

			#check to see if the message list is longer than 3 arguments
	 		if len(message) > 3:
	 			print("Too many arguments")
	 		#if the command is EXIT then quit the program
	 		elif command == 'END':
	 			sys.exit()

	 		#rest of the commands

	 		#set
			elif command == 'SET' and len(arguments) == 2:
				current.SET(arguments[0], arguments[1])

			#get - print either a value or if the value is None print NULL
			elif command == 'GET' and len(arguments) == 1:
				if current.GET(arguments[0]) == None:
					print("NULL")
				else:
					print current.GET(arguments[0])

			#unset
			elif command == 'UNSET' and len(arguments) == 1:
				current.UNSET(arguments[0])

			#numequalto
			elif command == 'NUMEQUALTO' and len(arguments) == 1:
				print current.NUMEQUALTO(arguments[0])

			#begin
			elif command == 'BEGIN' and len(arguments) == 0:
				#create a new db node that takes the current node to be set as it's previous node attribute
				#set current to now be this new node
				new = DataBase(current)
				current = new

			#rollback
			elif command == 'ROLLBACK' and len(arguments) == 0:
				#get the previous node from the current node if it exists
				if current.get_previous_node() != None:
					#set the previous node to a storeable variable
					old = current.get_previous_node()
					#delet the current node and set current to now be the previous node
					del current
					current = old
				#if there isn't a begin block
				else:
					print("No Transaction")

			#commit
			elif command == 'COMMIT' and len(arguments) == 0:
				#check if there is first a previous node for the current node
				if current.get_previous_node() != None:
					#loop that will go through each current node and retrieve its previous node
					#the current node will be deleted and the previous node will be the new current
					#the current node's data store and value count are merged with the previous node's
					#this is done till we reach the root node where there isn't a previous node
					while current.get_previous_node() != None:
						current.merge()
						old = current
						current = current.get_previous_node()
						del old
					continue
				#if there isn't a begin block
				else:
					print("No Transaction")

			else:
				print("Invalid command")



main()


		
		
