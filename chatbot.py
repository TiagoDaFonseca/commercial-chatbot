import os
import openai
from dotenv import load_dotenv, find_dotenv
import json
from requests_html import HTMLSession
import utils

_ = load_dotenv(find_dotenv())  # read local env
# Set Openai API key
openai.api_key = os.environ['OPENAI_API_KEY']


class MessageBuffer:

    def __init__(self, size=100):
        """
        Message Buffer to limit the number of prompts saved in memory.
        Initializes size.
        Returns: MessageBuffer Object
        """
        self.size = size
        self.messages = []

    def add(self, item):
        if len(self.messages) < self.size:
            self.messages.append(item)
        else:
            self.messages.pop(0)
            self.messages.append(item)

    def clean(self):
        self.messages = []


class ChatBot(object):
    def __init__(self,
                 name='ChipChat',
                 model='gpt-3.5-turbo-16k',
                 temperature=0,
                 max_tokens=500,
                 buffer_size=10):
        self.name = name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = MessageBuffer(size=buffer_size)
        self.knowledge_base = []
        self.system = """You are a Business representative for industry 4.0 and you work for Critical Manufacturing which is the \
                        best company in the world! Your are specialized in Manufacturing Execution systems applied to \
                        semiconductor and electronics assembly industry. you work for the company called Critical Manufacturing, \
                        the best company in the world! You will provide information regarding semiconductor, \
                        medical devices and surface-mount technology sectors, describing how a manufacturing execution system (i.e MES) \
                        can improve improve their operations.\
                        You only answer to questions that relate with the company business. \
                        If the question is not related with Critical manufacturing, semiconductor industry, \
                        electronics assembly industry or medical devices industry, just respond with this sentence \
                        between ###, i.e. ###Sorry, my knowledge is limited.### \
                        Never answer questions related with weather! \
                        For instance, if asked for the weather just answer: 'Sorry pal, my knowledge is limited'
                        Your name is ChipChat. Your are funny and polite and very enthusiastic! \
                        Every time you are asked for future events, complement the answer by inviting them to join us!
                        """

        self._get_links_list('https://www.criticalmanufacturing.com')

    def _get_links_list(self, url: str):
        self.knowledge_base = HTMLSession().get(url).html.links

    def set_params(self, model, temp, tokens):
        self.model = model
        self.temperature = temp
        self.max_tokens = tokens

    def get_completion_from(self, messages):
        """
        Openai chat completion request
        returns: string
        """
        response = openai.ChatCompletion.create(model=self.model, messages=messages, temperature=self.temperature,
                                                max_tokens=self.max_tokens)
        return response.choices[0].message['content']

    def greetings(self):
        """
        Say hello and introduces himself
        return: string
        """
        self.history.add({'role': 'system', 'content': self.system})
        self.history.add({'role': 'user', 'content': 'Present yourself'})

        # chat completion request
        response = self.get_completion_from(self.history.messages)
        # add response to messages history
        self.history.add({'role': 'assistant', 'content': response})
        return response

    def extract_topic(self, prompt: str) -> (bool, str, str):
        system_message = {'role': 'system', 'content': f' extract the 3 most common topics maximum in json format that \
                                                        are present in the user query, from the following:\
                                                        weather, job openings, product functionalities, who we are, leadership, \
                                                        research, customers, services, news, events, gartner, industries, \
                                                        contact, goodbye. if no topic exists return as other \
                                                        For instance, topics=[boda]'}

        messages = [system_message, {'role': 'user', 'content': prompt}]
        response = self.get_completion_from(messages)
        return response

    def get_response_from(self, topic: str, question: str) -> str:
        messages = []
        if topic == 'news':
            links = [link for link in list(self.knowledge_base) if (topic in link) or ('press' in link)]
        elif topic == 'job-openings':
            links = ['https://careers.criticalmanufacturing.com/', 'https://careers.criticalmanufacturing.com/#jobs']
        else:
            links = [link for link in list(self.knowledge_base) if topic in link]
        context = '\n'.join([utils.scrape_info_from(link) for link in links])
        if len(context) > 60000:
            context = context[:60000]
        query = f""" Use the text below about Critical Manufacturing to answer the subsequent question. \ 
                    If the answer cannot be found, write "sorry friend, I don't know"

                    Text:
                    \"\"\"
                    {context}
                    \"\"\"

                    Question: {question}
                    """
        messages += self.history.messages
        messages.append({'role': 'user', 'content': query})
        return self.get_completion_from(messages)

    def get_response(self, prompt: str):
        # add user prompt to chat history
        self.history.add({'role': 'user', 'content': prompt})

        # Extract the most relevant topic
        res = self.extract_topic(prompt)
        try:
            topic = json.loads(res)['topics'][0]
        except json.decoder.JSONDecodeError:
            topic = 'other'

        # find appropriate info for each topic
        match topic:
            case 'who we are':
                response = self.get_response_from(topic.replace(' ', '-'), prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'job openings':
                response = self.get_response_from(topic.replace(' ', '-'), prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'product functionalities':
                response = self.get_response_from('mes-for-industry-4-0', prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'leadership':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'research':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'customers':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'services':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'news':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'events':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'gartner':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'industries':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'contact':
                response = self.get_response_from(topic, prompt)
                self.history.add({'role': 'assistant', 'content': response})
            case 'weather':
                is_city, city = utils.get_city(prompt)
                if is_city:
                    response = f'Sure, why not? {city}? I know this city! '
                    result = utils.get_weather(city)
                    response += f"Looks like the weather in {city} is {result['current']['condition']['text'].lower()} with {result['current']['temp_c']} Celsius. "
                    if (city.lower() == 'maia') and (result['current']['condition']['text'].lower() == 'sunny'):
                        response += 'You should join us for a drink in our offices!'
                    self.history.add({'role': 'assistant', 'content': response})
                else:
                    result = utils.get_weather('Maia')
                    response = f"Sure! Well in Maia the weather is {result['current']['condition']['text'].lower()} \
                                with {result['current']['temp_c']}C. "
                    if result['current']['condition']['text'].lower() == 'sunny':
                        response += 'If you mean other city, you can try be more specific or... \
                                    you could join us for a drink in our offices!'
                    self.history.add({'role': 'assistant', 'content': response})
            case _:
                response = self.get_completion_from(self.history.messages)
                self.history.add({'role': 'assistant', 'content': response})

        return response.replace('#', '').strip()

    def run(self):
        pass



