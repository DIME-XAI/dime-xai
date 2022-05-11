from gensim.models import Word2Vec

# Gensim needs a list of lists to represent tokens in a document.
# In real life you’d read a text file and turn it into lists here.
text = ["this is a sentence", "so is this", "and we're all talking"]
tokens = [t.split(" ") for t in text]

# This is where we train new word embeddings.
model = Word2Vec(sentences=tokens, window=3,
                 min_count=1, workers=2)

# This is where they are saved to disk.
model.wv.save("wordvectors.kv")
