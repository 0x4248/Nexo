from html.parser import HTMLParser
import markdown

from . import logger

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
    logger.debug("XSSPreventionComponent", f"Sanitizing input: {input_string}")
    parser = SafeHTMLParser()
    parser.allowed_tags = {'b', 'i', 'u', 'a', 'br'}
    parser.feed(input_string)
    print("Sanitized input:", parser.get_sanitized())
    return parser.get_sanitized()

def sanitize_markdown_input(input_string: str) -> str:
    logger.debug("XSSPreventionComponent", f"Sanitizing markdown input: {input_string}")
    parser = SafeHTMLParser()
    parser.allowed_tags = {'b', 'i', 'u', 'a', 'br'}
    parser.feed(input_string)
    markdown_text = parser.get_sanitized()
    markdown_text = markdown.markdown(markdown_text)
    print("Sanitized markdown input:", parser.get_sanitized())
    return markdown_text

def sanitize_input_no_html(input_string: str) -> str:
    logger.debug("XSSPreventionComponent", f"Sanitizing input without HTML: {input_string}")
    parser = SafeHTMLParser()
    parser.allowed_tags = {}
    parser.feed(input_string)
    logger.debug("XSSPreventionComponent", f"Sanitized input without HTML: {parser.get_sanitized()}")
    return parser.get_sanitized()