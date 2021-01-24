import nltk
from nltk.corpus import stopwords
import string

SUPPORTED_LANGUAGES = ['danish',
                       'dutch',
                       'english',
                       'finnish',
                       'french',
                       'german',
                       'hungarian',
                       'italian',
                       'norwegian',
                       'porter',
                       'portuguese',
                       'romanian',
                       'spanish',
                       'swedish']


class TextCleaner:

    def __init__(self, language):
        if language not in SUPPORTED_LANGUAGES:
            raise AttributeError('Language {} is not supported'.format(language))

        self.language = language
        self._stemmer = nltk.SnowballStemmer(language)
        self._stop_words = stopwords.words(language)
        self._lemmatizer = nltk.WordNetLemmatizer()

    def stem_text(self, text):
        sentences = nltk.sent_tokenize(text)
        sentences_stems = []
        for sentence in sentences:
            sentences_stems.append(self.stem_sentence(sentence))

        return sentences_stems

    def stem_sentence(self, sentence):
        sentence = sentence.translate(
            sentence.maketrans(string.punctuation, ' '*len(string.punctuation))
        )

        tokens = nltk.word_tokenize(sentence)
        stems = []

        for token in tokens:
            stem = self._stemmer.stem(token)
            if stem not in self._stop_words:
                stems.append(stem)

        return stems

    def clean_text(self, text):
        sentence_stems = self.stem_text(text)

        return sentence_stems
