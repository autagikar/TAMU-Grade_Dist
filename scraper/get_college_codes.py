import urllib.request   # built-in Python library for making HTTP requests
from html.parser import HTMLParser  # built-in library for parsing HTML


# HTMLParser is a base class we extend to look for specific elements in the HTML
# We override handle_starttag, handle_endtag, and handle_data to extract what we need
class CollegeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_college_select = False  # tracks whether we're inside the college dropdown
        self.colleges = []              # stores (code, name) tuples we find
        self.current_value = None       # holds the value= attribute of the current <option>

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # Detect when we enter the college <select> dropdown element
        if tag == "select" and "college" in attrs.get("id", "").lower():
            self.in_college_select = True
        # Inside the dropdown, grab the value= attribute from each <option> tag
        if self.in_college_select and tag == "option":
            self.current_value = attrs.get("value", "")

    def handle_endtag(self, tag):
        # When the <select> closes, stop collecting options
        if tag == "select":
            self.in_college_select = False

    def handle_data(self, data):
        # The text between <option value="EN">ENGINEERING</option> is the college name
        if self.in_college_select and self.current_value is not None:
            label = data.strip()
            if label and self.current_value:
                self.colleges.append((self.current_value, label))
            self.current_value = None


# Fetch the grade reports page HTML
url = "https://web-as.tamu.edu/gradereports/"
with urllib.request.urlopen(url) as response:
    html = response.read().decode("utf-8")

# Parse the HTML and print all college codes found
parser = CollegeParser()
parser.feed(html)

print("College codes found:")
for code, name in parser.colleges:
    print(f"  {code:10} {name}")
