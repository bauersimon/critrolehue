import argparse
import subprocess
import tempfile

import jinja2

from extractor import model

parser = argparse.ArgumentParser(
    prog="critrole_visualize",
    description="Visualize color information from Critical Role"
)
parser.add_argument("input",
                    type=str,
                    help="Path to the color update JSON file.")
parser.add_argument("-o", "--output",
                    type=str,
                    default="",
                    help="Path to the HTML output file.")
arguments = parser.parse_args()

TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
    <style>
        li,
        div {
            margin: 0.5em;
        }
        li {
            background-color: gainsboro;
            padding: 0.5em;
            cursor: pointer;
            border: 2px solid white;
        }
        ul {
            list-style-type: none;
        }
        span {
            margin-right: 1em;
        }
        .colorbox {
            background-color: black;
            padding: 1em;
            padding-left: 2em;
            padding-right: 2em;
            margin: 0em;
            margin-top: -0.1em;
            margin-bottom: -0.3em;
            display: inline-block;
        }
    </style>
    <div style="display: flex;">
        <div>
            <iframe id="iframe" width="853" height="505"
                src="{{ url }}?enablejsapi=1"></iframe>
        </div>
        <div>
            <ul>
                {% for update in updates %}
                <li onclick="seekTime({{ update._timestamp }})" id="time_{{ update._timestamp }}">
                    <span>{{ update.timestring }}</span>
                    {% for c in update._colors %}
                    <div class="colorbox" style="background-color: hsl({{c[0]*360}}, {{c[1]*100}}%, {{c[2]*100}}%);"></div>
                    {% endfor %}
                    <span></span>
                    {% for temp in update._temps %}
                    <span>temp: {{ temp|round(1) }}</span>
                    {% endfor %}
                </li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <script type="text/javascript">
        var timeToItems = [
            {% for update in updates %}
            [{{ update._timestamp }}, "time_{{ update._timestamp }}"],
            {% endfor %}
        ];

        var tag = document.createElement('script');
        tag.id = 'iframe-demo';
        tag.src = 'https://www.youtube.com/iframe_api';
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        var player;
        function onYouTubeIframeAPIReady() {
            player = new YT.Player('iframe', {
                events: {
                    'onReady': onPlayerReady,
                }
            });
        }
        function onPlayerReady(event) {
            setInterval(() => {
                highlightTime();
            }, 500);
        }
        function highlightTime() {
            var time = player.getCurrentTime();

            timeToItems.forEach((timestamp) => {
                document.getElementById(timestamp[1]).style.border = "2px solid white";
            });

            // Find the index that matches the current time.
            var reversedTimeToItems = timeToItems.toReversed();
            var idx = reversedTimeToItems.findIndex((timestamp) => {
                return timestamp[0] < time;
            });
            if (idx == -1) {
                return
            }

            document.getElementById(reversedTimeToItems[idx][1]).style.border = "2px solid black";
        }
        function seekTime(time) {
            player.seekTo(time, true);
            player.playVideo();
        }
    </script>
</body>
</html>
"""

with open(arguments.input, "r") as f:
    url, updates = model.from_json(f.read())
url = url.replace("watch?v=", "embed/")

environment = jinja2.Environment()
template = environment.from_string(TEMPLATE)
rendered = template.render({"url": url, "updates": updates})

if arguments.output == "":
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp:
        temp.write(rendered.encode("utf-8"))
        subprocess.run(["xdg-open", temp.name])
else:
    with open(arguments.output, "w") as f:
        f.write(rendered)
