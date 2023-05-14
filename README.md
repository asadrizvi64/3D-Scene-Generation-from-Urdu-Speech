# 3D-Scene-Generation-from-Urdu-Speech
Urdu speech to image scene generator using numpy, pandas, and pandas3d visualizer library.
# Urdu Speech to 3D Scene
This project is a Python-based system that converts Urdu speech to a 3D scene. It includes the following functionalities:

- Online speech recognition using Google's Speech Recognition API
- Converting the Urdu script to Roman script for processing
- Preprocessing the text data, such as replacing similar words and pronouns
- Generating a 3D scene based on the processed text data, using Panda3D

## Getting Started
### Prerequisites
- Python 3.6+
- pip package installer
- Sounddevice, scipy, wavio, spacy, pandas, numpy, and other Python libraries (refer to requirements.txt)

### Installation
-> Clone the repository to your local machine using Git:
```git clone https://github.com/<username>/<repository>.git```
-> Change the directory to the cloned repository:
```cd <repository>```
-> Install the required packages using pip: 
```pip install -r requirements.txt```

### Usage
1. Run the following command to start the system: ```python main.py```
2. Follow the on-screen instructions to speak the Urdu text into the microphone. (5-second timer, start from "hey")
3. The system will process the spoken text and generate a 3D scene based on the processed data.

### Contributing
If you have any suggestions, please open an issue on the GitHub repository or create a pull request.
