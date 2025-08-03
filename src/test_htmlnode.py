import unittest

from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_empty_node(self):
        node = HTMLNode()
        self.assertEqual(
            repr(node),
            'HTMLNode(None, None, None, None)'
        )
    
    def test_child_node(self):
        child_node = HTMLNode(tag='a',value="link",props={'href':'https://www.google.com'})
        parent_node = HTMLNode(tag='p',children=child_node)
        self.assertEqual(
            repr(parent_node),
            "HTMLNode(p, None, HTMLNode(a, link, None, {'href': 'https://www.google.com'}), None)"
        )
    
    def test_no_tag(self):
        node = HTMLNode(value='This is just text')
        self.assertEqual(
            repr(node),
            "HTMLNode(None, This is just text, None, None)"
        )
    
    

if __name__ == "__main__":
    unittest.main()