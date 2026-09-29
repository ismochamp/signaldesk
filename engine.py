"""Trainable multinomial Naive Bayes text classifier with abstention."""
from collections import Counter,defaultdict
import math,re
STOP=set('the a an is are to of and or for in on with i we my our this that it be can you please'.split())
def tokens(text):return [x for x in re.findall(r'[^\W_]+',text.lower(),re.UNICODE) if len(x)>1 and x not in STOP]
def predict(examples,text):
    labels=Counter(label for _,label in examples)
    if len(labels)<2:raise ValueError('Train at least two categories before classifying requests.')
    counts=defaultdict(Counter)
    for sample,label in examples:counts[label].update(tokens(sample))
    vocab=set().union(*(set(c) for c in counts.values()))
    if not vocab:raise ValueError('Training examples contain no usable words.')
    query=Counter(tokens(text));known=set(query)&vocab
    logs={}
    for label,count in labels.items():
        logs[label]=math.log(count/len(examples))+sum(query[word]*math.log((counts[label][word]+1)/(sum(counts[label].values())+len(vocab))) for word in known)
    peak=max(logs.values());normal=sum(math.exp(v-peak) for v in logs.values())
    scores=sorted([{'label':k,'score':round(math.exp(v-peak)/normal,4)} for k,v in logs.items()],key=lambda r:(-r['score'],r['label']))
    coverage=len(known)/max(1,len(query));top=scores[0]
    needs_review=top['score']<.8 or coverage<.3 or len(known)<2
    return {'label':top['label'] if known else 'Unclassified','score':top['score'] if known else 0,'scores':scores,'coverage':round(coverage,3),'matched_terms':sorted(known),'needs_review':needs_review,'training_examples':len(examples)}
