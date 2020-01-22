from xml.dom import minidom
import xml.etree.ElementTree as Et


class SplitXMLFormat(object):
    def __init__(self, data, output_file):
        self.data = data
        self.output_file = output_file

    @staticmethod
    def __prettify(elements):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = Et.tostring(elements, 'utf-8')
        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent='\t')

    def convert(self):
        # create the file structure
        sentences = Et.Element('sentences')

        index = 1
        for element in self.data:
            sentence = Et.SubElement(sentences, 'sentence')
            sentence_text = Et.SubElement(sentence, 'text')
            sentence.set('id', str(index))
            sentence_text.text = element['sentence']

            if element['term'] is not None:
                aspect_terms = Et.SubElement(sentence, 'aspectTerms')
                aspect_term = Et.SubElement(aspect_terms, 'aspectTerm')
                for term in element['term']:
                    aspect_term.set('term', term[0])
                    aspect_term.set('polarity', element['sentiment'])
                    aspect_term.set('from', str(term[1]))
                    aspect_term.set('to', str(term[2]))

            index += 1

        # create a new XML file with the results
        xmlstr = self.__prettify(sentences)
        with open(self.output_file, 'w') as f:
            f.write(xmlstr)
