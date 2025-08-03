from textnode import TextNode, TextType

def main():
    testNode = TextNode('This is some anchor text', 'link', 'https://www.boot.dev')
    print(testNode)

if __name__ == '__main__':
    main()