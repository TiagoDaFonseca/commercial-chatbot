import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from chatbot import ChatBot
import openai

# initialize chatbot
bot =  ChatBot()


def send(role: str, msg: str) -> str:
    bot_message = st.chat_message(role)
    bot_message.write(msg)


def server():
    st.set_page_config(page_title="ChipChat", layout='wide')
    st.title('CMF commercial ChatBot')
    st.subheader('An LLM-powered app')
    colored_header('', description='Chat', color_name='blue-70')

    st.sidebar.header('Settings')
    api_key = st.sidebar.text_input('Insert here your openai access token', type="password")
    if api_key is not None:
        openai.api_key = api_key

    with st.sidebar:
        st.header('Parameters')

        model = st.selectbox('Model: ', options=['gpt-3.5-turbo-16k', 'gpt-3.5-turbo'])
        temperature = st.slider('Temperature: ', 0.0, 1.0, 0.0)
        max_tokens = st.selectbox('Max tokens: ', options=[100*i for i in range(10, 0, -1)])

        bot.set_params(model, temperature, max_tokens)

        add_vertical_space(3)
        st.markdown('''
        ## About
        This app is an LLM-powered chatbot built using:
        - [Streamlit](<https://streamlit.io/>)
        - [Openai](<https://platform.openai.com/docs/introduction/overview>)
        ''')

    response_container = st.container()
    input_container = st.container()

    if 'generated' not in st.session_state:
        try:
            st.session_state['generated'] = [bot.greetings()]
        except Exception as e:
            st.info(str(e))

    if 'generated' in st.session_state:
        # Applying the user input box
        with input_container:
            prompt = st.chat_input("Say something")

            if prompt:
                if 'past' not in st.session_state:
                    st.session_state['past'] = [prompt]
                else:
                    st.session_state.past.append(prompt)

                try:
                    generated_response = bot.get_response(prompt)
                    st.session_state.generated.append(generated_response)
                except openai.error.ServiceUnavailableError:
                    generated_response = 'Sorry, but it seems my knowledge is limited right now, try again later.'
                    st.session_state.generated.append(generated_response)
                    

        with response_container:
            send('assistant', st.session_state['generated'][0])
            if st.session_state['generated'] and (len(st.session_state['generated']) > 1):
                for i in range(len(st.session_state['past'])):
                    send('user', st.session_state['past'][i])
                    send('assistant', st.session_state['generated'][i+1])


if __name__ == '__main__':
    server()
