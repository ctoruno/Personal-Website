---
author: Carlos A. Toruño P.
date: "2024-01-28"
draft: false
excerpt: Accessing the power and capabilities of LLMs through their official API
subtitle: ""
weight: 1
title: Using GPT and Gemini to classify news articles
subtitle: A step-by-step guide on how to use the OpenAI and GoogleAI official APIs
layout: single
tags:
- LLM
- GPT
- Gemini
- AI
---

In my [previous blog post](https://www.carlos-toruno.com/blog/classification-system/03-using-chat-gpt-as-classifier/), I talked about Large Language Models (LLMs) and how you can use them to perform some specific tasks as long as you put special attention at how you are pharing your instructions to the model. However, we did all this using ChatGPT, which, technically speaking, is an app not a LLM. If you want to incorporate the power of LLMs into your own programming workflow you will have to access them through their official API. In this blog post I will go step by step on how to incorporate the power of GPT and Gemini models to your own framework in order to solve specific tasks.

<img src="featured.png" width="100%"/>

The task at hand will be very easy. First, we want to classify news articles into two groups: those related to the Rule of Law, and those unrelated to the Rule of Law. Second, for those articles that are related to the Rule of Law, we want to see how related they are to each on of the pillars of the Rule of Law. If you are a bit lost or feel unfamiliar with the theoretical framework, don't worry... so is the model. Therefore, I will be providing context along the road.

Let's see the data we will be working with.

## Loading the data
I will be working with a subset of news articles from European newspapers that we donloaded using a News API. For more information on how we were able to get this data, you can check [this blog post](https://www.carlos-toruno.com/blog/classification-system/01-gathering-data/). We begin by reading our data using the [Pandas Python Library](https://pandas.pydata.org/) as follows:


```python
import pandas as pd

master = pd.read_parquet("data_subset.parquet.gzip")
master.head(5)
```

<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>country</th>
      <th>journal</th>
      <th>asspillar</th>
      <th>language</th>
      <th>article_id</th>
      <th>title</th>
      <th>link</th>
      <th>keywords</th>
      <th>creator</th>
      <th>video_url</th>
      <th>...</th>
      <th>pubDate</th>
      <th>image_url</th>
      <th>source_id</th>
      <th>source_priority</th>
      <th>category</th>
      <th>language_id</th>
      <th>compiler</th>
      <th>title_trans</th>
      <th>description_trans</th>
      <th>content_trans</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2302</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>order_and_security</td>
      <td>german</td>
      <td>8535537712990c01388421e4aa6c8247</td>
      <td>Kein Ende des Kriegs in Israel in Sicht</td>
      <td>https://epaper.vn.at/titelblatt/2023/10/09/kei...</td>
      <td>[Titelblatt]</td>
      <td>[importuser]</td>
      <td>None</td>
      <td>...</td>
      <td>2023-10-09 20:45:15</td>
      <td>None</td>
      <td>vn</td>
      <td>1083701.0</td>
      <td>[top]</td>
      <td>de</td>
      <td>carlos</td>
      <td>No end to the war in Israel in sight</td>
      <td>Jerusalem The EU is suspending all payments to...</td>
      <td>Israel orders total blockade of the Gaza Strip...</td>
    </tr>
    <tr>
      <th>2307</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>order_and_security</td>
      <td>german</td>
      <td>c09c8b1761eed395062e595869472551</td>
      <td>Bewährungsprobe für Markus Söder</td>
      <td>https://epaper.vn.at/politik/2023/10/06/bewaeh...</td>
      <td>[Politik]</td>
      <td>[importuser]</td>
      <td>None</td>
      <td>...</td>
      <td>2023-10-06 20:49:05</td>
      <td>None</td>
      <td>vn</td>
      <td>1083701.0</td>
      <td>[politics]</td>
      <td>de</td>
      <td>carlos</td>
      <td>Test for Markus Söder</td>
      <td>Election in Bavaria on Sunday with some open q...</td>
      <td>The old Prime Minister will also be the new on...</td>
    </tr>
    <tr>
      <th>2313</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>order_and_security</td>
      <td>german</td>
      <td>b1783608728593e7d811d95e1b4f263a</td>
      <td>Bilder des Tages</td>
      <td>https://epaper.vn.at/politik/2023/10/02/bilder...</td>
      <td>[Politik]</td>
      <td>[importuser]</td>
      <td>None</td>
      <td>...</td>
      <td>2023-10-02 20:44:43</td>
      <td>None</td>
      <td>vn</td>
      <td>1083701.0</td>
      <td>[politics]</td>
      <td>de</td>
      <td>carlos</td>
      <td>Pictures of the day</td>
      <td>Translation through API failed. Reason: expect...</td>
      <td>The 2018 Nobel Peace Prize winner Denis Mukweg...</td>
    </tr>
    <tr>
      <th>2326</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>order_and_security</td>
      <td>german</td>
      <td>ed6711a119adb88769cda28ddd6c9b43</td>
      <td>Diebe stehlen 20 Tonnen Äpfel von Obstplantage</td>
      <td>https://epaper.vn.at/welt/2023/09/24/diebe-ste...</td>
      <td>[Welt]</td>
      <td>[importuser]</td>
      <td>None</td>
      <td>...</td>
      <td>2023-09-24 20:41:08</td>
      <td>None</td>
      <td>vn</td>
      <td>1083701.0</td>
      <td>[top]</td>
      <td>de</td>
      <td>carlos</td>
      <td>Thieves steal 20 tons of apples from orchard</td>
      <td>Dieterskirchen thieves stole around 20 tons of...</td>
      <td>Dieterskirchen thieves stole around 20 tons of...</td>
    </tr>
    <tr>
      <th>2328</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>order_and_security</td>
      <td>german</td>
      <td>baa36e05329fb8381a1d2c10f85b1134</td>
      <td>Politik in Kürze</td>
      <td>https://epaper.vn.at/politik/2023/09/21/politi...</td>
      <td>[Politik]</td>
      <td>[importuser]</td>
      <td>None</td>
      <td>...</td>
      <td>2023-09-21 20:49:39</td>
      <td>None</td>
      <td>vn</td>
      <td>1083701.0</td>
      <td>[politics]</td>
      <td>de</td>
      <td>carlos</td>
      <td>Politics in brief</td>
      <td>hangzhou Syrian President Bashar al-Assad is v...</td>
      <td>The Syrian ruler traveled to Hangzhou. Sana/AF...</td>
    </tr>
  </tbody>
</table>

The data we will be using is a small subset of 100 news articles from way bigger data file that contains information of more than 32,000 news articles from European newspapers. As you might have noticed, the data was stored as a parquet file. For huge quatities of information, [Apache Parquet](https://parquet.apache.org/) is a more efficient format to store data than JSON or CSV in terms of storage, memory usage, and reading speed. If you want to learn more about the advantages of human non-readable formats I would suggest you to read [this article](https://towardsdatascience.com/which-data-format-to-use-for-your-big-data-project-837a48d3661d) from Towards Data Science.

For the purpose of this blog post, I will only work with 5 specific news articles from the above subset and save them as a pandas data frame called `extract`. Let's take a look at the wonderful winners of this lotto: 


```python
idx = [2307, 2357, 2383, 2439, 2951]
extract = master.loc[idx, ["country", "journal", "article_id", "link", "title_trans", "description_trans", "content_trans"]]
extract
```

<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>country</th>
      <th>journal</th>
      <th>article_id</th>
      <th>link</th>
      <th>title_trans</th>
      <th>description_trans</th>
      <th>content_trans</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2307</th>
      <td>[austria]</td>
      <td>https://www.vn.at/</td>
      <td>c09c8b1761eed395062e595869472551</td>
      <td>https://epaper.vn.at/politik/2023/10/06/bewaeh...</td>
      <td>Test for Markus Söder</td>
      <td>Election in Bavaria on Sunday with some open q...</td>
      <td>The old Prime Minister will also be the new on...</td>
    </tr>
    <tr>
      <th>2357</th>
      <td>[austria]</td>
      <td>https://www.salzburg24.at/</td>
      <td>edfa1c27e299213b2e2bf4325361a0ba</td>
      <td>https://www.salzburg24.at/news/oesterreich/dre...</td>
      <td>Three dead in fire in LK Mödling: investigatio...</td>
      <td>After three patients died in a fire at the Möd...</td>
      <td>0 Published: 18. October 2023 3:33 p.m. After ...</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>[austria]</td>
      <td>https://www.salzburg24.at/</td>
      <td>27abe7fe74f897c0192e5e59188a9d1f</td>
      <td>https://www.salzburg24.at/news/welt/klima-prot...</td>
      <td>Climate protest in The Hague: 2,400 arrests</td>
      <td>In the Dutch city of The Hague, police broke u...</td>
      <td>0 Wij verafschuwen het geweld the word was use...</td>
    </tr>
    <tr>
      <th>2439</th>
      <td>[austria]</td>
      <td>https://www.salzburg24.at/</td>
      <td>80cea065a92d0e20c0b260a612fd1b87</td>
      <td>https://www.salzburg24.at/sport/fussball/oeste...</td>
      <td>Failed qualifying dress rehearsal for Austria</td>
      <td>Austria's national soccer team failed in the d...</td>
      <td>0 Published: 07. September 2023 10:38 p.m. Aus...</td>
    </tr>
    <tr>
      <th>2951</th>
      <td>[belgium]</td>
      <td>https://www.lesoir.be/</td>
      <td>8739dea5ef18c8f95991f1b063804e1f</td>
      <td>https://www.lesoir.be/520042/article/2023-06-1...</td>
      <td>Tax reform in Belgium, an emergency for sixty ...</td>
      <td>The federal government is trying to reform tax...</td>
      <td>The big tax reform, everyone wants it, but no ...</td>
    </tr>
  </tbody>
</table>



## Writting the instructions

As I mentioned before, we are going to divide the task at hand in two stages. In the first stage, we will classify articles according to their relation to the Rule of Law. For this, we will use a contextual prompt as follows:

>_You are an assistant with knowledge and subject-matter expertise on Rule of Law, justice, governance, global politics, 
>social sciences, and related fields in the European Union. Your task is to carefully read a news article and determine 
>whether it is related to the definitions of Rule of Law, Justice, and Governance that I will give you. To successfully 
>perform this task, you should carefully read the definitions that I will provide, and use the knowledge of global politics, 
>law, and social sciences that you have._

Additionally, we will write the additional information, the news article, and the set of instructions in a separate prompt that we are going to call `instructions_stage_1`. First, I will provide some _key concepts_ to the model so it doesn't base its answers entirely on the information that was used during its training. This is done so we can have some control on the predicted tokens used by the model to provide an answer.

>#### Key macro concepts
>_Here are the definitions of Rule of Law, Justice, and Governance:_
>
>_The term Rule of Law refers to ..._
>
>_We define Justice as ..._
>
>_Finally, we define Governance as ..._

In the same prompt, after passing the key concepts, I will pass the headline, summary, and full content of the news article:

>_Now, given the following news article:_
>
>_News title:_ {headline}
>
>_News summary:_ {summary}
>
>_News body:_ {body}

Finally, I will provide some specific instructions telling the model what to do with the information I just passed and I will ask the model to structure its answer following a specific JSON format:

>_Please analyze the news article and its context, and answer the following question:_
>1. _Based on the definitions that I just provided above, is this news article narrating events related to the Rule of _
>_Law, Justice, or Governance?_
>
>_Use the following JSON format to answer:_
>
>{{
>
>    _rule_of_law_related: answer to the question number 1. if the news article is not related to the Rule of Law, Justice,_ 
>    _or Governance answer with "Unrelated", otherwise answer with "Yes"._
>
>}}

I will make use of [Markdown](https://www.markdownguide.org/basic-syntax/) syntax such as headers (#) and lists to structure and pass the information to the model. You can check the FULL instruction prompt that I'm using for the first stage [here](https://www.carlos-toruno.com/blog/classification-system/04-Langchain-GeminiPro/instructions_stage_1.txt).

## Accesing LLMs through their API endpoints

Now that we have loaded the data, we have written (and tested) our prompt, we can proceed to use a LLM to perform the task for us. To be able to send requests to an API, we need to have an API Key. In this guide, we will be using the [GPT model from OpenAI](https://openai.com/gpt-4) and the [Gemini model from GoogleAI](https://deepmind.google/technologies/gemini/#introduction). Therefore, in order to follow this guide, you will have to create an account and an API key from these two developers. Right now, January 2024, accessing the Gemini Pro model through its official API is free and open to the public given that they are introducing the product to the market.

[In a previous post](https://www.carlos-toruno.com/blog/classification-system/01-gathering-data/#managing-you-api-key), I talked about how to manage your API keys through environment variables. Just in case, I leave you the video explaining how to do this using the [dotenv Python library](https://github.com/theskumar/python-dotenv).

<iframe width="100%" height="325" src="https://www.youtube.com/embed/CJjSOzb0IYs?si=Klk-0E98DidAOf1_" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

We start by loading our API keys as follows:


```python
import os
from dotenv import load_dotenv

# Loading API KEY from environment
load_dotenv()
OpenAI_key   = os.getenv("openai_key")
GoogleAI_key = os.getenv("GOOGLE_API_KEY") 
```

Once we have our API keys loaded as environment variables, we can use the [OpenAI official Python library](https://github.com/openai/openai-python) to send calls and acces their models. OpenAI has different model families depending on the capability you are interested. [DALL·E](https://openai.com/dall-e-3) is a family of models focused on image generation, [Whisper](https://openai.com/research/whisper) is a family of models focused on speech recognition, and [GPT](https://openai.com/gpt-4) is their signature model focused on text generation. For a task such as text classification, what we need is a text model. Therefore, we will be using the `GPT-4-Turbo` model to classify our news articles.

First, let's focus only in the news article about the elections in Bavaria "_A Test for Markus Söder_" with row index `2307` in our `extract` data frame:


```python
headline = extract.loc[2307, "title_trans"]
summary  = extract.loc[2307, "description_trans"]
body     = extract.loc[2307, "content_trans"]
```

We pass the headline, summary, and content of the news article to the `instructions_stage_1` prompt using the `format()` method:


```python
instructions_stage_1_2307 = instructions_stage_1.format(headline = headline, 
                                                        summary  = summary, 
                                                        body     = body)
```

We will use the Chat Completion endpoint to pass the information and classify the article at hand as RELATED or UNRELATED to the definition of Rule of Law that we have. The Chat Completion API will take a list of messages as input, and generate an output. However, these messages need to be assign to a specific role.

According to the [official OpenAI documentation](https://platform.openai.com/docs/guides/text-generation/chat-completions-api), there are three roles available: "_system_", "_user_", and "_assistant_". The system message will be setting the general behavior of the model across the conversation. The user messages provide requests or comments for the assistant to respond to. Assistant messages store previous assistant responses, but you can also pass example responses to signal a desired behavior for the model.

Having this in mind, we will pass our `context_stage_1` prompt as the **_system message_**, and our `instructions_stage_1` prompt as a **_user_** message. This information is passaed to the API wrapper as individual Python dictionaries within a list.

We will also require the model to provide its answer in a JSON format by specifying the "_type_" parameter in the `response_format` argument.


```python
from openai import OpenAI

client = OpenAI(api_key = os.getenv("openai_key"))

completion = client.chat.completions.create(
    model = "gpt-4-0125-preview",
    messages = [
        {"role": "system", "content": context_stage_1},
        {"role": "user",   "content": instructions_stage_1_2307}
    ],
    response_format = {"type": "json_object"},
    temperature = 0.2
)
```

We take a look to the answer provided by the language model by printing the choices of answers thrown by the model. By default, the response object will only contain one single choice, but you can modify this by adding the respective arguments to the call. As we can observe, the model has classified the news article as **RELATED** to the Rule of Law, which, to be honest, makes sense because the article is talking about elections in Bayern, Germany.

If you are wondering about the `temperature` parameter, it is a numeric value between 0 and 1 that signals how deterministic or random should the assistant construct its answer. Lower values make the answer more deterministic and focused, while higher values will increase the randomness of the output.


```python
print(completion.choices[0].message.content)
```

    {
        "rule_of_law_related": "Yes"
    }
    

We have succesfully completed the first stage. Now that we know that the article is related to the Rule of Law, we can proceed to the second stage of our task: rating from zero to ten how related is this article to each one of the pillars of the Rule of Law. For this, we will be making some adjustments to our prompts. 

For example, we modify our _context prompt_ to incorporate the new objective:

>_You are an assistant with knowledge and expertise in global politics, social sciences, rule of law, and related fields. Your task is to assist 
>me in classifying news articles according to which pillar of the Rule of Law do they belong to. To successfully accomplish this task, you will 
>have to carefully read a news article and the definitions of each pillar that I will give you, as well as use the knowledge of global politics, 
>social sciences, and law that you have. Once you have read the news article, you will proceed to determine the extent to which the events 
>described in the news article are related to each pillar._

For our _instructions prompt_ we will be using a rather large text that spans over 4,000 words. However, you can check the full text of the prompt [here](https://www.carlos-toruno.com/blog/classification-system/04-Langchain-GeminiPro/instructions_stage_2.txt). Having these new inputs, we can send a new request in the same way we did before:


```python
# Introducing the news article into the instruction prompt
instructions_stage_2_2307 = instructions_stage_2.format(headline = headline, 
                                                        summary  = summary, 
                                                        body     = body)

# Making a request to the GPT Chat Completions API
completion = client.chat.completions.create(
    model = "gpt-4-0125-preview",
    messages = [
        {"role": "system", "content": context_stage_2},
        {"role": "user",   "content": instructions_stage_2_2307}
    ],
    response_format = {"type": "json_object"},
    temperature = 0.2
)

# Printing the output
print(completion.choices[0].message.content)
```

    {
        "pillars_relation": [
            {"1. Constraints on Government Powers": 8},
            {"2. Absence of Corruption": 5},
            {"3. Open Government": 7},
            {"4. Fundamental Rights": 2},
            {"5. Order and Security": 1},
            {"6. Regulatory Enforcement and Enabling Business Environment": 1},
            {"7. Civil Justice": 1},
            {"8. Criminal Justice": 1}
        ]
    }
    

**Beautiful!** **Subarashī!**

We can see that the model thinks that the news article in **highly related** to pillars 1 "_Constraints on Government Powers_" and pillar 3 "_Open Government_"; somehow related to pillar 2 "_Absence of Corruption_", and completely unrelated to all the other pillars. Honestly... that was amazing. Because those are quite similar to the ratings that I (an allegedly expert in the topic) would give to the article. The model only needed some context and instructions to start generating text. Behind the curtains, what is happening is that the model is just constructing sentences based on the probability of what the next word is basing its predictions on the inputs that you just passed. Again, isn't that amazing?

Let's continue with our journey. We can do the exact same task, using another big language model that was just release in December, 2023 by Google. The **Gemini Pro**. Unlike the GPT-4-Turbo, Google has granted free access to the Gemini Pro capabilities through their official API. In order to use this model, we will need to adjust some things:

- First, the Google API only accepts two roles in the list of messages: "_user_" and "_model_", so we will have to turn the context prompt into a user message.
- Second, the API only accepts multi-turn conversations. That means that, for our specific case in which we pass two user messages, we also need to provide a model answer to the first message. A short text like: "_Sure, I can assist you in classifying news articles according to the pillars of the Rule of Law._" will be enough.
- Third, we need to setup some safety settings to avoid getting rejections in our calls. Please check the [official Python documentation](https://ai.google.dev/tutorials/python_quickstart) for more information.

Let's begin by authenticating and setting up a channel through the Generative Model endpoint as follows:

```python
import google.generativeai as genai

# Authenticating our API key
genai.configure(api_key = GoogleAI_key)

# Set up the model config
generation_config = {
  "temperature": 0.2,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 1000,
}

# Safety presettings
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
]

# Set-up a model
model = genai.GenerativeModel(model_name        = "gemini-pro",
                              generation_config = generation_config,
                              safety_settings   = safety_settings)
```

Once that we have set-up a model to be used, we can start a multi-turn instance with the model to provide the information contained in `context_stage_1`, and `instructions_stage_1`. We do this by making use of the `start_chat()` method for the open instances. In the same manner as we did when interacting with the GPT model, we need to send the context and the model answer prompts as part of a history of messages. However, this time, we are sending the instructions as a new message to the conversation and waiting for the response.

Just imagine that you open your own messaging app and you see a prior conversation with the Gemini model where you are asking for a specific task. Then, you just send the instructions prompt as a new message to this conversation because you forgot it. Really easy, right?

```python
# Start an instance
instance = model.start_chat(history = [
  {
    "role": "user",
    "parts": [context_stage_1]
  },
  {
    "role": "model",
    "parts": [model_answer_stage_1]
  }
])

# Sending instructions
instance.send_message(instructions_stage_1_2307)

# Previewing answer
print(instance.last.text)
```

    ```
    {
        "rule_of_law_related": "Yes"
    }
    ```
    

As we can observe, Gemini Pro also thinks that this news article is related to the Rule of Law. Still amazing, don't get me wrong. Let's now try it again but now with the second stage. Let's compare the ratings assigned by GPT and Gemini to the same news article:


```python
# Start an instance
instance = model.start_chat(history = [
  {
    "role": "user",
    "parts": [context_stage_2]
  },
  {
    "role": "model",
    "parts": [model_answer_stage_2]
  }
])

# Sending instructions
instance.send_message(instructions_stage_2_2307)

# Previewing answer
print(instance.last.text)
```

    ```
    {
        "pillars_relation": [
            {
                "1. Constraints on Government Powers": 7
            },
            {
                "2. Absence of Corruption": 5
            },
            {
                "3. Open Government": 4
            },
            {
                "4. Fundamental Rights": 6
            },
            {
                "5. Security": 3
            },
            {
                "6. Regulatory Enforcement and Enabling Business Environment": 2
            },
            {
                "7. Civil Justice": 1
            },
            {
                "8. Criminal Justice": 1
            }
        ]
    }
    ```

As we can observe, the ratings are somehow similar between GPT and Gemini. However, Gemini scored Pillar 4 "_Fundamental Rights_" higher than GPT, while also giving a lower score to Pillar 3 "_Open Government_". Both answers are acceptable, and I can also see the potential reasons behind the differences in the scores, but that goes beyond the scope of this post.

We can extract the individual scores for each pillar by parsing the string content into a Python dictionary and extracting the dictionary values using a list comprehension. This way we can keep track of the scores in a more data-focused way for our news articles.


```python
import json

json_content  = json.loads(instance.last.text[3:-3])
pillar_scores = [list(x.values())[0] for x in json_content["pillars_relation"]]
pillar_scores
```

    [7, 5, 4, 6, 3, 2, 1, 1]

## Setting up a data workflow

By now, you are able to use the OpenAI and GoogleAI APIs to access their models in order to generate text outputs. However, we have been doing it targeting a single news article. This gives us no advantage against using the official apps such as ChatGPT or Bard. The main purpose for us to access the power and capabilities of the models through their API is to be able to process large amounts of information without having to depend on an user interface. In other words, accessing the model in a programmatically way. In other words, instead of running the code individually for each article, having access to the API allow us to set up a workflow to process a whole data file. 

For example, in our case, we will define a single function that will perform the task automatically for us. The function will work as follows:
- First, it will extract the relevant information for each news article (headlin, summary, and content) and format an instruction prompt for that article in specific.
- Then, it will send the instructions to the model through their respective API.
- Finally, it will parse and process the string output sent by the model and store it as new variables in our data frame.

We will use the GeminiPro API for this example as follows:


```python
def classify_article(row, stage):
    """
    A function that takes a row as an input, formats a prompt, sends 
    a conversation request to the GeminiPro API and returns the answer 
    from the model.
    """
    if stage == 1:
        instprompt = instructions_stage_1
        conprompt  = context_stage_1
        ansprompt  = model_answer_stage_1
    if stage == 2:
        instprompt = instructions_stage_2
        conprompt  = context_stage_2
        ansprompt  = model_answer_stage_2

    # Formatting prompt
    prompt = instprompt.format(headline = row["title_trans"], 
                               summary  = row["description_trans"], 
                               body     = row["content_trans"])
    
    # Start an instance
    instance = model.start_chat(history = [
    {
        "role": "user",
        "parts": [conprompt]
    },
    {
        "role": "model",
        "parts": [ansprompt]
    }
    ])
    
    # Sending instructions
    instance.send_message(prompt)

    # Parsening results
    out = json.loads(instance.last.text[3:-3])
    if stage == 1:
        val = list(out.values())[0]
        return val
    
    if stage == 2:
        if row["stage_1"] == "Yes":
            pillar_scores = [list(x.values())[0] for x in out["pillars_relation"]]
        
        else:
            pillar_scores = [0,0,0,0,0,0,0,0]

        return pillar_scores
```

Once we have the function defined, we can use vectorization to apply it to a whole data frame. We will test it using the `extract` data file with our 5 news articles.


```python
extract["stage_1"] = extract.apply(lambda row: classify_article(row, stage=1), axis = 1)
extract["stage_2"] = extract.apply(lambda row: classify_article(row, stage=2), axis = 1)
```

```python
extract.loc[:,["title_trans", "description_trans", "content_trans", "stage_1", "stage_2"]]
```

<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table>
  <style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

    table {
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
  </style>
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>title_trans</th>
      <th>description_trans</th>
      <th>content_trans</th>
      <th>stage_1</th>
      <th>stage_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2307</th>
      <td>Test for Markus Söder</td>
      <td>Election in Bavaria on Sunday with some open q...</td>
      <td>The old Prime Minister will also be the new on...</td>
      <td>Yes</td>
      <td>[7, 5, 4, 6, 2, 3, 2, 2]</td>
    </tr>
    <tr>
      <th>2357</th>
      <td>Three dead in fire in LK Mödling: investigatio...</td>
      <td>After three patients died in a fire at the Möd...</td>
      <td>0 Published: 18. October 2023 3:33 p.m. After ...</td>
      <td>Yes</td>
      <td>[3, 2, 1, 5, 7, 1, 2, 8]</td>
    </tr>
    <tr>
      <th>2383</th>
      <td>Climate protest in The Hague: 2,400 arrests</td>
      <td>In the Dutch city of The Hague, police broke u...</td>
      <td>0 Wij verafschuwen het geweld the word was use...</td>
      <td>Yes</td>
      <td>[7, 0, 0, 8, 7, 0, 0, 9]</td>
    </tr>
    <tr>
      <th>2439</th>
      <td>Failed qualifying dress rehearsal for Austria</td>
      <td>Austria's national soccer team failed in the d...</td>
      <td>0 Published: 07. September 2023 10:38 p.m. Aus...</td>
      <td>Not related to Rule of Law</td>
      <td>[0, 0, 0, 0, 0, 0, 0, 0]</td>
    </tr>
    <tr>
      <th>2951</th>
      <td>Tax reform in Belgium, an emergency for sixty ...</td>
      <td>The federal government is trying to reform tax...</td>
      <td>The big tax reform, everyone wants it, but no ...</td>
      <td>Not related to Rule of Law</td>
      <td>[0, 0, 0, 0, 0, 0, 0, 0]</td>
    </tr>
  </tbody>
</table>


**Sehr schön!**

You can now try playing and process/generate data with Large Language Models by extending these examples on your own data project. As I mentioned in my previous post, there are hundreds of LLMs available for you to play out there. Some of them have their own python library available. In this situation, where setting up workflows with different providers can easily become chaotic, you need to worry. The [Langchain framework](https://www.langchain.com/) comes in handy for this. 

Langchain is a framework for developing applications powered by language models. It provides tools for connecting your application with different models, managing prompt templates, parsening outcomes, among many other features. In a future blog post, I will elaborate a bit more on the basic use of this framework to facilitate many of the steps we implemented in this example. Until then, farewell my dear three readers.

Finally, I would like to thanks [Pablo Gonzalez](https://github.com/pgonzalezb4) for its valuable mentorship and support in this project.
