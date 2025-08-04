from enum import Enum
from htmlnode import LeafNode, ParentNode

class TextType(Enum):
    TEXT = ''
    BOLD = 'b'
    ITALIC = 'i'
    CODE = 'code'
    LINK = 'a'
    IMAGE = 'img'


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = TextType(text_type)
        self.url = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f'TextNode({self.text}, {self.text_type.value}, {self.url})'
    
def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(value=text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode(tag=text_node.text_type.value, value=text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode(tag=text_node.text_type.value, value=text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode(tag=text_node.text_type.value, value=text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode(tag=text_node.text_type.value, value=text_node.text, props={'href':text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode(tag=text_node.text_type.value, props={'src':text_node.url,'alt':text_node.text})
    else:
        raise ValueError("text_type must be valid type")