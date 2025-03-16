# Skylers MindHive Assessment
Hello Mindhive!

the above are all the source code for the given assignment. This assignment has been fun, met alot of unexpected challenges especially for deployment. But I'm glad to have done it, and learned alot from it.
you can take a look at the publiclly hosted version at https://mindhive.penguins-in-the-sky.xyz/ here

There has been a few uncertainties when it comes to the assignment: 

## Scraping
Considering that the website now injects all stores in malaysia via script, instead of queries, there isn't any pagination nor possible to scrape after given a search query, so the decision has been made to simply scrape the script itself which contains all known subway stores in malaysia, instead of limiting it to only Kuala Lumpur. last checked on 16/3/2025, https://subway.com.my/find-a-subway is down, if its permanently down then it might be my fault, or that they ip blocked me.

## Architecture
With this small of a scope, its actually better to have it monolithic. However I personally have a habit of building microservice style architecture from scratch, including a dedicated connection pooling service. It is absolute overkill to do such a thing. However I believe that starting with a microservice architecture pays off in the long run, and 
logistically it makes far more sense to code it as such. Please do read the internal documentation of connection pool service to read through my thought process.

## LLM
I'm testing out the latest LLM model by Alibaba called QWEN. currently using 3B parameters, with a 1.5B parameter embedding model by BAAI, Quantized with AWQ, using LLAMA.index for data augmentation and indexing, deployed with VLLM. Do note that deploying with VLLM is kind of a hassle with docker, and it took me quite a while to fix, feel free to contact me about any problems with setting it up, or you can simply spin it up manually without docker. I have yet the time to properly tune the LLM itself, so instead to ensure consistency I've taken measures in the system prompt to make it more limited in scope.

## RAG
For the RAG architecture, It is my greatest regret to not dedicate more time to planning it out. currently the document is simply a list of all stores, when more time should have been allocated to structuring a comprehensive list of documents that contains various analysis, proper geocoded stores, etc. As a consequence, the LLM is giving very inaccurate answers, disregarding its fairly low params count

## Local Hosting
In regards to local hosting LLMs, it is more of a personal preference, I find that I would learn more by simply locally hosting things rather than just relying on an online API. Of course this comes with a limitation of how powerful my actual setup is (4070 super 12GB VRAM). In production obviously we should be looking for cloud solutions, but for a test like this I'd much prefer locally hosting to understand the full breadth of complexity when it comes to full-stacking a LLM web app

# Disclaimer
Since this is locally hosted, and since the LLM does take up more than half of the VRAM available in my PC, there might be times where the chatbot just does not answer, if its so that means I've probably temporarily turned it off. Do not hesitate to contact me so that i can spin it right back up. A simple query should take no more than 3 seconds to return.

The code quality here is not my proudest, lack of consistency, type hints and documentations, proper implementations of PP, and so on. I apologize for all these, and hope that it can be overlooked. since this is CICD, ill probably update and clean the code when i have the time.

There are also a number of bugs that i have found while coding that i did not have the time to fix, these are marked with "TODO:" within the code itself.

I didn't have time to fully complete the sh file that I wanted to make to allow for easy installation. I do apologize for that as well

# Requirements
-docker

-docker compose

-docker buildx (needed for linux)

-python 3.11.11

-nvidia-container-toolkit

-mongo compass or mongodb-tools

-CUDA capable GPU

# Setup
Update:16/3/2025: https://subway.com.my/find-a-subway is down at the moment, it might not be possible to locally setup until it is up

## Via docker(setup is much more complicated because of nvidia-container-toolkit setup)-
Ensure all the requirements are installed on your computer

Request skyler for the setup files

From the setup files, merge the folders within /setup/envs with the working directory, the result being all service source code containing .env

Run setup.sh

go to your MongoDB at host.docker.internal:27017 and create a database called "MindHive", the username and password is skyler,skyler, respectively

create a empty called Routes collection and import the Routes.json

go to host.docker.internal:8004/docs# and perform a get request at /scrape

you can now connect to the website with http://0.0.0.0/8080


## Manually
the only requirements are python 3.11.11, and you would need to have your own way of serving mongodb and redis

Ensure all the requirements are installed on your computer

Request skyler for the setup files

From the setup files, merge the folders within /setup/env with the working directory, the result being all service source code containing .env

go to your MongoDB at host.docker.internal:27017 and create a database called "MindHive", the username and password is skyler,skyler, respectively

create a empty called Routes collection and import the Routes.json

You might need to tweak the connection link between redisdb, and mongodb, in the env of scraping service, and connection pool service, respectively, if you are hosting these services with a non-default port number

run every service up:

-backend services all uses fastapi run main.py --port [port number] check port usage section for assignment

-front end service simply uses python main.py

go to localhost:8004/docs# and perform a get request at /scrape


## Port Usage

Front-End: 8080

API Gateway: 3000

Connection Pool: 3001

Backend: 3002

LLM-Qwen: 3003

Scraping Spider: 3004


