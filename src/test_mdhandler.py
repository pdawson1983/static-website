import unittest

from mdhandler import split_nodes_delimiter, \
    extract_markdown_images, extract_markdown_links, \
        split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType

class TestMdHandler(unittest.TestCase):
    def test_inline_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '`', TextType.CODE)
        self.assertEqual(
            new_nodes, 
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word",TextType.TEXT)
            ]
        )
    
    def test_inline_markdown_at_start(self):
        node = TextNode("`code block` This is text starting with a code block", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '`', TextType.CODE)
        self.assertEqual(
            new_nodes, 
            [
                TextNode("code block", TextType.CODE),
                TextNode(" This is text starting with a code block", TextType.TEXT),
            ]
        )
    
    def test_inline_markdown(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '**', TextType.BOLD)
        self.assertEqual(
            new_nodes, 
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word",TextType.TEXT)
            ]
        )
    
    def test_two_inline_markdown_words(self):
        node = TextNode("This is **some** text with a **bold** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], '**', TextType.BOLD)
        self.assertEqual(
            new_nodes, 
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("some", TextType.BOLD),
                TextNode(" text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word",TextType.TEXT)
            ]
        )
    
    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertEqual(
            matches,
            [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        )
    
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertEqual(
            matches,
            [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        )

    def test_split_single_image_nodes(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")
            ]
        )
    
    def test_split_multiple_image_nodes(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image",
                    TextType.IMAGE,
                    "https://i.imgur.com/3elNhQu.png")
            ]
        )
    
    def test_split_single_link_nodes(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com")
            ]
        )
    
    def test_split_multiple_link_nodes(self):
        node = TextNode(
            "This is text with a [link](https://www.google.com) and another [second link](https://bing.com)",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link",
                    TextType.LINK,
                    "https://bing.com")
            ]
        )
    
    def test_text_to_textnodes(self):
        text = (
            "This is **text** with an _italic_ word and a `code block`"
            " and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg)" 
            " and a [link](https://boot.dev)"
        )
        nodes = text_to_textnodes(text)
        self.assertEqual(
            nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ]
        )
    
    def test_text_to_textnodes_empty_string(self):
        nodes = text_to_textnodes("")
        self.assertEqual(nodes, [])
    
    def test_text_to_textnodes_whitespace_only(self):
        nodes = text_to_textnodes("   ")
        self.assertEqual(nodes, [TextNode("   ", TextType.TEXT)])

    def test_text_to_textnodes_adjacent_formatting(self):
        text = "**bold**_italic_`code`"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes, [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE)
        ])

    def test_text_to_textnodes_unclosed_bold(self):
        text = "This has **unclosed bold text"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_text_to_textnodes_unclosed_italic(self):
        text = "This has _unclosed italic text"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_text_to_textnodes_unclosed_code(self):
        text = "This has `unclosed code text"
        with self.assertRaises(ValueError):
            text_to_textnodes(text)

    def test_text_to_textnodes_image_at_start(self):
        text = "![start image](https://example.com) followed by text"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[0].text_type, TextType.IMAGE)

    def test_text_to_textnodes_link_at_end(self):
        text = "Text ending with [a link](https://example.com)"
        nodes = text_to_textnodes(text)
        self.assertEqual(nodes[-1].text_type, TextType.LINK)
    
    def test_markdown_to_blocks(self):
        pass
        # TODO Create markdown_to_blocks tests

if __name__ == "__main__":
    unittest.main()