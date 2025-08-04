import re
from enum import Enum
from textnode import TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = 'p'
    HEADING_1 = 'h1'
    HEADING_2 = 'h2'
    HEADING_3 = 'h3'
    HEADING_4 = 'h4'
    HEADING_5 = 'h5'
    HEADING_6 = 'h6'
    CODE = 'code'
    QUOTE = 'blockquote'
    UNORDERED_LIST = 'ul'
    ORDERED_LIST = 'ol'



def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown, formatted section not closed")
        
        for i, part in enumerate(parts):
            if i % 2 ==0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r'\!\[(.+?)\]\((.+?)\)', text)                    
    return matches

def extract_markdown_links(text):
    matches = re.findall(r'\[(.+?)\]\((.+?)\)', text)                    
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        matches = extract_markdown_images(node.text)
        parts = re.split(r'(\!\[.+?\]\(.+?\))', node.text)
        for part in parts:
            if not part:
                continue
            if part.startswith('!['):
                text, url = matches.pop(0)
                new_nodes.append(TextNode(str(text),TextType.IMAGE, str(url)))
            else:
                new_nodes.append(TextNode(part, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        matches = extract_markdown_links(node.text)
        parts = re.split(r'(\[.+?\]\(.+?\))', node.text)
        for part in parts:
            if not part:
                continue
            if part.startswith('['):
                text, url = matches.pop(0)
                new_nodes.append(TextNode(str(text),TextType.LINK, str(url)))
            else:
                new_nodes.append(TextNode(part, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '*', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
    
def markdown_to_blocks(markdown):
    blocks = []
    for block in markdown.split('\n\n'):
        if not block:
            continue
        blocks.append(block.strip())
    
    return blocks

def block_to_block_type(block):
    if re.match(r'^#{1}\s', block):
        return BlockType.HEADING_1
    if re.match(r'^#{2}\s', block):
        return BlockType.HEADING_2
    if re.match(r'^#{3}\s', block):
        return BlockType.HEADING_3
    if re.match(r'^#{4}\s', block):
        return BlockType.HEADING_4
    if re.match(r'^#{5}\s', block):
        return BlockType.HEADING_5
    if re.match(r'^#{6}\s', block):
        return BlockType.HEADING_6
    if re.match(r'\A`{3}', block) and re.search(r'`{3}\Z', block):
        return BlockType.CODE
    if re.match(r'^>\S', block):
        return BlockType.QUOTE
    if re.match(r'^-\s', block):
        return BlockType.UNORDERED_LIST
    if re.match(r'^1\.\s', block):
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH