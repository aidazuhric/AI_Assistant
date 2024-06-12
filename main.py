from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

# Speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0-male, 1-female
activationWord = 'computer'

# Set the browser path
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# WolframAlpha configuration
appId = '6XX4WL-8RQQ4UY7UE'
wolframClient = wolframalpha.Client(appId)

def speak(text, rate=120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer() 
    print('Listening for a command')
    
    with sr.Microphone() as source:
        # Adjust for ambient noise
        listener.adjust_for_ambient_noise(source)
        listener.pause_threshold = 2
        
        print("Please say something...")
        try:
            input_speech = listener.listen(source, timeout=5, phrase_time_limit=10)  # Add timeout for better control
            print("Got it, processing...")
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return 'None'
    
    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'The input speech was: {query}')  
    except sr.UnknownValueError:
        print('Sorry, I did not understand that')
        speak('Sorry, I did not understand that')
        return 'None'
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        speak('Sorry, the speech service is not available')
        return 'None'
    return query

def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No wikipedia result')
        return 'No result received'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print('wikiPage.title')
    wikiSumarry = str(wikiPage.summary)
    return wikiSumarry

def listOrDict(var): # Results in search_wolframalpha can be either list or dictionary so we make the additional method which can parse wheter it's a list or a dictionary
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframalpha(query = ''):
    response = wolframClient.query(query)
    
    if response['@success'] == 'false': # @success means that Wolfram Alpha was able to resolve the query
        return 'Could not compute'
    else:
        result = ''
        # question
        pod0 = response['pod'][0] # pod is a list of results and it can contain subpods
        # May contain answer (Has highest confidence value)
        pod1 = response['pod'][1]

        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            result = listOrDict(pod1['subpod'])
            return result.split('(')[0] # Results may contain bracketed sections so we use result.split which gets us everything before the first bracket
        else:
            question = listOrDict(pod0['subpod'])
            return question.split('(')[0]
            # if failed we can search wikipedia instead
            speak('Computation failed. Querying universal databank.')
            return search_wikipedia(question)
            
# Main

if __name__ == '__main__':
    speak('All systems nominal')
    
    while True:
        query = parseCommand().lower().split()
        
        if query[0] == activationWord:
            query.pop(0)
            
            if query[0] == 'say': #configured activation word to be 'say'
                if 'hello' in query:
                    speak('Greetings.')
                else:
                    query.pop(0)
                    speech = ' '.join(query)
                    speak(speech)
                    
            # Web navigation
            if query[0] == 'go' and query[1] == 'to': #giving command with "Computer go to youtube.com (it will open any website)"
                speak('Opening...')
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)
                
            # Wikipedia
            if query[0] == 'wikipedia': # command example: 'Computer wikipedia London'
                query = ' '.join(query[1:])
                speak('Querying the universal databank.')
                speak(search_wikipedia(query))
                
            # Wolfram Alpha
            if query[0] == 'compute' or query[0] == 'computer': # command example: 'Computer compute distance from London to Paris'
                query = ' '.join(query[1:])
                speak('Computing')
                try:
                    result = search_wolframalpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')
                    
            # Note taking
            if query[0] == 'log': # command: 'Computer log' and then say anything
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(newNote)
                speak('Note written')

            if query[0] == 'exit':
                speak('Goodbye')
                break
            
