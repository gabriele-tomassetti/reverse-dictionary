import sys
from pathlib import Path
import logging
import gensim
from gensim.models import KeyedVectors
from timeit import default_timer as timer
from flask import Flask, request, jsonify, render_template, logging
import webbrowser

def determine_words(definition):         
    possible_words = definition.split()
    for i in range(len(possible_words) - 1, -1, -1):
        if possible_words[i] not in model.vocab:                    
            del possible_words[i]          

    possible_expressions = []
    for w in [possible_words[i:i+3] for i in range(len(possible_words)-3+1)]:        
       possible_expressions.append('_'.join(w))            

    ex_to_remove = []

    for i in range(len(possible_expressions)):        
        if possible_expressions[i] in model.vocab:                    
            ex_to_remove.append(i)        

    words_to_remove = []    
    for i in ex_to_remove:
        words_to_remove += [i, i+1, i+2]        
    words_to_remove = sorted(set(words_to_remove))    

    words = [possible_expressions[i] for i in ex_to_remove]    
    for i in range(len(possible_words)):
        if i not in words_to_remove:
            words.append(possible_words[i])    

    return words
    
def find_words(definition, negative_definition):           
    positive_words = determine_words(definition)
    negative_words = determine_words(negative_definition)
           
    similar_words = [i[0] for i in model.most_similar(positive=positive_words, negative=negative_words, topn=30)]  

    words = []    

    for word in similar_words:
        if (word in dict_words):
            words.append(word)

    if (len(words) > 20):
        words = words[0:20]
    
    return words

def create_app():
    app = Flask(__name__)   
    return app

app = create_app()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        words = request.form['definition'].split()
        negative_words = ''
        positive_words = ''
        for i in range(len(words)):
            if(words[i][0] == '-'):                
                negative_words += words[i][1:] + ' '                
            else:                
                positive_words += words[i] + ' '    
        
        return jsonify(find_words(positive_words, negative_words))        
    else:
        return render_template('index.html')

def generate_optimized_version():
    model = KeyedVectors.load_word2vec_format("./models/GoogleNews-vectors-negative300.bin.gz", binary=True)
    model.init_sims(replace=True)
    model.save('./models/GoogleNews-vectors-gensim-normed.bin')

if __name__ == "__main__":
    global model
    global dict_words
    
    # read dictionary words
    dict_words = []
    f = open("./models/words.txt", "r")
    for line in f:
        dict_words.append(line.strip())    
    f.close()    
    # remove copyright notice    
    dict_words = dict_words[44:]      

    app.logger.warning("Loading Word2Vec model...")
    start = timer()        
    # Load Google's pre-trained Word2Vec model. 
    optimized_file = Path('./models/GoogleNews-vectors-gensim-normed.bin')
    if optimized_file.is_file():        
        model = KeyedVectors.load("./models/GoogleNews-vectors-gensim-normed.bin",mmap='r')
    else:
        generate_optimized_version()
    
    # keep everything ready    
    model.syn0norm = model.syn0  # prevent recalc of normed vectors    

    app.logger.warning("Word2Vec Model loaded")            
    end = timer()
    app.logger.warning("It took %d seconds to load the model" % (end - start))    
    
    # launch web browser
    webbrowser.open("http://127.0.0.1:5000",new=2)
    
    # start Flask app
    app.run()