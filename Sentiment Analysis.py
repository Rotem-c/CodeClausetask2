import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')
import nltk

data= pd.read_csv("D:/Reviews.csv")
data= data.head(500)
print(data.shape)

print(data.head())

# Quick EDA

print(data['Score'].value_counts())

ax= data['Score'].value_counts().sort_index().plot(kind='bar',
                                               title='Count of reviews by stars',
                                                figsize=(10,5))
ax.set_xlabel('Review Stars')
plt.show() 
example= data['Text'][50]
print(example)
tokens= nltk.word_tokenize(example)
print(tokens[:10])
tagged= nltk.pos_tag(tokens)
print(tagged[:10])
entities=nltk.chunk.ne_chunk(tagged)
entities.pprint()

#VADER
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

sia = SentimentIntensityAnalyzer()
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm

sia = SentimentIntensityAnalyzer()

print(sia.polarity_scores('I am so happy'))
print(sia.polarity_scores('This is the worst thing ever'))
print(sia.polarity_scores(example))

#Run the polarity score on the entire dataset
res={}
for i, row in tqdm(data.iterrows(),total=500):
    text=row['Text']
    myid=row['Id']
    res[myid]=sia.polarity_scores(text)

vaders=pd.DataFrame(res).T
print(vaders)

vaders=vaders.reset_index().rename(columns={'index':'Id'})
vaders=vaders.merge(data, how='left')

# sentiment scores in metadata
print(vaders.head())

ax=sns.barplot(data=vaders,x='Score',y='compound')
ax.set_title('Compound Scre by Amzon Star Reviews')
plt.show()

sns.barplot(data=vaders,x='Score',y='pos')
plt.show()

fig, axs = plt.subplots(1, 3, figsize=(12, 3))
sns.barplot(data=vaders, x='Score', y='pos', ax=axs[0])
sns.barplot(data=vaders, x='Score', y='neu', ax=axs[1])
sns.barplot(data=vaders, x='Score', y='neg', ax=axs[2])
axs[0].set_title('Positive')
axs[1].set_title('Neutral')
axs[2].set_title('Negative')
plt.tight_layout()
plt.show()

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# VADER results on example
print(example)
sia.polarity_scores(example)


# Run for Roberta Model
encoded_text = tokenizer(example, return_tensors='pt')
output = model(**encoded_text)
scores = output[0][0].detach().numpy()
scores = softmax(scores)
scores_dict = {
    'roberta_neg' : scores[0],
    'roberta_neu' : scores[1],
    'roberta_pos' : scores[2]
}
print(scores_dict)


def polarity_scores_roberta(example):
    encoded_text = tokenizer(example, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'roberta_neg' : scores[0],
        'roberta_neu' : scores[1],
        'roberta_pos' : scores[2]
    }
    return scores_dict


res = {}
for i, row in tqdm(data.iterrows(), total=len(data)):
    try:
        text = row['Text']
        myid = row['Id']
        vader_result = sia.polarity_scores(text)
        vader_result_rename = {}
        for key, value in vader_result.items():
            vader_result_rename[f"vader_{key}"] = value
        roberta_result = polarity_scores_roberta(text)
        both = {**vader_result_rename, **roberta_result}
        res[myid] = both
    except RuntimeError:
        print(f'Broke for id {myid}')

results_df = pd.DataFrame(res).T
results_df = results_df.reset_index().rename(columns={'index': 'Id'})
results_df = results_df.merge(data, how='left')

print(results_df.columns)

sns.pairplot(data=results_df,
             vars=['vader_neg', 'vader_neu', 'vader_pos',
                  'roberta_neg', 'roberta_neu', 'roberta_pos'],
            hue='Score',
            palette='tab10')
plt.show()

print(results_df.query('Score == 1') \
    .sort_values('roberta_pos', ascending=False)['Text'].values[0])


print(results_df.query('Score == 1') \
    .sort_values('vader_pos', ascending=False)['Text'].values[0])


print(results_df.query('Score == 5') \
    .sort_values('roberta_neg', ascending=False)['Text'].values[0])


print(results_df.query('Score == 5') \
    .sort_values('vader_neg', ascending=False)['Text'].values[0])

from transformers import pipeline

sent_pipeline = pipeline("sentiment-analysis")

print(sent_pipeline('I love sentiment analysis!'))
print(sent_pipeline('Make sure to like and subscribe!'))
print(sent_pipeline('booo'))