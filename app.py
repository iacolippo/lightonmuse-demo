import os

import streamlit as st
import lightonmuse


st.set_page_config(page_title="Lighton Muse interactive demo")


@st.cache
def get_muse_client():

    creator = lightonmuse.Create("orion-fr")
    return creator


def app_title():

    col1, mid, col2 = st.columns([4, 1, 30])
    with col1:
        st.image(
            "https://camo.githubusercontent.com/39e9d21c0216ddc6856ff4769bd0e53e64d672a90f6c36654ef447dee274d696/68747470733a2f2f636c6f75642e6c696768746f6e2e61692f77702d636f6e74656e742f75706c6f6164732f323032302f30312f4c696768744f6e436c6f75642e706e67",
            width=90
        )
    with col2:
        st.title("\t\t\tLighton Muse")


def create_word_biases(params, forbidden_words, encourage_words):

    biases = {}

    if forbidden_words:
        for bias in forbidden_words.split(";"):
            # effectively forbid word
            biases[bias] = -100

    if encourage_words:
        for bias in encourage_words.split(";"):
            # fine-tuned value that works nicely in
            # combination with penalties
            biases[bias] = 4.5

    if len(biases) > 0:

        params["word_biases"] = biases


def format_stop_word(params, stop_words):

    # build the stop_words list
    if stop_words:
        stop_words_list = list()
        for word in stop_words.split(";"):
            stop_words_list.append(word)

        params["stop_words"] = stop_words_list
    else:
        params['stop_words'] = None


def generate_prompt(prompt, n_token, mode, temperature, p, k, best_of, presence_penalty, frequency_penalty,
                    encourage_words, forbidden_words):

    if prompt == "":
        return prompt

    n_completions = best_of if best_of > 1 else 1

    params = {
        "n_tokens": n_token,
        "mode": mode,
        "temperature": temperature,
        "p": p,
        "k": k,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "best_of": best_of,
        "n_completions": n_completions,
        "seed": 42  # clearly the best seed
    }

    # add the biases and stop words if they have been provided
    create_word_biases(params, forbidden_words, encourage_words)
    format_stop_word(params, stop_words)

    # call Create

    muse_client = get_muse_client()

    info = st.empty()
    try:
        info.write("Please wait...")
        outputs, cost, rid = muse_client(text=prompt, **params)
        prompt_completion = outputs[0]["completions"][0]['output_text']
        info.write("Done.")

    except RuntimeError as e:
        prompt_completion = prompt
        info.write(str(e))
        return prompt

    return prompt + " " + prompt_completion


app_title()


MAX_TOKEN = 2048
mode = st.sidebar.selectbox('Mode', ('Greedy', 'TopK', 'Nucleus'), index=1).lower()
n_token = st.sidebar.number_input(f"N tokens [1, {MAX_TOKEN}]", min_value=1, max_value=MAX_TOKEN, value=16)
temperature = st.sidebar.number_input("Temperature [0.01, 100]", min_value=0.01, max_value=100., value=1., step=0.05)
best_of = st.sidebar.number_input("Best of", min_value=1, max_value=16)
presence_penalty = st.sidebar.number_input("Presence penalty [0, 1]", min_value=0.0, max_value=1.0, value=0.0)
frequency_penalty = st.sidebar.number_input("Frequency penalty [0, 1]", min_value=0.0, max_value=1.0, value=0.0)
p = st.sidebar.number_input("p [0, 1]", min_value=0.0, max_value=1.0, value=0.9)
k = st.sidebar.number_input("k [1, 300]", min_value=1, max_value=300, value=3)

muse_api_key_data_env = os.getenv('MUSE_API_KEY', "")
muse_api_key_data = st.text_input("API KEY", value=muse_api_key_data_env)

if muse_api_key_data:
    os.environ['MUSE_API_KEY'] = muse_api_key_data


encourage_words = st.text_input("Encourage words", value="Bordeaux;Marseille",
                                help="Insert encouraged words separated by ;")
forbidden_words = st.text_input("Forbidden words", value="Paris;Lyon", help="Insert forbidden words separated by ;")
stop_words = st.text_input('Stop words', help="Insert stop words separated by ;")


prompt_input = st.empty()
generate_button = st.empty()

generate = generate_button.button("Generate")

# Initialization
if 'prompt_data' not in st.session_state:
    st.session_state['prompt_data'] = ""

height = 500
user_input = prompt_input.text_area("Prompt", value=st.session_state['prompt_data'], key="prompt_input", height=height)
if generate:

    generated_prompt = generate_prompt(
        user_input,
        n_token, mode,
        temperature,
        p,
        k,
        best_of,
        presence_penalty,
        frequency_penalty,
        encourage_words,
        forbidden_words
    )

    if generated_prompt != user_input:
        st.session_state['prompt_data'] = generated_prompt
        prompt_input.text_area("Prompt", value=generated_prompt, height=height)
