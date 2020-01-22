

class SplitIlwaanetFormat(object):
    def __init__(self, data, output_file):
        self.data = data
        self.output_file = output_file

    @staticmethod
    def __get_word_length(term):
        word_split = term.split()
        word_length = len(word_split)

        return word_length, word_split

    @staticmethod
    def __get_tag(sentiment):
        tag = ''
        if sentiment == 'negative':
            tag = '/n'
        elif sentiment == 'positive':
            tag = '/p'

        return tag

    @staticmethod
    def __set_tag(processed_sentence, end, tag):
        tagged_sentence = processed_sentence[:end] + tag + processed_sentence[end:]

        return tagged_sentence

    @staticmethod
    def __set_tag_two_or_more_words(sentence, words, start, tag):
        tagged_sentence = ''
        processed_sentence = sentence

        for word in words:
            end = start + len(word)
            tagged_sentence = processed_sentence[:end] + tag + processed_sentence[end:]
            processed_sentence = tagged_sentence
            start = end + len(tag) + 1

        return tagged_sentence

    def __insert_tag(self, sentence, terms, sentiment):
        tagged_sentence = ''
        tag = self.__get_tag(sentiment)

        # only one aspect term
        if len(terms) == 1:
            # term is a tuple (term, from_index, to_index)
            term = terms[0]
            word_length, word_split = self.__get_word_length(term[0])

            # one aspect term, one word
            if word_length == 1:
                tagged_sentence = self.__set_tag(sentence, term[2], tag)

            # one aspect term, two or more words
            elif word_length > 1:
                tagged_sentence = self.__set_tag_two_or_more_words(sentence, word_split, term[1], tag)

        # more than one aspect term
        elif len(terms) > 1:
            tagged_sentence = sentence
            start = 0
            for flag, term in enumerate(terms):
                if flag == 0:
                    end = term[2]
                else:
                    end = term[2] + len(tag)
                    start = term[1] + len(tag)

                # term is a tuple (term, from_index, to_index)
                word_length, word_split = self.__get_word_length(term[0])

                # two aspect terms, one word
                if word_length == 1:
                    tagged_sentence = self.__set_tag(tagged_sentence, end, tag)

                # two aspect terms, two or more words
                elif word_length > 1:
                    tagged_sentence = self.__set_tag_two_or_more_words(tagged_sentence, word_split, start, tag)

        return tagged_sentence

    def convert(self):
        f = open(self.output_file, 'w')
        for element in self.data:
            if element['term'] is not None:
                # sort by second element
                term = list(set(element['term']))
                term = sorted(term, key=lambda x: x[1])

                if term is not None:
                    tagged_sentence = self.__insert_tag(element['sentence'], term, element['sentiment'])
                    # print(tagged_sentence)
                    f.write(tagged_sentence + '\n')

        f.close()

if __name__ == '__main__':
    check = [
        {
            'sentence': 'Failed password for user root',
            'term': [('user', 20, 24)],
            'sentiment': 'negative'
        },
        {
            'sentence': 'Failed password for identification string root',
            'term': [('identification string', 20, 41)],
            'sentiment': 'negative'
        },
        {
            'sentence': 'PS/2 mouse device common for all mice',
            'term': [('PS/2', 0, 4), ('device', 11, 17)],
            'sentiment': 'positive'
        },
        {
            'sentence': 'Failed user password for identification string root',
            'term': [('user', 7, 11), ('identification string', 25, 46)],
            'sentiment': 'negative'
        },
    ]

    s = SplitIlwaanetFormat(check, 'test.txt')
    s.convert()

