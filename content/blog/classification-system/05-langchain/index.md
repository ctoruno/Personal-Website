---
author: Carlos A. Toruño P.
date: "2024-03-03"
draft: false
excerpt: Langchain is the most used framework when working with LLMs, in this post you will learn the basic functionalities that this library has to offer
subtitle: ""
weight: 1
title: Using Langchain and Gemini to classify news articles
subtitle: A quick tutorial on how to integrate the Langchain framework when working with Language Models
layout: single
tags:
- LLM
- Langchain
- Gemini
- AI
---

My dear three readers, I know I have been off for a whole month now and I feel terrible. Things have been really crazy at work lately. However, I found some time this weekend and I wanted to continue with my series on using AI to setup a gathering and classification system that is able to massively track and organize events that can provide insights on the state of the Rule of Law in a country. Until now, I have talked about how to gather news articles using a News API and how to classify them using AI, which is a topic that I left open back in January.

In my [previous blog post](https://www.carlos-toruno.com/blog/classification-system/04-llm-api/), I briefly mentioned [Langchain](https://www.langchain.com/langchain) and why it is a must-known framework if you are planning on working with Large Language Models. Retaking that conversation, Langchain is an open-source framework that facilitates the integration of generative AI models into your own framework. You can see it as a toolkit that covers and provide easy and fast solutions to many of the usual tasks that programmers face when dealing with language models. Langchain provides a whole set of features that makes your life easier. In this post, I'm just going to explain the basic features and how to integrate this amazing tool into our news classification exercise.

<img src="featured.jpg" width="100%"/>

## How does it work?
Langchain was built following a modular architecture. This means that you can easily call and use different components depending on your needs. The framework provides separate libraries for selectors, model wrappers, prompt managing, output parsers, text splittling, API interaction, among many others. You can think of Langchain as a Swiss Army Knife that comes with multiple blades and tools that you can use independently depending on how are you planning to interact with the language model.

At the same time, Langchain also allows you to streamline the process by constructing "_chains_". These chains are sequences of steps that process information, pass it to a language model, and ultimately generate an output. By programming these sequences or "_chains_", you can pre-program the process in order to have an assembly line ready for use.

For example, going back to [our news classification exercise](https://www.carlos-toruno.com/blog/classification-system/04-llm-api/), we needed to customize a prompt template, send a call to a language model, and then parse the received output. These three steps can be easily streamlined using Langchain. As I said before, in this post I will just touch base over some basic functionalities. However, if you would like a more indepth explanation of Langchain, I would suggest you to watch this video from Rabbitmetrics:

<iframe width="100%" height="345" src="https://www.youtube.com/embed/aywZrzNaKjs?si=qU0M4iE2CaeK3hVV" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

Additionally, I would also suggest you to read the official documentation publicly available in [this website](https://python.langchain.com/docs/get_started/introduction).

## Required libraries
At this point, is more than clear that we need to install Langchain in order to use it. We can proceed by installing the official python release version by running the following line in our terminal:

```console
pip install langchain
```

For this exercise, we will be using Google's Gemini model that was released on December, 2023. Therefore, we will also need to install the official [Python Software Development Kit from Google](https://ai.google.dev/tutorials/python_quickstart?_gl=1*1tz497e*_up*MQ..&gclid=CjwKCAiA3JCvBhA8EiwA4kujZjdXHbaRefWLu6WwPprj53XzQmUhuFAsITSrePIowuDG6-4Jb41WbxoC5a8QAvD_BwE#setup) and the [Google AI module from Langchain](https://python.langchain.com/docs/integrations/chat/google_generative_ai). Following the official documentation from both developers, we can install these by running the following lines in our terminal:

```console
pip install -q -U google-generativeai
pip install --upgrade --quiet  langchain-google-genai pillow
```

Once we have all the required libraries installed, we can proceed to import the modules we will be using in this tutorial. Most of these modules and libraries are already known by my three usual readers. Therefore, I'm just going to highlight three:
- The `ChatPromptTemplate` is a module that allows us to manage prompt templates.
- The `ChatGoogleGenerativeAI` is a wrapper that allows you to send calls or invoke the Gemini language model in a standardized fashion.
- The `BaseOutputParser` is a module that allow us to easily parse outputs received from language models.


```python
import json
import time
import pandas as pd
from langchain.schema import BaseOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory
)
from google.generativeai.types import BlockedPromptException
```

Now that we have all of our libraries and modules, the next important setup is to load our API key from [Google AI Studio](https://aistudio.google.com/). As I always highlight, you have to be super-extra-intensively careful when managing your API keys. **NEVER** display API keys in your scripts... unless... NO!! NEVER!! The most common way to load API keys is through environmental variables. For this, I usually use the [Python dotenv](https://github.com/theskumar/python-dotenv) library:


```python
import os
from dotenv import load_dotenv

# Loading API KEY from environment
load_dotenv()
GoogleAI_key = os.getenv("googleAI_API_key")
os.environ['GOOGLE_API_KEY'] = GoogleAI_key
```

## Reading and exploring our data
The data we will be working with for this tutorial is a dataset of 203 news articles for which we have 4 variables:
- Article ID
- Headline text
- Summary
- Full content text

Let's read the data and take a quick look into the first 15 articles in our set:


```python
master_data = pd.read_parquet("master-data.parquet.gzip")
master_data.head(15)
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
      <th>article_id</th>
      <th>title_eng</th>
      <th>desc_eng</th>
      <th>content_eng</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>5b3033b7646c124e2a893f135d6b6718</td>
      <td>Wikland's illustrations traveled to Latvia for...</td>
      <td>[caption id="attachment_412290" align="alignno...</td>
      <td>On Saturday, an exhibition of Ilon Wikland's i...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>c55891953899b72b8fc9e4132727cec0</td>
      <td>Goals by Nova Englund and Linnea Helmin were n...</td>
      <td>Surahammar was defeated in the meeting with Ha...</td>
      <td>Surahammar was defeated in the meeting with Ha...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>e7d7afc056b2aa73061834edf93aeaa7</td>
      <td>Leader of the Qassam Brigades: The Phantom of ...</td>
      <td>Mohammed Deif is the leader of the military wi...</td>
      <td>Mohammed Deif is the leader of the military wi...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>aa4e2287a042765adaed62e66c38cc6b</td>
      <td>Fierce criticism of the best tennis player in ...</td>
      <td>The world's top-ranked tennis player, Arina Sa...</td>
      <td>The best-ranked tennis player in the world, Be...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>d07d8deeb60237fb1a3c12e1b07ab50c</td>
      <td>Education Minister: Hubig: German skills in sc...</td>
      <td>Education Minister Stefanie Hubig (SPD) wants ...</td>
      <td>Hubig announced a precise analysis of the data...</td>
    </tr>
    <tr>
      <th>5</th>
      <td>7abd533276ada8c99a4611a95fa6056b</td>
      <td>The “Wild West” of Nantes in May: serial shoot...</td>
      <td>Around ten episodes of gunfire left one dead a...</td>
      <td>Le Figaro Nantes Bloody month of May in Nantes...</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2e51e03074e70136dc47cae1790bd721</td>
      <td>End of the Bundeswehr mission in Afghanistan: ...</td>
      <td>The current federal government wanted to use “...</td>
      <td>The current federal government wanted to use “...</td>
    </tr>
    <tr>
      <th>7</th>
      <td>c6697f8d32ddc66c6c48f6040e196466</td>
      <td>Cars and heavy vehicles, the European Parliame...</td>
      <td>BRUXELLES. Less polluting cars and vans, the E...</td>
      <td>BRUXELLES. Less polluting cars and vans, the E...</td>
    </tr>
    <tr>
      <th>8</th>
      <td>d1adbdd16c6f589859b3f0f4bb1bb7ed</td>
      <td>Danko overshadowed the Voice. The nominations ...</td>
      <td>As for the relations between Smer, Hlas and SN...</td>
      <td>The leader of Hlas Peter Pellegrini presented ...</td>
    </tr>
    <tr>
      <th>9</th>
      <td>df8c3e7629128fe0ecabe64837cd54de</td>
      <td>Iva Ančić: We expect a spectacle and an excell...</td>
      <td>We see that the awareness of gaming itself has...</td>
      <td>Reboot Infogamer powered by A1 is coming back ...</td>
    </tr>
    <tr>
      <th>10</th>
      <td>6623a54bdb6452ede407e47779ae0f28</td>
      <td>An analysis by Ulrich Reitz - Ban the AfD? An ...</td>
      <td>The Federal Minister of the Interior and her h...</td>
      <td>Comments Email Share More Twitter Print Feedba...</td>
    </tr>
    <tr>
      <th>11</th>
      <td>fd6a409ea84add5d803fee8e2877d071</td>
      <td>Now it's coming: the green light for the first...</td>
      <td>At its most recent meeting, the Homburg city c...</td>
      <td>Now here it comes, the bike zone in the Hombur...</td>
    </tr>
    <tr>
      <th>12</th>
      <td>d88ae6a3ec59ddc8dd2df71d32a2cbe1</td>
      <td>Municipalities: District warns of fraud when d...</td>
      <td>The Vorpommern-Greifswald district warns of in...</td>
      <td>The Vorpommern-Greifswald district warns of in...</td>
    </tr>
    <tr>
      <th>13</th>
      <td>1bf6ebbd3bad47afe77b0967f19b2a48</td>
      <td>That's why King Matthias shut down his uncle</td>
      <td>Contrary to expectations, Mátyás turned out to...</td>
      <td>Since Mátyás was a minor when László Hunyadi w...</td>
    </tr>
    <tr>
      <th>14</th>
      <td>f852ba76ef4574a0064c812b215d4ce0</td>
      <td>A PFAS ban? What does this mean for buyers of ...</td>
      <td>Alarming news is coming from the backrooms of ...</td>
      <td>Several environmental protection associations ...</td>
    </tr>
  </tbody>
</table>

## Loading the prompts
Today, we will be performing the same exercise that we did in [our previous blog post](https://www.carlos-toruno.com/blog/classification-system/04-llm-api/). As a summary, we will be doing a classification exercise in which we ask the Gemini model to read a news article and classify it in two groups: (i) articles that are related to our Rule of Law, Justice, and Governance framework, and (ii) those that are unrelated. Once that we have identified which articles are related to the Rule of Law, Justice, and Governance, we ask Gemini to provide a score telling us how closely related is the article to each one of the eight pillars of our framework: Constraints to Government Powers, Abscense of Corruption, Open Government, Fundamental Freedoms, Order and Security, Regulatory Enforcement, Civil Justice, and Criminal Justice. For that reason, we will be referring to each one of these classification rounds as _stage 1_ and _stage 2_, respectively. For each one of these stages, we will be passing a _context_ and an _instructions_ prompt. You can go over these prompts by clicking on the URLs bellow:
- [_Stage 1 - Context Prompt Template_](https://www.carlos-toruno.com/blog/classification-system/05-langchain/context_stage_1.txt)
- [_Stage 1 - Instructions Prompt Template_](https://www.carlos-toruno.com/blog/classification-system/05-langchain/instructions_stage_1.txt)
- [_Stage 2 - Context Prompt Template_](https://www.carlos-toruno.com/blog/classification-system/05-langchain/context_stage_2.txt)
- [_Stage 2 - Instructions Prompt Template_](https://www.carlos-toruno.com/blog/classification-system/05-langchain/instructions_stage_1.txt)

We proceed to load these plain text files as Python objects:


```python
def read_prompt(file_path):
    with open(file_path, 'r', encoding = "utf-8") as f:
        text = f.read()
    return text

context_stage_1      = read_prompt("context_stage_1.txt")
instructions_stage_1 = read_prompt("instructions_stage_1.txt")
context_stage_2      = read_prompt("context_stage_2.txt")
instructions_stage_2 = read_prompt("instructions_stage_2.txt")
```

You can open these prompt templates and see how they are trying to provide an accurate context and instructions to the model. Similarly, they provide a very extensive explanation of our theoretical framework so the model output fits our needs as best as possible. Our target is to pass this context every time that we ask Gemini to read an article, this is why we treat these as **templates**. If you open any of the instructions prompt templates, you will see that they include the following chunk of text:

> _Now, given the following news article:_<br>
> _News title: {headline}_<br>
> _News summary: {summary}_<br>
> _News body: {body}_

Everytime that we send a news article to Gemini, we have to replace the `{headline}`, `{summary}`, and `{body}` parts of the template with the actual headline, summary, and content that we have in our `master_data`. **It is very important that the .txt file that we are reading contain the "_replaceable_" parts within curly brackets in order for the prompt managing tools from Langchain to work as expected**. In my previous post, we were doing this using the `format()` method for strings in Python. However, Langchain provides a similar tool for managing and customizing prompts through the `ChatPromptTemplate` module. We can define our context template as a **_System Role_** message, and our instructions template as a **_Human Role_** using the `from_messages()` method. To understand how role management works in text generation models, you can check [this page](https://platform.openai.com/docs/guides/text-generation/chat-completions-api) from the OpenAI's official documentation. For our _stage 1_ exercise, we could define the prompt template as follows:

```python
stage_1_prompt = ChatPromptTemplate.from_messages([
                ("system", context_stage_1),
                ("human", instructions_stage_1),
            ])
```

This way, Langchain will understand that there are parts that will need to be replaced in the prompt text before passing it to the model. We will tell Langchain how to replace these values when invoking the model. For now, it is fine just having a final prompt with the roles properly assigned. This is the first step in our "_chain_".

Once that we have our prompt template defined, we can think on our second step, which is sending the customize prompt to Gemini. For this, Langchain offers a wide set of wrappers that makes it super easy to send calls to a large variety of Large Language Models. In this exercise, we will be using the `ChatGoogleGenerativeAI` wrapper to send our calls:

```python
ChatGoogleGenerativeAI(model = "gemini-pro",
                       temperature     = 0.2, 
                       safety_settings = safety_settings,
                       convert_system_message_to_human = True)
```

For our calls, we are defining that we would like to use the `gemini-pro` model with a temperature parameter of 0.15. The temperature parameter is used to control the _randomness_ or _creativity_  of the output. A low temperature will prioritize the next words in its prediction, while a high temperature will consider "less likely" options in the prediction. Given that we want the model to work under "_factual accuracy_", we pass a low temperature parameter. Moreover, given that Gemini does not support the "System Role" in its syntax, we activate the `convert_system_message_to_human` parameter.

Given that, by default, Gemini comes with some medium-high safety settings that could block a prompt to be answered by the model, we would like to reduce how strict these settings are. For this, we define a new set of safety nets as follows:


```python
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}
```

However, the model could still block some of our news articles by some undefined reasons that we cannot control. This will need to be taken into account when classifying the news articles. But now, we have completed the second step in our "_chain_".

Finally, we have asked the model to:

>_Use the following JSON format to answer:<br>_
>{{ <br>
>&nbsp;&nbsp;&nbsp;&nbsp;_rule_of_law_related: [Model Answer]_<br>
>}}

By giving the model this instruction, we can expect its answer to have a JSON structure formatting. However, the output will still be a string. Therefore, we need to parse this string as a python dictionary. For this, we will use the `BaseOutputParser` method as follows:


```python
class JSONOutputParser(BaseOutputParser):
    def parse(self, text: str):
        """
        Parse the output of an LLM call to a valid JSON format.
        """
        return json.loads(text.replace('```json', '').replace('```', ''), strict=False)
```

Having defined the output parser, we can say that we have succesfully defined the three steps required by our exercise. We can assemble all three steps into a single "_chain_" by using the `|` constructor provided by Langchain as follows:

```python
chain_gemini = chat_prompt | ChatGoogleGenerativeAI(model = "gemini-pro",
                                                    temperature     = 0.0, 
                                                    safety_settings = safety_settings,
                                                    convert_system_message_to_human = True) | JSONOutputParser()
```

If we were to manually classify one article at a time, this will be a valid solution. However, given that we want to pass all 203 news articles at once, we need to define a proper function that we are going to call `classify_article()`. This function will take a headline, a summary, and a full body content and it will classify or rate the news article according to which stage of the process we are referring to. Stay with me, the following chunk of code might be a little bit rough, so I suggest you to read the comments along the code.


```python
def classify_article(headline, summary, body, stage_1 = True, relation = None):
    """
    This function takes a headline, a summary, and the content of a news article and it sends a call to Google's Gemini
    to classify the article. There are two different classifications: Stage 1 and Stage 2. If stage_1 is set to TRUE, then
    the call to the model will try to answer the following question: Is this news article related or unrelated to the Rule of Law?
    If stage_1 is set to FALSE, then the call to the model will try to rate how closely related is the news article to each
    one of the eight pillars of the Rule of Law.
    """

    # Defining the prompt according to which stage are we calling the function for
    if stage_1 == True:
        system_prompt = context_stage_1
        human_prompt  = instructions_stage_1
    else:
        system_prompt = context_stage_2
        human_prompt  = instructions_stage_2

    # Setting up the Prompt Template
    chat_prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", human_prompt),
                ])

    # Defining our chain
    chain_gemini = chat_prompt | ChatGoogleGenerativeAI(model = "gemini-pro",
                                                        temperature     = 0.0, 
                                                        safety_settings = safety_settings,
                                                        convert_system_message_to_human = True) | JSONOutputParser()
    
    # For Stage 2, we don't want to pass articles that were already classified as "UNRELATED", so we pre-defined the outcome
    if stage_1 == False and relation != "Yes":
        outcome = "Unrelated"

    else:
        try: 
            llm_response = chain_gemini.invoke({
                "headline": headline,
                "summary" : summary,
                "body"    : body,
            })
            status = True
            time.sleep(1)   # We need to slow down the calls. given that the Gemini API has a limit of 60 calls per second

        # The API can still block some of our prompts due to undefined reasons. Sadly, we can't do anything about it, so we
        # predefine the outcome    
        except BlockedPromptException:
            print("BLOCKED")
            status = False
                
        # We use the STATUS variable to throw an outcome to our call depending if our prompt was blocked or not and
        # on the stage we are calling the function for
        if status == True:
            if stage_1 == True:
                outcome = llm_response["rule_of_law_related"]

            else:
                outcome = json.dumps(llm_response["pillars_relation"])
        else:
            outcome = "Blocked Prompt"

    return outcome
```

Once that we have this _awesome_ function defined, we can proceed to apply it to the whole data frame of news articles using the `apply()` method:


```python
# Stage 1 of the classification
master_data["gemini_stage_1"] = master_data.apply(lambda row: classify_article(row["title_eng"], 
                                                                               row["desc_eng"], 
                                                                               row["content_eng"], 
                                                                               stage_1 = True), axis = 1)
```

```python
master_data["gemini_stage_1"].value_counts()
```
    gemini_stage_1
    Unrelated         155
    Yes                47
    Blocked Prompt      1
    Name: count, dtype: int64

We can see that, after reading all 203 news articles, the model classified 155 as "Unrelated" and 47 as "Related" to the Rule of Law, Justice, and Governance framework that we passed. This means that, for the second stage, we will only pass 47 articles to see how closely related they are to each of the eight pillars in our framework. We proceed in the same manner that we did for Stage 1, but this time, we pass the outcome from Stage 1 as the `relation` parameter, so the function knows which articles to send to the model and which ones not to.

```python
# Stage 2 of the classification
master_data["gemini_stage_2"] = master_data.apply(lambda row: classify_article(row["title_eng"], 
                                                                               row["desc_eng"], 
                                                                               row["content_eng"], 
                                                                               relation = row["gemini_stage_1"],
                                                                               stage_1  = False), axis = 1)
```

For each one the 47 news articles that were classified as "RELATED" to the Rule of Law, the model has assigned a score from zero to ten rating how closely related the article is to each one the eight pillars of our framework. Let's take a look at one specific example:

```python
print(master_data["gemini_stage_2"][5])
```

```python
[
  {"1. Constraints on Government Powers": 8}, 
  {"2. Absence of Corruption": 7}, 
  {"3. Open Government": 6}, 
  {"4. Fundamental Rights": 7}, 
  {"5. Security": 9}, 
  {"6. Regulatory Enforcement and Enabling Business Environment": 5}, 
  {"7. Civil Justice": 4}, 
  {"8. Criminal Justice": 9}
]
```

As we can see, we have achieved our goal. However, Having this huge string in our data is not practical. Therefore, what we could do is to define a threshold under which, if the assigned rating is equal or above to this threshold, then we can firmly say that the article IS related to this pillar. Otherwise, we labelled this news article as UNRELATED to a specific pillar. Following that logic, we can create eight binary variables that will be equal to one if the article surpasses or is at least equal to the threshold and it will be equal to zero, otherwise. Let's write a function that will follow this logic.

```python
import ast

def extract_score(string, pillar, t = 7):
    """
    This function extracts scores from a string and returns a binary value that is equal to 1 if the score is higher/equal
    than a specific threshold, and it returns zero if otherwise.
    """
    try:
        scores_dicts = ast.literal_eval(string)
        ratings = [v for x in scores_dicts for _,v in x.items()]
        keys    = [k for x in scores_dicts for k,_ in x.items()]
        pattern = str(pillar) + ". "
        idx     = next((index for index, element in enumerate(keys) if pattern in element), None)

        if idx is not None:
            score = ratings[idx]
        else:
            score = 0
            
        if score >= t:
            return 1
        else:
            return 0
        
    except ValueError:
        if string == "Unrelated":
            return 0
```

Easy peasy, right?

We now proceed toapply the function to create the new set of binary variables:


```python
for i in range(1, 9):
    var_name     = "Gemini_pillar_" + str(i)
    master_data[var_name] = master_data["gemini_stage_2"].apply(lambda x: extract_score(x, i))
```


```python
master_data[master_data["gemini_stage_1"] == "Yes"].head(10)
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
      <th>article_id</th>
      <th>title_eng</th>
      <th>desc_eng</th>
      <th>content_eng</th>
      <th>gemini_stage_1</th>
      <th>gemini_stage_2</th>
      <th>Gemini_pillar_1</th>
      <th>Gemini_pillar_2</th>
      <th>Gemini_pillar_3</th>
      <th>Gemini_pillar_4</th>
      <th>Gemini_pillar_5</th>
      <th>Gemini_pillar_6</th>
      <th>Gemini_pillar_7</th>
      <th>Gemini_pillar_8</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>7abd533276ada8c99a4611a95fa6056b</td>
      <td>The “Wild West” of Nantes in May: serial shoot...</td>
      <td>Around ten episodes of gunfire left one dead a...</td>
      <td>Le Figaro Nantes Bloody month of May in Nantes...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2e51e03074e70136dc47cae1790bd721</td>
      <td>End of the Bundeswehr mission in Afghanistan: ...</td>
      <td>The current federal government wanted to use “...</td>
      <td>The current federal government wanted to use “...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>d1adbdd16c6f589859b3f0f4bb1bb7ed</td>
      <td>Danko overshadowed the Voice. The nominations ...</td>
      <td>As for the relations between Smer, Hlas and SN...</td>
      <td>The leader of Hlas Peter Pellegrini presented ...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 7}, {...</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>6623a54bdb6452ede407e47779ae0f28</td>
      <td>An analysis by Ulrich Reitz - Ban the AfD? An ...</td>
      <td>The Federal Minister of the Interior and her h...</td>
      <td>Comments Email Share More Twitter Print Feedba...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 9}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>13</th>
      <td>1bf6ebbd3bad47afe77b0967f19b2a48</td>
      <td>That's why King Matthias shut down his uncle</td>
      <td>Contrary to expectations, Mátyás turned out to...</td>
      <td>Since Mátyás was a minor when László Hunyadi w...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 10}, ...</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>16</th>
      <td>9563949a0c0bfff0105048ddcec42c63</td>
      <td>A man killed his wife and then committed suici...</td>
      <td>A man killed his wife and then tried to kill h...</td>
      <td>On the morning of October 16, 2023, a 66-year-...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 0}, {...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2c886c2fc437d97bcf6efc783c6135e8</td>
      <td>German-Polish border: Federal police start new...</td>
      <td>The federal police are gradually enforcing the...</td>
      <td>The federal police are gradually enforcing the...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>23</th>
      <td>fa07a7d9886fbb61bf4ed851f7a537aa</td>
      <td>Controversial decision: Naming the curator for...</td>
      <td>A heated argument is raging over the naming of...</td>
      <td>A heated argument has broken out in the Turkis...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>41</th>
      <td>6e3b6913c88b05f4e55572fe2302f72e</td>
      <td>An elderly woman got to know Pasi, and a large...</td>
      <td>The district court of Varsinais Suomen believe...</td>
      <td>A woman in her seventies slipped in the yard o...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>45</th>
      <td>f5f879f7c5fa7c97cbc66ed65a974cfc</td>
      <td>TAP. Leader of the Liberal Initiative accuses ...</td>
      <td>Rui Rocha highlighted that, during the commiss...</td>
      <td>This Monday, the president of IL accused the p...</td>
      <td>Yes</td>
      <td>[{"1. Constraints on Government Powers": 8}, {...</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>

```python
master_data.iloc[:,6:].apply(sum)
```

    Gemini_pillar_1    39
    Gemini_pillar_2    19
    Gemini_pillar_3     8
    Gemini_pillar_4    28
    Gemini_pillar_5    12
    Gemini_pillar_6     3
    Gemini_pillar_7    10
    Gemini_pillar_8    20
    dtype: int64


According to our results, 39 articles were classified as related to Pillar 1, while only three were classified as related to Pillar 6. There might be better ways to do what I just did (_if you happen to know one, just email me_), but this is how I am proceeding with the classification stage in our exercise. And that it is my dear readers. 

Bis bald und viele Spaß!!
