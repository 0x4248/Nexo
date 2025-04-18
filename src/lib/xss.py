from html.parser import HTMLParser

class SafeHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.allowed_tags = {}

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            if tag == "a":
                href = dict(attrs).get("href", "")
                self.result.append(f'<a href="{href}">')
            else:
                self.result.append(f'<{tag}>')

    def handle_endtag(self, tag):
        if tag in self.allowed_tags:
            self.result.append(f'</{tag}>')

    def handle_startendtag(self, tag, attrs):
        if tag in self.allowed_tags:
            self.result.append(f'<{tag} />')

    def handle_data(self, data):
        self.result.append(data)

    def get_sanitized(self):
        return ''.join(self.result)


def sanitize_input(input_string: str) -> str:
    print("Sanitizing input:", input_string)
    parser = SafeHTMLParser()
    parser.allowed_tags = {'b', 'i', 'u', 'a', 'br'}
    parser.feed(input_string)
    print("Sanitized input:", parser.get_sanitized())
    return parser.get_sanitized()

def sanitize_input_no_html(input_string: str) -> str:
    print("Sanitizing input:", input_string)
    parser = SafeHTMLParser()
    parser.allowed_tags = {}
    parser.feed(input_string)
    print("Sanitized input:", parser.get_sanitized())
    return parser.get_sanitized()