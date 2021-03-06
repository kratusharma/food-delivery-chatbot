
from tkinter import *
from tkinter import scrolledtext


import nltk
from nltk.stem.lancaster import LancasterStemmer

import numpy
import tflearn
import tensorflow
import random
import json
import pickle


stemmer = LancasterStemmer()

with open("intents.json") as file:
	data = json.load(file)

try:
	with open("data.pickle","rb") as f:
		words,labels,training,output = pickle.load(f)
except:
	words = []
	labels = []
	docs_x = []
	docs_y = []

	for intent in data["intents"]:
		for pattern in intent["patterns"]:
			wrds = nltk.word_tokenize(pattern)
			words.extend(wrds)
			docs_x.append(wrds)
			docs_y.append(intent["tag"])

		if intent["tag"] not in labels:
			labels.append(intent["tag"])

	words = [stemmer.stem(w.lower()) for w in words if w!="?"]
	words = sorted(list(set(words)))

	labels = sorted(labels)

	# 	## boolean representation of the document
	training = []
	output = []

	out_empty = [0 for _ in range(len(labels))]

	for x,doc in enumerate(docs_x):
		boolean = []
		wrds = [stemmer.stem(w.lower()) for w in doc]

		for w in words:
			if w in wrds:
				boolean.append(1)
			else:
				boolean.append(0)

		output_row = out_empty[:]
		output_row[labels.index(docs_y[x])] = 1

		training.append(boolean)
		output.append(output_row)


	training = numpy.array(training)
	output = numpy.array(output)

	with open("data.pickle","wb") as f:
		pickle.dump((words,labels,training,output),f)


tensorflow.reset_default_graph()


net = tflearn.input_data(shape=[None,len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]),activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
	model.load("model.tflearn")
except:
	model.fit(training, output, n_epoch=2000, batch_size=8, show_metric=True)
	model.save("model.tflearn")


def bag_of_words(s, words):
	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i,w in enumerate(words):
			if w==se:
				bag[i] = 1
	
	return numpy.array(bag)


def chat(inp):
	# print("\nStart talking with the bot (quit to stop)!\n\n")
	# while True:
		# inp = input("You: ")
	if inp.lower() == "quit":
		# break
		return ""


	results = model.predict([bag_of_words(inp, words)])[0]
	##results gives probablity

	results_index = numpy.argmax(results)

	tag = labels[results_index]

	if results[results_index] > 0.5:
		for tg in data["intents"]:
			if tg['tag'] == tag:
				responses = tg['responses']

		response_system = random.choice(responses)
	else:
		response_system = "I didn't get that, Try again !"
	# print(response_system)

	return response_system



# chat()

##########



root = Tk()
root.title('FoodieChat')
root_width = 500
root_height = 750
root.maxsize(root_width,root_height)   #(width,height)
root.config(bg='#002699')


def getReply():
    query = text_area.get("1.0", END)
    text_area.delete('1.0', END)

    query = '[YOU] :: ' + query
    response = '[BOT] :: '

    response += chat(query)

    messages.config(state=NORMAL)
    messages.insert(END,query)
    messages.insert(END,response+'\n')
    messages.config(state=DISABLED)


#----User Interface Section---------------------------------------------------------------------------------------------
headerFrame = Frame(root,height = 50,width = 500,bg = 'black')
headerFrame.grid(row = 0,column = 0,padx = 5,pady = 5)

outputCanvas = Canvas(root,height = 550,width = 500,bg = '#99ffff')
outputCanvas.grid(row = 1,column = 0,padx = 10,pady = 10)

footerFrame = Frame(root,height = 50,width = 500,bg = 'black')
footerFrame.grid(row = 2,column = 0,padx = 10,pady = 10)

# #--input frame-------------------------------------------------------
head = Label(headerFrame,text = 'FoodieChat',fg = 'black',bg = '#ffff00',height = 1,width = 15,font = ('Comic Sans MS',14))
head.grid(row = 0,column = 0,padx = 5,pady = 5)


messages = scrolledtext.ScrolledText(outputCanvas,width = 33,height = 22,font = ("Comic Sans MS",14),bg='#ccffff')
messages.grid(row = 0 , column = 0, padx = 5, pady = 5)
messages.config(state=DISABLED)


text_area = scrolledtext.ScrolledText(footerFrame,width = 25,height = 1,font = ("Comic Sans MS",14))
text_area.grid(row = 0 , column = 1, padx = 5, pady = 5)

send = Button(footerFrame,text = 'SEND',fg = 'white',bg = 'green',height = 1,width = 10,font = ('Comic Sans MS',14),command = getReply)
send.grid(row = 0,column = 2,padx = 5,pady = 5)


root.mainloop()
