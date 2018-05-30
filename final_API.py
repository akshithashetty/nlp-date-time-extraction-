from flask import Flask
from flask import json
from flask import request
from flask import jsonify
import parsedatetime
import re
import datetime
import nltk
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import state_union
import spacy
import en_core_web_sm
from spacy.matcher import Matcher
nltk.download('state_union')
app = Flask(__name__)



@app.route('/date', methods = ['GET','POST'])

def time_final():
#Below is a python function that takes an input string and prints date and time extracted from it using the regular expression patterns
    content=request.json
    s=content['sms']
    def date_time_extract(s):
        #1-Jan-2018
        pattern1 = r'((?:\d{1,2}[- ,./]*)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ,./]*\d{4})'
        #1-jan-2018
        pattern2 = r'((?:\d{1,2}[- ,./]*)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[- ,./]*\d{4})'
        #1-jan-18
        pattern3= r'((?:\d{1,2}[- ,./]*)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[- ,./]*\d{2})'
        #1-Jan-18
        pattern4 = r'((?:\d{1,2}[- ,./]*)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ,./]*\d{2})'
        # 1 st jan 2018
        pattern5=r'((?:\d{1,2}[- ,./]*)(?:st|st of|th|of|th of )[a-z]*[- ,./]*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[- ,./]*\d{4})'
        # 1 st  of Jan
        pattern6=r'((?:\d{1,2}[- ,./]*)(?:th|st|st of|of|th of )[a-z]*[- ,./]*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ,./]*\d{4})'
        #dd/mm/yyyy
        pattern7=r'((?:\d{1,2}[- ,./]*)(?:\d{1,2}[- ,./]*)[- ,./]*\d{4})'

        #time
        pattern8=r'([01]?[0-9][:.][0-9]{2}?\s?[ap]m)'

        pattern=pattern1+"|"+pattern2+"|"+pattern3+"|"+ pattern4+"|"+pattern5+"|"+pattern6+"|"+pattern7+"|"+pattern8



        mydate=re.compile(pattern)
        mydate=mydate.findall(s,re.I)


        for match in mydate:
            for item in match:
                if item!='':
                    return(item)
    def time_extract(s):
        pattern8=r'([01]?[0-9][:.][0-9]{2}?\s?[ap]m)'


        pattern=pattern8
        mydate=re.compile(pattern)
        mydate=mydate.findall(s,re.IGNORECASE)


        for match in mydate:

            return(match)


    y=date_time_extract(s)

    if (y==None):
        cal = parsedatetime.Calendar()
        date_timestruct=cal.parse(s)
        temp=list(date_timestruct)
        res=temp[0]
        year=str(res.tm_year)
        month=str(res.tm_mon)
        day=str(res.tm_mday)
        hour=str(res.tm_hour)
        minute=str(res.tm_min)
        sec=str(res.tm_sec)

        return((month+"-"+day+"-"+year+'   '+hour+":"+ minute + ":" + sec))


    else:
        print(y)
        print(time_extract(s))
        return y+'   '+(time_extract(s))



@app.route('/title', methods = ['GET','POST'])
def process_content():


        content=request.json

        s=content['sms']


        train_text = state_union.raw("2005-GWBush.txt")
        custom_sent_tokenizer = PunktSentenceTokenizer(train_text)
        tokenized = custom_sent_tokenizer.tokenize(s)

        i=(tokenized[0])


        words=nltk.word_tokenize(i)



        ref=["Mrs.","Lets","Dear","Thanks","Thank","dear","Hello","Hi","Mr.","Miss"]
        for a in words :
            if a in ref:
                no=words.index(a)
                del words[no]

                del words[no]


        tagged = nltk.pos_tag(words)


        chunkGram = r"""NP: {(<DT>?<JJ>*(<NN>|<NNS>|<NNP>)+<JJ>*<C.>*<IN>*<TO>*(<PRP>|<PRP.>)*<RB.>*)*}
                        """
        chunkParser = nltk.RegexpParser(chunkGram)

        chunked = chunkParser.parse(tagged)


        def filt(x):
            return x.label()=='NP'


        for subtree in chunked.subtrees(filter =  filt):
             # Generate all subtrees

             n= (len(subtree))
             a=list((subtree[n-1]))
             if ((a[1]) == "IN"):
                 remove=True
             else :
                 remove=False



             output=' '.join([w for w, t in subtree.leaves()])
             if remove:
                 output=output.rsplit(' ', 1)[0]

             return(output)


             break



@app.route('/location', methods = ['GET','POST'])
def location():
    content=request.json

    s=content['sms']
    nlp = en_core_web_sm.load()

    matcher = Matcher(nlp.vocab)

    pattern = [ {'LOWER': 'at'},{'POS': 'DET','OP': '*'},{'POS': 'ADJ','OP': '*'},{'POS': 'NOUN','OP': '*'},{'POS': 'PROPN','OP': '*'}]
    matcher.add('loc1', None, pattern)

    doc = nlp(s)

    matches = matcher(doc)



    for match_id, start, end in matches :
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start : end]  # get the matched slice of the doc
        ans=span.text

        ans1=ans.lstrip('at')
        return(ans1)
        break

    ref=["LOC","ORG","GPE","FAC"]
    if (matches==[]):

        for ent in doc.ents:

            if (ent.label_) in ref:
                return(ent.text)
                break




if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1',port=8000,debug=True)
