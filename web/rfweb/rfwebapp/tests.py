import unittest
from StringIO import StringIO

from rfweb.rfwebapp.views.upload import SuitData, InvalidXmlError

VALID_SPEC = '''
<keywordspec generated="20090428 20:43:40" type="suite" name="TestSuit">
<version>1.0</version>
<doc>This is documentation</doc>
<init>
<doc>Init Doc</doc>
<arguments>
<arg>arg1</arg>
<arg>arg2=default</arg>
</arguments>
</init>
<kw name="KW 1">
<doc>Kw doc</doc>
<arguments>
<arg>arg</arg>
</arguments>
</kw>
<kw name="Keyword 2">
<doc></doc>
<arguments>
</arguments>
</kw>
<kw name="Another Keyword">
<doc></doc>
<arguments>
<arg>arg1</arg>
<arg>arg2=default</arg>
<arg>*args</arg>
</arguments>
</kw>
</keywordspec>
'''


class TestSuitData(unittest.TestCase):

    def test_parsing_suit_data(self):
        data = SuitData(self._create_input(VALID_SPEC))
        self.assertEqual(data.name, 'TestSuit')
        self.assertEqual(data.doc, 'This is documentation')
        self.assertEqual(data.version, '1.0')

    def test_parsing_keyword_data(self):
        data = SuitData(self._create_input(VALID_SPEC))
        expected = [('KW 1', 'Kw doc', 'arg'), 
                    ('Keyword 2', '', ''), 
                    ('Another Keyword', '', 'arg1, arg2=default, *args')]
        self.assertEqual(len(data.kws), 3)
        for kw, (name, doc, args) in zip(data.kws, expected):
            self.assertEqual(kw.name, name)
            self.assertEqual(kw.doc, doc)
            self.assertEqual(kw.args, args)

    def test_parsing_init_data(self):
        data = SuitData(self._create_input(VALID_SPEC))
        self.assertEqual(len(data.inits), 1)
        self.assertEqual(data.inits[0].doc, 'Init Doc')
        self.assertEqual(data.inits[0].args, 'arg1, arg2=default')
        self.assertEqual(data.inits[0].name, '<init>')

    def test_parsing_empty_documentations(self):
        data = SuitData(self._create_input('''
<keywordspec type="suite" name="Test">
<doc></doc>
<kw name="KW 1"><doc></doc><arguments/></kw>
</keywordspec>'''))
        self.assertEqual(data.doc, '')
        self.assertEqual(data.kws[0].doc, '')

    def test_parsing_spec_with_incomplete_data_fails(self):
        self._assert_parsing_fails('<keywordspec/>')

    def test_parsing_spec_without_keywords_fails(self):
        self._assert_parsing_fails('<keywordspec type="suite" name="Test">'
                                   '<doc></doc></keywordspec>')

    def test_iterating_spec_with_incomplete_keyword_data_fails(self):
        self._assert_parsing_fails('''
<keywordspec name="SuitName">
<doc></doc>
<kw name="Another Keyword">
</kw>
</keywordspec>''')

    def test_parsing_non_xml_fails(self):
        self._assert_parsing_fails('This is not xml')

    def test_parsing_invalid_xml_fails(self):
        self._assert_parsing_fails('<invalid_root_tag/>')

    def test_parsing_old_style_suit_data(self):
        data = SuitData(self._create_input('''
<keywordspec type="suite" name="Test">
<doc>No version here</doc>
<keywords><kw name="KW 1"><doc>KW 1 doc</doc><arguments/></kw></keywords>
</keywordspec>'''))
        self.assertEqual(data.name, 'Test')
        self.assertEqual(data.doc, 'No version here')
        self.assertEqual(data.version, '<unknown>')
        self.assertEqual(len(data.kws), 1)
        self.assertEqual(data.kws[0].name, 'KW 1')
        self.assertEqual(data.kws[0].doc, 'KW 1 doc')
        self.assertEqual(data.kws[0].args, '')

    def _assert_parsing_fails(self, data):
        self.assertRaises(InvalidXmlError, SuitData, self._create_input(data))

    def _create_input(self, data):
        return StringIO('<?xml version="1.0" encoding="UTF-8"?>\n' + data.strip())

if __name__ == '__main__':
    unittest.main()

