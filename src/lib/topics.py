
import json

def get_topics():
    with open("data/topics.json", "r") as f:
        data = json.load(f)
        return data
def set_topics(topics):
    with open("data/topics.json", "w") as f:
        json.dump(topics, f, indent=4)
        
def add_topic(topic):
    topics = get_topics()
    if topic not in topics:
        topics.append(topic)
        set_topics(topics)
        return True
    return False