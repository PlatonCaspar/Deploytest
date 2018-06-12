import unittest
import search


class TestSearchMethods(unittest.TestCase):
    
    def test_check_property(self):
        value = "PartType:Resistor"#; case:0402;Project:Gridlink"
        search_word = "PartType:Resistor"
        score = search.check_property(search_word, value)
        # print(score)
        assert score is 1
        value = "PartType:Res"#;case:0402;Project:Gridlink"
        search_word = "PartType:Resistor"
        score = search.check_property(search_word, value)
        assert score is 0
        value = "Patch:1,5,6,3"#;Project:Gridlink"
        search_word = "Patch:1,3,5"
        score = search.check_property(search_word, value)
        print(score)
        assert score is 3

    def test_value_search(self):
        value = "platos;ist;eine;Webapp;zur;Verwaltung;von;Bauteilen;und;Prototypen;"
        search_word = "platos ist eine zur"
        score = search.value_search(search_word, value)
        assert score is 7
        value = "platos;ist;eine;Webapp;zur;Verwaltung;von;Bauteilen;und;Prototypen;"
        search_word = "Verwaltung von bauteilen Prototypen und"
        score = search.value_search(search_word, value)
        assert score is 8
        value = "platos;ist;eine;Webapp;zur;Verwaltung;von;Bauteilen;und;Prototypen;"
        search_word = "Verwaltung&Bauteile&Stefan"
        score = search.value_search(search_word, value)
        assert score is 0
        value = "platos;ist;eine;Webapp;zur;Verwaltung;von;Bauteilen;und;Prototypen:5;"
        search_word = "  Verwaltung von bauteilen Prototypen und &Prototypen:5"
        score = search.value_search(search_word, value)
        assert score is 19


if __name__ == '__main__':
    unittest.main()

