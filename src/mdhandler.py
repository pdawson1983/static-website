import re
from enum import Enum
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, LeafNode, ParentNode

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
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '*', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE)
    return nodes
    
def markdown_to_blocks(markdown):
    blocks = []
    for block in markdown.split('\n\n'):
        if not block:
            continue
        blocks.append(block.strip())
    #breakpoint()
    return blocks

def block_to_block_type(block):
    lines = block.split("\n")
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
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if re.match(r'^-\s', block):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    if re.match(r'^1\.\s', block):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH

def code_block_to_html_node(block):
    code_content = re.sub(r'^```.*?\n', '', block)  
    code_content = re.sub(r'(\n)```$', r'\1', code_content)  
    code_node = TextNode(code_content, TextType.CODE)
    return ParentNode('pre',[text_node_to_html_node(code_node)])

def quote_block_to_html_node(block):
    code_content = re.sub(r'(^|\n)>', r'\1',block)
    quote_textnodes = text_to_textnodes(code_content)
    html_nodes = []
    for node in quote_textnodes:
        html_nodes.append(text_node_to_html_node(node))
    return ParentNode(BlockType.QUOTE.value, html_nodes)

def paragraph_to_html_node(block):
    lines = block.split('\n')
    html_nodes = []
    
    for i, line in enumerate(lines):
        if line.strip():  
            text_nodes = text_to_textnodes(line)
            for node in text_nodes:
                html_nodes.append(text_node_to_html_node(node))
        

        if i < len(lines) - 1:
            html_nodes.append(LeafNode('br'))  
    
    return ParentNode(BlockType.PARAGRAPH.value, html_nodes)

def unordered_list_to_html_node(block):
    lines = re.findall(r'^- (.+)$', block, re.MULTILINE)
    html_nodes = []
    for line in lines:
        html_nodes.append(LeafNode('li', line))
    return ParentNode(BlockType.UNORDERED_LIST.value, html_nodes)

def ordered_list_to_html_node(block):
    lines = re.findall(r'^\d\. (.+)$', block, re.MULTILINE)
    html_nodes = []
    for line in lines:
        html_nodes.append(LeafNode('li', line))
    return ParentNode(BlockType.ORDERED_LIST.value, html_nodes)

def headings_to_html_node(block):
    lines = re.findall(r'^(#+)\s(.+)$', block, re.MULTILINE)
    html_nodes = []
    for h, value in lines:
        text_nodes = text_to_textnodes(value)
        sub_nodes = []
        for node in text_nodes:
            sub_nodes.append(text_node_to_html_node(node))
        if len(sub_nodes) > 1:
            html_nodes.append(ParentNode(f'h{len(h)}', sub_nodes))
        elif len(sub_nodes) == 1 and text_nodes[0].text_type != 'TEXT':
            html_nodes.append(ParentNode(f'h{len(h)}', sub_nodes))
        else:
            html_nodes.append(LeafNode(f'h{len(h)}', value))
    
    return html_nodes
        



def markdown_to_html_node(markdown):
    HEADING_TYPES = {BlockType.HEADING_1, BlockType.HEADING_2, BlockType.HEADING_3, 
                 BlockType.HEADING_4, BlockType.HEADING_5, BlockType.HEADING_6}
    blocks = markdown_to_blocks(markdown)
    child_nodes=[]
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.CODE:
            node = code_block_to_html_node(block)
            child_nodes.append(node)
        elif block_type == BlockType.QUOTE:
            child_nodes.append(quote_block_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            child_nodes.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            child_nodes.append(ordered_list_to_html_node(block))
        elif block_type in HEADING_TYPES:
            child_nodes.extend(headings_to_html_node(block))
        else:
            if block_type == BlockType.PARAGRAPH:
                child_nodes.append(paragraph_to_html_node(block))
            else:
                text_nodes = text_to_textnodes(block)
                html_nodes = []
                for node in text_nodes:
                    html_nodes.append(text_node_to_html_node(node))
                child_nodes.append(ParentNode(block_type.value, html_nodes))

    return ParentNode('div', child_nodes)
    
        
    
            
            



        
