from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import feedparser
import calendar
from datetime import datetime
import wikipedia

app = Flask(__name__)
CORS(app)

tasks = []

def get_news():
    rss_feeds = [
        'https://feeds.feedburner.com/ndtvnews-india-news',
        'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
        'https://www.thehindu.com/news/national/21582500/0.rss'
    ]
    all_articles = []
    for url in rss_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entry['source'] = url.split('/')[2]  # Add source from URL
            all_articles.append(entry)
    # Sort by published date if available
    all_articles = sorted(all_articles, key=lambda x: x.get('published_parsed', datetime.now()), reverse=True)
    return all_articles[:10]

def options_menu():
    return ("Task options:\n"
            "1. Add task - 'add' 📝\n"
            "2. View tasks - 'view' 👀\n"
            "3. Edit task - 'edit' ✏️\n"
            "4. Remove task - 'remove' ❌\n"
            "Example:\n"
            "- To add: task add homework 📝\n"
            "- To view: task view 👀\n"
            "- To edit: task edit 2 new task description ✏️\n"
            "- To remove: task remove 1 ❌")

def get_bot_response(message):
    msg = message.lower().strip()

    try:
        if msg in ["hi", "hello", "hey", "hy"]:
            return "👋 Hello! I am InfoBot — your virtual assistant. How can I assist you today?"
            
        elif "what can you do" in msg or "help" in msg:
            return ("I can do the following 🤖:<br><br>"
                    "- Provide the latest news 📰 ('news')<br>"
                    "- Show the calendar 📅 ('calendar')<br>"
                    "- Manage tasks (add, view, edit, remove) 📝<br>"
                    "- Fetch information from Wikipedia 📚 (just type the topic)")

        elif "who are you" in msg:
            return "I am InfoBot — a smart assistant who helps you with daily tasks and provides information! 😊"
            
        elif msg == "news":
            articles = get_news()
            if articles:
                news_message = "Top 10 Latest News 📰:<br><br>"
                for a in articles:
                    source = a.get('source', 'Unknown')
                    news_message += f"• <a href='{a.link}' target='_blank'>{a.title}</a> ({source})<br><br>"
                return news_message
            else:
                return "Sorry, no news found 😔."

        elif msg == "calendar":
            today = datetime.today().strftime('%d-%m-%Y')
            day = calendar.day_name[datetime.today().weekday()]
            return f"Today's date: {today} ({day}) 📅"

        elif msg == "task":
            return options_menu().replace("\n", "<br>")

        elif msg.startswith("task add"):
            task = msg.replace("task add", "").strip()
            if not task:
                return "Please specify the task name 📝."
            tasks.append(task)
            return f"Task added: {task} ✅"

        elif msg == "task view":
            if not tasks:
                return "No tasks available 🕒."
            return "Your tasks 👇:<br>" + "<br>".join([f"{i+1}. {t}" for i, t in enumerate(tasks)])

        elif msg.startswith("task edit"):
            parts = msg.split()
            if len(parts) < 4:
                return "Incorrect format 😕. Example: task edit 2 new task description ✏️"
            try:
                index = int(parts[2]) - 1
                new_task = " ".join(parts[3:])
                if index < 0 or index >= len(tasks):
                    return "Incorrect task number ❌."
                old_task = tasks[index]
                tasks[index] = new_task
                return f"Task edited ✏️:<br>Old: {old_task}<br>New: {new_task}"
            except ValueError:
                return "Invalid task number ❌."

        elif msg.startswith("task remove"):
            try:
                index = int(msg.replace("task remove", "").strip()) - 1
                if index < 0 or index >= len(tasks):
                    return "Incorrect task number ❌."
                removed = tasks.pop(index)
                return f"Task removed: {removed} ❌"
            except ValueError:
                return "Incorrect number format. Example: task remove 1 ❌"
        
        # Add the "bye" functionality
        elif msg in ["bye", "goodbye", "see you", "bye bye"]:
            return "👋 Goodbye! Have a great day ahead! 😊"

        else:
            try:
                summary = wikipedia.summary(msg, sentences=3)
                return summary.replace("\n", "<br>")
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Topic unclear. Here are some options:<br><br>{'<br>'.join(e.options[:5])} 🔍"
            except wikipedia.exceptions.PageError:
                return "No results found 😕. Is the topic written correctly? ❓"
            except Exception as e:
                return f"Something went wrong: {str(e)} ❌"

    except Exception as e:
        return f"Error: {str(e)} ❌"

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data['message']
        reply = get_bot_response(user_msg)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)} ❌"})

if __name__ == '__main__':
    app.run(debug=True)