#!/usr/bin/env python
# coding: utf-8

# 
# # Importing Required Libraries

# In[3]:


import speech_recognition as sr # for online speech recognition

# for recording audio and saving
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv

# for data pre-processing
import re
import spacy
import pandas as pd
nlp = spacy.load("en_core_web_md")

import random as rd

# for 3d scene genration
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import time


import warnings
warnings.filterwarnings('ignore')


# # Importing Required Files

# In[4]:


entities = open("noun.text", 'r').read().splitlines()
pos = open("pos.txt", 'r').read().splitlines()
comman_words = pd.read_csv('Comman-Words.csv')
chars_dict = pd.read_csv('Char-dict.csv')
replace  = open('replace.txt', 'r').read().splitlines()
meta_data = pd.read_csv('meta_data.csv') # data about the 3d models

loadPrcFileData("", "load-file-type p3assimp") # for panda3d


# # Speech to Urdu Script

# In[ ]:


def recordAudio():
    # Sampling frequency
    freq = 48000

    # Recording duration
    duration = 7

    # Start recorder with the given values 
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), 
                       samplerate=freq, channels=2)

    # Record audio for the given number of seconds
    sd.wait()

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("recording0.wav", freq, recording)

    # Convert the NumPy array to audio file
    wv.write("recording1.wav", recording, freq, sampwidth=2)


# In[ ]:


def Audio2Text():
    print("You have 7 sec to speak, start with \"Hey Google\"")
    recordAudio()
    
    recognizer = sr.Recognizer()

    audio = sr.AudioFile("recording1.wav")
    with audio as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)


    # GOOGLE speech to urdu conversion
    try:
        data = recognizer.recognize_google(audio, language='ur-PK')
        return data
    except:
        print('Voice not Recognized')
        exit(0)

text = Audio2Text()


# # Transliteration: Urdu To Roman

# In[5]:


def convert_to_roman(word):
    '''
        1. Got a word, break into characters
        2. Iterate over characters and map if it is valid character else append as it is
        3. Return a word by joining all mapped characters
    '''
    
    chars = re.findall(r'[\u0600-\u06ff]',word)
    roman_chars = []
    
    for char in chars:
        ch = (chars_dict.loc[chars_dict['Urdu'] == char].values)
        try:
            roman_chars.append(ch[0][1])
        except:
            roman_chars.append(char)
            
    return ''.join(roman_chars)


def urdu2roman(sentence):
    '''
        1. Got a sentence, break it into words
        2. Iterate over words, try to map word using comman word, else map by character if word is urdu,
           finally append as it is
        3. Return a sentence by joining all mapped words
    '''
    
    
    new_roman = []
    urdu_words = sentence.split(' ')
    
    for urdu_word in urdu_words:
        flag=True #flag indicated that word conversion is remaining
        roman_word = (comman_words.loc[comman_words['Urdu'] == urdu_word].values)
        if len(roman_word)>0:
            new_roman.append(roman_word[0][0])
            flag=False
        
        if flag:
            roman_word = convert_to_roman(urdu_word)
            if roman_word!='':
                new_roman.append(roman_word)
                flag=False
        
        if flag:
            new_roman.append(urdu_word)
    
    return ' '.join(new_roman)

sentence = urdu2roman(text)


# # Preprocessing

# ### Converting to Lower Case

# In[6]:


sentence = sentence.lower()


# ### Replacing Similar Words with one word

# In[7]:


def replaceWords(sentence):
    global replace
    
    new_sentence = []
    words = sentence.split(' ')
    
    it = 0
    while it < len(words):
        word = words[it]
        appendFlag = True
    
        if word=='main' and words[it+1]=='is':
            new_sentence.append('maiz')
            it += 2
            word = words[it]
        
        for replaceW in replace:
            correctWord, wrongWords = replaceW.split(':')
            for wrongW in wrongWords.split(','):
                if word==wrongW:
                    new_sentence.append(correctWord)
                    appendFlag = False
                    break
            if not appendFlag:
                break
                
        if appendFlag:
            new_sentence.append(word)
        it+=1
        
    return " ".join(new_sentence)
        
    
    
sentence = replaceWords(sentence)


# ### Replacing Pronouns

# In[8]:


def replacePronouns(sentence):
    pronouns = ['uska', 'uski', 'uske', 'iske']
    words = sentence.split(' ')
    
    noun = ""
    for i in range(len(words)):
        if words[i] in entities:
            noun = words[i]
        elif words[i] in pronouns:
            words[i] = noun
    
    return " ".join(words)


# ### Spliting Multiple Sentences

# In[9]:


def splitSentence(data):
    sentences = []
    sentence = []
    words = data.split(" ")
    
    for i in range(len(words)):
        sentence.append(words[i])
        if words[i] == "hai" and (i==len(words)-1 or words[i+1]=="aur"):
            sentences.append(" ".join(sentence))
            sentence.clear()
    
    if len(sentence)!=0:
        sentences.append(" ".join(sentence))

    
    return sentences


# ### Get Entities with Relation

# In[10]:


def getEntitiesRelation(sentence):
    objects = []
    positions = []
    
    for word in sentence.split(' '):
        if word in entities:
            objects.append(word)
        if word in pos:
            positions.append(word)
            
    return objects, positions


