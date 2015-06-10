from flask import Flask, render_template, request
import grammar
import os

app = Flask(__name__)

from io import StringIO
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

@app.route('/')
def hello_world():
    input = request.args.get('input',grammar.example)
    to_parse = request.args.get('to_parse',"a+a∗a")
    G = grammar.Grammar.from_text(input)
    with Capturing() as output:
        try:
            G.stats()
            G.parse(to_parse)
        except Exception as e:
            print(e)
    return render_template('index.html', input=input,
            to_parse=to_parse, output='\n'.join(output))

if __name__ == '__main__':
    app.run(port=8080, debug=os.getenv("PROD") == None)