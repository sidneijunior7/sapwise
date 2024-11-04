import streamlit as st
import openai
import time
# ===============================================================+
#           INICIO DO CÓDIGO                                    +
# ===============================================================+

# Configure sua chave de API da OpenAI
MY_API = st.secrets.openai.OPENAI_KEY
MY_ASSISTANT = st.secrets.openai.ASSISTANT_KEY
client = openai.OpenAI(
    api_key=MY_API,  # this is also the default, it can be omitted
)


def load_prompt():
    with open('include/prompt.md', 'r', encoding='utf-8') as file:
        return file.read()

def select_thread(thread_id):
    selected = client.beta.threads.retrieve(thread_id)
    return selected


def run_thread(assistant_id, thread_id):
    run = client.beta.threads.runs.create_and_poll(
        assistant_id=assistant_id,
        thread_id=thread_id
    )

    return run

def create_message(thread_id, content):
    _message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=content
    )
    return _message


def stream_response(response):
    for chunk in response:
        yield str(chunk)
        time.sleep(0.006)

sc1, sc2 = st.sidebar.columns([0.7, 0.3])
st.logo('images/logo.png')

thread = st.secrets.user_thread.thread

select = select_thread(thread)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Digite sua mensagem"):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):

        new_message = create_message(thread, prompt)

        new_run = run_thread(
            thread_id=thread,
            assistant_id=MY_ASSISTANT
        )

        if new_run.status == "completed":
            resposta = client.beta.threads.messages.list(thread).data[0].content[0].text.value
            # Adiciona a resposta completa ao histórico
            st.session_state.messages.append({"role": "assistant",
                                              "content": st.write_stream(stream_response(resposta))
                                              })