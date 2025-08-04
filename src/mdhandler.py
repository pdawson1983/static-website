import re
from textnode import TextNode, TextType


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
                break
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
                break
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
    
