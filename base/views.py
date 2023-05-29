from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import random
import nltk
from nltk.corpus import wordnet
from django.http import JsonResponse
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        return redirect('home')
    
    return render(request, 'signup.html')

def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def logout1(request):
    logout(request)
    return render(request,'logout.html')

conversation = {"hello":["hello","hey, hello how can i help you"],"who are you":["i am lms chatbot"," am a chatbot"],"how are you":["I'm great, thank you! How can I assist you today?" ,"I'm great, thank you!"],"what's the weather like today":["The weather is sunny and warm today. It's a perfect day to go outside!"],"How can I reset my password?":["To reset your password, you can go to the login page and click on the 'Forgot Password'."],"what are the tools available":['''<ul>
  <li>User Management</li>
  <li>Course Management</li>
  <li>Content Management</li>
  <li>Learning Material Access</li>
  <li>Assessment and Grading</li>
  <li>Communication Tools</li>
  <li>Progress Tracking</li>
</ul>
'''],"who are the lms  developers":['''<ul>
  <li> <img style="width:40px;border-radius:80px;height:40px" src="" alt="pic"> <a href="https://github.com/NagiPragalathan">  Nagi Pragalathan</a></li>
  <li> <img src="https://github.com/glorysherin/JEC/blob/main/kokila.jpeg" alt="pic"><a href="https://github.com/jkokilaCSE">Kokila</a></li>
  <li><img src="https://github.com/glorysherin/JEC/blob/main/Glory.jpeg" alt="pic "<a href="https://github.com/glorysherin">Glory Sherin</a></li>
  <li><img src="" alt="pic "<a href="https://github.com/MohanKumarMurugan">Mohan Kumar</a></li>
</ul>
''']}
# Define synonyms for common question words
synonyms = {"what": ["what", "which", "where", "when", "how"],
            "is": ["is", "are", "am", "was", "were", "be", "being", "been"]}

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return list(synonyms)

def have_similar_meanings(word1, word2):
    for syn1 in get_synonyms(word1):
        for syn2 in get_synonyms(word2):
            if syn1 == syn2:
                return True
    return False

# Create your views here.

def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about-us.html')

def get_stackoverflow_link(question, site='stackoverflow.com'):

    num_results = 30

    stackoverflow_link = ""
    # Search Google for the question and get the top search results
    if "write a" in question.lower():
        url = 'https://www.google.com/search?q={}&num={}&hl=en&tbm=isch&tbo=u&source=univ&sa=X&ved=0ahUKEwiB4ZG4-d3wAhXB4zgGHUaXDbUQsAQIYw'.format(question + " site:stackoverflow.com", 5)
        search_results = search(url, num_results=20)
    else:
        search_results = search(question, num_results=num_results)
    common=[]
    # Loop through the search results and find the Stack Overflow link
    for result in search_results:
        print("result,result",result)
        common.append(result)
        if site in result:
            stackoverflow_link = result
            break
    if stackoverflow_link != "":
        return stackoverflow_link
    else:
        return common[0]

def get_answer_from_given_link(question_url):
    code = ''
    response = requests.get(question_url)

    soup = BeautifulSoup(response.content, 'html.parser')
    # responsive-tabs
    try:
        question_title = soup.find('a', class_='question-hyperlink').get_text()
        print('Question:', question_title)

        print('run next....')
        # Find the code blocks in the question and print them
        code_blocks = soup.find_all('pre')
        print(code_blocks)
        for i, code_block in enumerate(code_blocks):
            print(f'\nExample code {i+1}:')
            print(code_block.get_text())
            code = code+str(code_block)
    except:
        code = soup.get_text()
    return code

# Process user input and generate an appropriate response
def respond_to_input(user_input):
    # Check if input matches a conversation keyword
    for key in conversation:
        if user_input.lower() == key:
            return random.choice(conversation[key])
    
    # Check if input is a question
    question_words = synonyms["what"]
    if user_input.lower().startswith(tuple(question_words)):
        # Extract the main verb from the question
        # tokens = nltk.word_tokenize(user_input.lower())
        # pos_tags = nltk.pos_tag(tokens)
        # verbs = [token for token, pos in pos_tags if pos.startswith('V')]
        # if len(verbs) > 0:
        #     main_verb = verbs[0]
            # Check if the main verb has a similar meaning to "is"
            # if have_similar_meanings(main_verb, "is"):
                link = get_stackoverflow_link(user_input)
                code = get_answer_from_given_link(link)
                if code:
                    response = code
                else:
                    wikipedia.set_lang("en")
                    # Get the summary of a page
                    page = wikipedia.page(user_input)
                    summary = page.summary
                    response = summary
                return response
    link = get_stackoverflow_link(user_input)
    code = get_answer_from_given_link(link)
    if code:
        response = code
    else:
        wikipedia.set_lang("en")
        # Get the summary of a page
        page = wikipedia.page(user_input)
        summary = page.summary
        response = summary
    return response


def chatbot_res(request):
    if request.method == "GET":
        message = request.GET.get("message")
        response = respond_to_input(message)
        return JsonResponse({"response": response})
    else:
        return JsonResponse({"error": "Invalid request method"})
