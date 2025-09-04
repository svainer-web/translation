# Doctrine Translation
## pranslation Phases:
### 1. Create Dictionary and add him in doctrine file

This part running only once to add language support to doctrines

To do this you must run 2 scripts:
- addLanguages.py - add <DictionaryIndex> to all doctrine files with text
- createDictionary.py - create Xml Dictionary file and replace test to index

### 2. To create translation:
- createDictionary.py - write separated files in 2 directories hebrew and english.

- In format : 
```
1 
data
2 
data2
```

- use ```Google jules``` to convert texts.
prompts: 
- hebrew
```
I want you to go over the files in the folder ./hebrew/ and for each create a new text file similar to this one in the path ./hebrew/translated/ . I want it to be a translation of the exact strings in this file from Hebrew to English. pay attension to the fact that all of those strings are related to military air-force army context so take that in mind while tranlating. In addition, when Hebrew says "מבנה" its related to a groug of aircrafts (meaning a formation). Do not translate file if it already in tranlated folder
```
- english
```
Now I want you to go over the files in the folder ./english/ and for each create a new text file similar to this one in the path ./english/translated/ . I want it to be a translation of the exact strings in this file from English to Hebrew. pay attension to the fact that all of those strings are related to military force army context so take that in mind while tranlating. In addition, file name show army category. Do not translate file if it already in tranlated folder
```

- return Dictionary.py - return strings to Dictionary xml files