# ### Rephrasing

# In[11]:


def flipSentence(sentence):
    sentences = sentence.split(' hai ')
    if len(sentences)==1:
        return sentence
    else:
        return sentences[1]+" "+sentences[0]


# # Making Graph from Sentence

# In[12]:


def makeGraph(data):
    graph = dict()
    data = replacePronouns(data)
    sentences = splitSentence(data)
    
#     print(sentences)
    for sentence in sentences:
        if sentence.split(' ')[-1] != 'hai':
            sentence = flipSentence(sentence)
        print(sentence)
        objects, positions = getEntitiesRelation(sentence)
        node1 = node2 = None
        
        
        for j in range(len(positions)):
            position = positions[j]
            if position == "darmian":
                node1 = objects.pop(0)+" "+objects.pop(0)
            elif position != "darmian" and node2==None:
                node1 = objects.pop(0)
            node2 = objects.pop(0)
            
            if j == len(positions)-1:
                for obj in objects:
                    if node1 == node2:
                        node2 =  obj
                    else:
                        node2 += " "+obj
            
            if node1 not in graph.keys():
                graph[node1] = [(node2, position)]
            else:
                graph[node1].append((node2, position))
            node1 = node2
                
    return graph


# In[ ]:





# # Get 3d Models' relative Positions from Graph

# In[14]:


def setPositions(_3dMaps, parent, Node, pos):
    global meta_data
    
    node = Node.split(' ')[0]


    if pos=="darmian":
        P = _3dMaps[-2]
        parent_data = (meta_data[meta_data['Model']==P[0]].values)[0]
        child_data = (meta_data[meta_data['Model']==node].values)[0]
        new_value = (node, child_data[1], (P[2][0] + parent_data[2] + child_data[2] + 0.1 , P[2][1], P[2][2]))
        _3dMaps.append(new_value)



    if pos == 'sath':
        pos = rd.sample(['aage', 'peeche'])
    
    
    P = None
    for C in _3dMaps:
        if C[0] == parent:
            P = C
            break
    parent_data = (meta_data[meta_data['Model']==parent].values)[0]
    child_data = (meta_data[meta_data['Model']==node].values)[0]

    if pos == 'dai':
        new_value = (node, child_data[1], (P[2][0] + parent_data[2] + child_data[2] + 0.1 , P[2][1], P[2][2]))
    elif pos == 'bai':
        new_value = (node, child_data[1], (P[2][0] - parent_data[2] - child_data[2] - 0.1 , P[2][1], P[2][2]))
    elif pos == 'aage':
        new_value = (node, child_data[1], (P[2][0] , P[2][1], P[2][2] + parent_data[4] + child_data[4]+0.1))
    elif pos == 'peeche':
        new_value = (node, child_data[1], (P[2][0] , P[2][1], P[2][2] - parent_data[4] - child_data[4] - 0.1))
    elif pos == 'ooper':
        new_value = (node, child_data[1], (P[2][0] , P[2][1]+parent_data[3]+child_data[3], P[2][2]))
    elif pos == 'neeche':
        new_value = (node, child_data[1], (P[2][0] , P[2][1]-child_data[3], P[2][2]))
    elif pos=='mein':
        new_value = (node, child_data[1], (P[2][0] , P[2][1]+0.02, P[2][2]))
    _3dMaps.append(new_value)

    print(_3dMaps)
    if len(Node.split(' ')) > 1:
        setPositions(_3dMaps, Node.split(' ')[0], Node.split(' ')[1:], pos)
    
        
    

def DFS(graph, node, visited, _3dMaps, parent=None, pos=None):
    visited.add(node)
    if pos == None and parent==None:
        global data
        if len(node.split(' '))==0:
            data = meta_data[meta_data['Model']==node].values[0]
            _3dMaps.append((node, data[1], (0, 0, 0)))
        else:
            i = 0
            for N in node.split(' '):
                data = meta_data[meta_data['Model']==N].values[0]
                if i==0:
                    _3dMaps.append((N, data[1], (0, 0, 0)))
                else:
                    _3dMaps.append((N, data[1], (4, 0, 0)))
                i+=1

    else:
        setPositions(_3dMaps, parent, node, pos)
    
    try:
        for n, p in graph[node]:
            if n not in visited:
                DFS(graph, n, visited, _3dMaps, node, p)
    except:
        pass

def mapping(graph):
    visited = set()
    start = list(graph.keys())[0]
    _3dMaps = []
    
    DFS(graph, start, visited, _3dMaps)
    
    return _3dMaps


# In[16]:


graph = makeGraph(sentence)
maps = mapping(graph)


# # 3D Scene Genration(works better in PY file)

# In[17]:


class MyApp(ShowBase):


    def __init__(self, models):

        ShowBase.__init__(self)
        data = []
        for model in models:
            path = "Models/"+model[0]+".obj"
            M = self.loader.loadModel(path)
            M.reparentTo(self.render)
            M.setScale(model[1], model[1], model[1])
            M.setPos(model[2][0], model[2][1], model[2][2])
            data.append(M)
        

app = MyApp(maps)

app.run()


# In[ ]:





# In[ ]:




