import os
import pickle
import datetime
from tpsx import TextCleaner

DANISH = 'danish'
DUTCH = 'dutch'
ENGLISH = 'english'
FINNISH = 'finnish'
FRENCH = 'french'
GERMAN = 'german'
HUNGARIAN = 'hungarian'
ITALIAN = 'italian'
NORWEGIAN = 'norwegian'
PORTER = 'porter'
PORTUGUESE = 'portuguese'
ROMANIAN = 'romanian'
SPANISH = 'spanish'
SWEDISH = 'swedish'


class Result:
    """
    This class represents the output of the algorithm
    contains all the information used to determine the score of a topics
    and the score of the topics

    Variables
    ----------
    topics: Topic
        Represent the topics the output refers to
    related_words: list
        A list of the Words that are related with the Topic
    related_words_num: int
        The number of related sentences
    related_topics: list
        A list of Result with a relation between the topics
    related_topics_num: int
        The number of related topics
    score: float
        The score of the topics
    topic_score:
        The final score merged with the other topics
    """

    def __init__(self, topic):
        """
        :param topic: Topic
            Topic the output refers to
        """
        self.topic = topic
        self.related_words = []
        self.related_words_num = 0
        self.related_topics = []
        self.related_topics_num = 0
        self.score = 0
        self.topic_score = 0

    def merge_topics(self):
        for topic_index in range(self.related_topics_num):
            if self.related_topics[topic_index][0]:
                self.topic_score += self.related_topics[topic_index][1].score
            else:
                self.topic_score -= self.related_topics[topic_index][1].score

        return self.topic_score

    def show_data(self, details=False):
        print(self.__str__(details))

    def __str__(self, details=True):
        string = f"{'-' * 20} {self.topic.label} {'-' * 20}\n"
        string += f"Score: {self.score}"
        string += f"\nTopic score: {self.topic_score}\n\n"
        if details:
            string += 'Related sentences\n'
            for word in self.related_words:
                string += f"\n\tWord - [id {word._id}, label {word.label}]"
            string += f"\n\nRelated sentences count = {self.related_words_num}"
            if self.related_topics_num:
                string += '\n\nRelated topics'
                for coexist, related_topic in self.related_topics:
                    string += f'\n\tTopic {"-" if coexist else "x"} [id {related_topic.topic._id}, label {related_topic.topic.label}]'
                string += f"\n\nRelated topics count = {self.related_topics_num}"
            string += '\n\n'

        return string


class Word:
    """
        This class is used to represent a Topic
    """
    _ids = 0

    def __init__(self, word):
        """
        :param word: str
        """
        Word._ids += 1
        self._id = Word._ids
        self.label = word
        self.count = 1

    def __str__(self):
        return f"""{'-'*20} id {self._id} {'-'*20}\nword = {self.label}\noccurrences = {self.count}\n"""


class Topic:
    """
    This class is used to represent a Topic
    """
    _ids = 0

    def __init__(self, label):
        """
        :param label: str
            A label that represent the topics
        """
        Topic._ids += 1
        self._id = Topic._ids
        self.label = label

    def __str__(self):
        return f"""{'-'*20} id {self._id} {'-'*20}\ntopic_label = {self.label}\n\n"""


class Relation:
    """
    This class is used to represent the relation of a topics and a word
    """
    _ids = 0

    def __init__(self, topic, word):
        """
        :param topic: Topic
            A topics object
        :param word: str
        """
        Relation._ids += 1
        self._id = Relation._ids
        self.topic = topic
        self.word = word
        self.word_count = 1
        self.weight = self.word_count / word.count

    def __str__(self):
        return f"{'-'*20} id {self._id} {'-'*20}\ntopic_label = {self.topic.label} \
                \nword = {self.word.label}\nweight = {self.weight}\n\n"


class RelatedTopic:
    """
    This class is used to represent a relation between
    two topics
    """
    _ids = 0

    def __init__(self, topic1, topic2, coexist, bidirectional):
        """
        :param topic1: str
            Label of the first topics
        :param topic2: str
            Label of the second topics
        :param coexist: bool
        :param bidirectional: bool
            If bidirectional is true topics have a shared relation
            topic1 -- topic2
            If bidirectional is false topics have a one way relation
            topic1 -> topic2
        """
        RelatedTopic._ids += 1
        self._id = RelatedTopic._ids
        self.topic1 = topic1
        self.topic2 = topic2
        self.coexist = coexist
        self.bidirectional = bidirectional

    def __str__(self):
        return f"{'-'*20} id {self._id} {'-'*20}\n{self.topic1} -{'-' if self.coexist else 'x'}{'-' if self.bidirectional else '>'} {self.topic2}"


