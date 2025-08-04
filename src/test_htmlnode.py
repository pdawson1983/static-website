import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

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
    
    def test_leaf_node(self):
        leaf = LeafNode(tag='b', value="This is leaf")
        self.assertEqual(
            repr(leaf),
            "HTMLNode(b, This is leaf, None, None)"
        )
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(
            node.to_html(),
            "<p>Hello, world!</p>"
        )

    def test_render_leaf_node_with_tag(self):
        leaf = LeafNode(tag='b', value="This is leaf")
        self.assertEqual(
            leaf.to_html(),
            '<b>This is leaf</b>'
        )
    
    def test_render_leaf_node_with_no_tag(self):
        leaf = LeafNode(value="This is leaf with no tag")
        self.assertEqual(
            leaf.to_html(),
            'This is leaf with no tag'
        )

    def test_value_error_of_bold_leafnode(self):
        with self.assertRaises(ValueError):
            leaf = LeafNode(tag='b')
    
    def test_no_value_error_of_img_leafnode(self):
        leaf = LeafNode(tag='img', props={'src': 'static/image.jpg', 'alt': 'This is an image node'})
        self.assertIsNotNone(leaf)
    
    def test_leaf_node_with_props(self):
        leaf = LeafNode(tag='a', value="This is leaf", props={'href':'https://www.google.com','target':'_blank' })
        self.assertEqual(
            leaf.to_html(),
            '<a href="https://www.google.com" target="_blank">This is leaf</a>'
        )
    
    def test_to_html_with_single_leaf_child(self):
        child_node = LeafNode('b', "Child")
        parent_node = ParentNode("div", children=[child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><b>Child</b></div>"
        )
    
    def test_to_html_with_multiple_simple_leaf_children(self):
        child1_node = LeafNode('b', "Child1")
        child2_node = LeafNode(None, "Child2")
        parent_node = ParentNode("div", children=[child1_node,child2_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><b>Child1</b>Child2</div>"
        )

    def test_to_html_with_multiple_complex_leaf_children(self):
        child1_node = LeafNode('a', "Child1", props={'href':'https://www.google.com','target':'_blank' } )
        child2_node = LeafNode('a', "Child2", props={'href':'https://www.google.com','target':'_blank' })
        parent_node = ParentNode("div", children=[child1_node,child2_node])
        self.assertEqual(
            parent_node.to_html(),
            '<div><a href="https://www.google.com" target="_blank">Child1</a><a href="https://www.google.com" target="_blank">Child2</a></div>'
        )
    

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

if __name__ == "__main__":
    unittest.main()