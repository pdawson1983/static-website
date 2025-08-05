
class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        text_str =''
        for key in self.props.keys():
            text_str += f'{key}="{self.props[key]}" '
        return text_str.strip()
    
    def __repr__(self):
        return f'HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})'

class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, children=None, props=None):
        super().__init__(tag, value, None, props)
        if self.value == None and self.tag not in ['img', 'br']:
            raise(ValueError)

    def to_html(self):
        if self.tag in ['img', 'br']:  # Self-closing tags
            return f'<{self.tag}{" " + self.props_to_html() if self.props else ""} />'
        elif self.tag:
            return f'<{self.tag}{" " + self.props_to_html() if self.props else ""}>{self.value}</{self.tag}>'
        return self.value
    
    def __repr__(self):
        return f'LeafNode({self.tag}, {self.value}, {self.props})'
    
class ParentNode(HTMLNode):
    def __init__(self, tag=None, children=None, props=None):
        super().__init__(tag, None, children, props)
    
    def to_html(self):
        if self.tag == None:
            raise ValueError("tag value cannot be None")
        if self.children == None:
            raise ValueError("parent must have a child node and cannot equal None")
        return f'<{self.tag}{" " + self.props_to_html() if self.props else ""}>{"".join([child.to_html() for child in self.children])}</{self.tag}>'
    
    def __repr__(self):
        return f'ParentNode({self.tag}, {self.children}, {self.props})'