class TopicsExtractor:
    """
    This class is used to create and execute the model
    to extract the text topics
    """

    def __init__(self, language):
        """
        :param language: str
            language used in the model
            [english]
        """
        self.language = language.lower()
        self.cleaner = TextCleaner(language)

        self.words = []
        self.topics = []
        self.relations = []
        self.related_topics = []

    def _spread_word(self, word, topic_label, count):
        exists = False
        for relation in self.relations:
            if relation.word.label == word.label:
                if relation.topic.label == topic_label:
                    exists = True
                    relation.word_count += 1
                    relation.weight = relation.word_count / count
                    break
                else:
                    relation.weight = relation.word_count / count

        if not exists:
            topic = self.get_topic(topic_label)

            if not topic:
                raise ValueError(f'Topic: {topic_label} is not defined')

            new_relation = Relation(topic, word)
            self.relations.append(new_relation)

    def add_word(self, word_label, topic_label):
        """Adds a word related to a topics

        :param word_label: str
        :param topic_label: str
        """
        count = 1
        exists = False
        word_res = None
        for word in self.words:
            if word.label == word_label:
                word_res = word
                exists = True
                count = word.count + 1
                word.count = count
                break

        if not exists:
            word_res = Word(word_label)
            self.words.append(word_res)

        self._spread_word(word_res, topic_label, count)

    def add_topic(self, topic_label):
        """Adds a topics

        :param topic_label: str
        :return: bool
        """
        exists = False
        for topic in self.topics:
            if topic.label == topic_label:
                exists = True
                topic_res = topic_label
                break

        if not exists:
            self.topics.append(Topic(topic_label))
            return True

        return False

    def _build_relation(self, topic1, topic2, coexist=True, bidirectional=True):
        exists = False
        topic_res = None

        if topic1 == topic2:
            raise ValueError('Can\'t create a relation with the same topics')

        if not self.get_topic(topic1):
            raise ValueError(f'Topic1 is not defined: {topic1}')

        if not self.get_topic(topic2):
            raise ValueError(f'Topic2 is not defined: {topic2}')

        for related_topic in self.related_topics:
            if related_topic.topic1 == topic1 and related_topic.topic2 == topic2:
                exists = True
                topic_res = related_topic
                topic_res.bidirectional = bidirectional
                break
            elif related_topic.topic2 == topic1 and related_topic.topic1 == topic2:
                exists = True
                topic_res = related_topic
                if not topic_res.bidirectional and not bidirectional:
                    topic_res.bidirectional = bidirectional
                    temp = topic_res.topic1
                    topic_res.topic1 = topic_res.topic2
                    topic_res.topic2 = temp
                elif topic_res.bidirectional and not bidirectional:
                    topic_res.bidirectional = False
                    temp = topic_res.topic1
                    topic_res.topic1 = topic_res.topic2
                    topic_res.topic2 = temp
                break

        if not exists:
            topic_res = RelatedTopic(topic1, topic2, coexist, bidirectional)
            self.related_topics.append(topic_res)
        else:
            topic_res.coexist = coexist

        return topic_res

    def add_related_topic(self, topics_set1, topics_set2, coexist=True, bidirectional=True):
        """Adds a relation between two topics

        If bidirectional is true topics have a shared relation
        topic1 -- topic2
        If bidirectional is false topics have a one way relation
        topic1 -> topic2

        :param topics_set1: str or list
        :param topics_set2: str or list
        :param coexist: bool
        :param bidirectional: bool
        :return: list
        """

        topic_res = []

        if not isinstance(topics_set1, str) and not isinstance(topics_set1, list) \
                or not isinstance(topics_set2, str) and not isinstance(topics_set2, list):
            raise ValueError('topics_sets must be str or list of str')

        if isinstance(topics_set1, str):
            topics_set1 = [topics_set1]

        if isinstance(topics_set2, str):
            topics_set2 = [topics_set2]

        for topics_set1_element in topics_set1:
            for topics_set2_element in topics_set2:
                topic_res.append(self._build_relation(topics_set1_element,
                                                  topics_set2_element,
                                                  coexist,
                                                  bidirectional))

        return topic_res

    def get_related_topic(self, topic_label):
        """Get the related topics of a topics by its label

        :param topic_label: str
        :return: list of str
        """
        topic_res = []

        if not self.get_topic(topic_label):
            raise ValueError(f'Topic is not defined: {topic_label}')

        for related_topic in self.related_topics:
            if related_topic.bidirectional:
                if related_topic.topic1 == topic_label:
                    if related_topic.topic2 not in topic_res:
                        topic_res.append([related_topic.coexist, related_topic.topic2])
                elif related_topic.topic2 == topic_label:
                    if related_topic.topic1 not in topic_res:
                        topic_res.append([related_topic.coexist, related_topic.topic1])
            else:
                if related_topic.topic1 == topic_label:
                    if related_topic.topic2 not in topic_res:
                        topic_res.append([related_topic.coexist, related_topic.topic2])

        return topic_res

    def get_topic(self, topic_label):
        """Get a topic_label object with the same label

        :param topic_label:
        :return: Topic
        """
        topic_res = None
        for topic_index in range(len(self.topics)):
            if self.topics[topic_index].label == topic_label:
                topic_res = self.topics[topic_index]
                break

        return topic_res

    def merge_topics(self, topics):
        """Merge Results based on the defined topic_label relations

        :param topics: dict
        :return:
        """
        for topic in topics:
            for coexist, related_topic in self.get_related_topic(topic):
                if related_topic in topics:
                    topics[topic].related_topics.append([coexist, topics[related_topic]])
            topics[topic].related_topics_num = len(topics[topic].related_topics)
            topics[topic].merge_topics()

        return topics

    def train(self, topics=None, examples=None):
        """Give examples of sentences related to a topic_label

        :param topics: str
        :param examples: list
        """
        if not isinstance(topics, str) and not isinstance(topics, list):
            raise ValueError('topics must be str or list of str')

        topics_list = []

        if isinstance(topics, str):
            self.add_topic(topics)
            topics_list.append(topics)
        else:
            for topic in topics:
                if not isinstance(topic, str):
                    raise ValueError('Invalid topic in list of topics, must be a str')
                self.add_topic(topic)
                topics_list.append(topic)

        if not isinstance(examples, str) and not isinstance(examples, list):
            raise ValueError('example must be str or list of str')

        cleaned_data = []

        if isinstance(examples, str):
            for data_sentence in self.cleaner.clean_text(examples):
                for data in data_sentence:
                    cleaned_data.append(data)
        else:
            for example in examples:
                if not isinstance(example, str):
                    raise ValueError('Invalid example in list of examples, must be a str')
                for data_sentence in self.cleaner.clean_text(example):
                    for data in data_sentence:
                        cleaned_data.append(data)

        for word in cleaned_data:
            for topic in topics_list:
                self.add_word(word, topic)

    def _execute_prediction(self, words, merge_topics):
        topics = {}

        for data_word in words:
            for relation in self.relations:
                if relation.word.label == data_word:
                    if relation.topic.label in topics.keys():
                        # Add the weight of a existing topics - word relation to a Result
                        topics[relation.topic.label].score += relation.weight
                        topics[relation.topic.label].related_words.append(relation.word)
                        topics[relation.topic.label].related_words_num += 1
                        topics[relation.topic.label].topic_score += relation.weight
                    else:
                        # Create a new Result with the current topics
                        result = Result(relation.topic)
                        result.related_words.append(relation.word)
                        result.related_words_num += 1
                        result.score = relation.weight
                        topics[relation.topic.label] = result
                        topics[relation.topic.label].topic_score = relation.weight

        if merge_topics:
            topics = self.merge_topics(topics)

        return topics

    def predict(self, sentences, merge_topics=True):
        """Predict the topic_label of a list of words

        If merge_topics is true the output topics score will be merged based
        on the defined topic_label relations

        To define topics relations use set_related_topics method

        :param sentences: list
        :param merge_topics: bool
        :return:
        """

        if not isinstance(sentences, str) and not isinstance(sentences, list):
            raise ValueError('Invalid sentences must be a str or a list of str')

        cleaned_data = []

        if isinstance(sentences, str):
            for data_sentence in self.cleaner.clean_text(sentences):
                for data in data_sentence:
                    cleaned_data.append(data)
        else:
            for sentence in sentences:
                if not isinstance(sentence, str):
                    raise ValueError('Invalid sentence in list of examples, must be a str')
                for data_sentence in self.cleaner.clean_text(sentence):
                    for data in data_sentence:
                        cleaned_data.append(data)

        topics = self._execute_prediction(cleaned_data, merge_topics)

        return topics

    def save(self, path=None, filename=None):
        """Save the current model

        :param path:
        :param filename:
        :return:
        """
        if not path:
            path = '/'

        if not os.path.exists(path):
            os.mkdir(path)

        if not filename:
            filename = f'{datetime.datetime.now().strftime("%y%m%d%H%M%S")}-db.pickle'

        try:
            with open(os.path.join(path, filename), 'wb') as file:
                pickle.dump(obj=self, file=file)
                return 0
        except:
            return 1

    @classmethod
    def load(cls, file_path):
        """Load a saved model

        :param file_path: path to the file
        :return: return a TopicsExtractor object with the loaded data
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError()
        with open(file_path, 'rb') as file:
            return pickle.load(file)
