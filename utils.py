import csv
from datetime import datetime
import os
import pandas as pd
import streamlit as st
import langchain as lc

from typing import List, Dict

DATA_PATH = 'data'

def setup():
    if not os.path.isdir("data"):
        os.mkdir("data")
    if not os.path.isdir("Files"):
        os.mkdir("Files")

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def del_old_chat():
    if "ChatBot" in st.session_state: del st.session_state["ChatBot"]
    if "Conversation" in st.session_state: del st.session_state["Conversation"]
    if "Memory" in st.session_state: del st.session_state["Memory"]

def setup_new_chat_memory(coversation_title):
    st.session_state["Conversation"] = Conversation(coversation_title)
    st.session_state["Memory"] = lc.memory.ConversationBufferMemory()
    if st.session_state["Conversation"].context:      # Load previous conversation into memory (if a previous conversation)
        for input, output in st.session_state["Conversation"].context:
            st.session_state["Memory"].save_context(input, output)

def get_conversation_list():
    items = ['New conversation'] + [conv[:-4] for conv in sorted(os.listdir(DATA_PATH), reverse=True)]
    if 'usage' in items: items.remove('usage')
    return items

class UsageLogger:
    _fieldnames = ['time', 'cost']

    def __init__(self):
        self._file_exists = os.path.exists(os.path.join(DATA_PATH, 'usage.csv'))
        if not self._file_exists:
            self._create_file()
        self.prev_cost = 0.0

    def _create_file(self):
        with open(os.path.join(DATA_PATH, 'usage.csv'), 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            writer.writeheader()
        self._file_exists = True

    def append(self, cb):
        time = get_time()
        with open(os.path.join(DATA_PATH, 'usage.csv'), 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            writer.writerow({'time': time, 'cost': cb.total_cost})
        self.prev_cost = cb.total_cost

    def get_day(self):
        df = self.get_all_usage()
        date_from = pd.Timestamp.today().normalize()
        return df[df['time'] > date_from]

    def get_week(self):
        df = self.get_all_usage()
        date_from = pd.Timestamp.today().to_period('W').to_timestamp()
        return df[df['time'] > date_from]
    
    def get_month(self):
        df = self.get_all_usage()
        date_from = pd.Timestamp.today().to_period('M').to_timestamp()
        return df[df['time'] > date_from]
    
    def get_all_usage(self):
        """
            Reloads usage
        """
        df = pd.read_csv(os.path.join(DATA_PATH, 'usage.csv'))
        df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H-%M-%S")
        return df

    def month_total(self):
        """
            Returns the total cost for the current month
        """
        return self.get_month().cost.sum()

    def day_total(self):
        """
            Returns the total cost for the current day
        """
        return self.get_day().cost.sum()
    
    def avg_query_cost(self):
        df = self.get_all_usage()
        return df.cost.mean()
    
    def number_of_entries(self):
        df = self.get_all_usage()
        return len(df)


class Conversation:
    _fieldnames = ['role', 'content']

    def __init__(self, conversation_name):
        self.conversation_name = conversation_name
        self._messages = self.read()
        if self.conversation_name == "New conversation":
            self.conversation_name = get_time()
        self._started = False
    
    @property
    def messages(self) -> List[Dict[str, str]]:
        return self._messages
    
    @property
    def context(self) -> List[Dict[str, str]]:
        """
            Gives messages in context format
        """
        for input, output in zip(self._messages[0:2:-1], self.messages[1:2:-1]):
            assert input['role'] == 'User'
            assert output['role'] == 'Assistant'
            yield {'User': input['content']}, {'Assistant': output['content']}

    def read(self):
        """
        Returns a list of messages in the conversation. If the conversation is new, returns an empty list.
        """
        if self.conversation_name == 'New conversation':
            return []
        with open(os.path.join(DATA_PATH, self.conversation_name+'.csv'), 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
        
    def start(self):
        """
        Creates a new conversation file if the conversation is new. Does nothing if the conversation already exists.
        """
        if self._messages == []:
            with open(os.path.join(DATA_PATH, self.conversation_name+'.csv'), 'w') as f:
                writer = csv.DictWriter(f, fieldnames=self._fieldnames)
                writer.writeheader()
        self._started = True

    @property
    def started(self):
        return self._started

    def append(self, message: Dict[str, str]):
        """
        Appends a message to the conversation.
        """
        self.start()  # In case the conversation is new
        self._messages.append(message)
        with open(os.path.join(DATA_PATH, self.conversation_name+'.csv'), 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            writer.writerow(message)