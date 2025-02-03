# Building Your AI-Powered Aptos Agent

The Aptos blockchain allows developers—and even non-developers—to interact with Move modules (smart contracts) through various SDKs, APIs, and ABIs. Now, with the help of this AI Agent, you can do all that **through a conversation**—no deep coding expertise required. If the idea of opening a terminal makes you nervous, check out [Brian Wong’s Aptos Agent Template](https://x.com/briannwongg/status/1867716033659965672) on Replit (no Github required!), which inspired this very tutorial.

## Why Build an AI Agent on Aptos?

AI Agents have exploded in popularity thanks to large language models (LLMs) like ChatGPT. Instead of performing narrow tasks (like old-school trading bots), our AI Agent uses an LLM in a conversation loop ([called a REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop)) and some pre-defined functions so that it can follow plain-English instructions—“Deploy a token,” “Check my wallet balance,” or “Store data on-chain.” 

In 2024, projects like **Freysa** showcased an AI defending a blockchain account holding $47,000 in prize money while players paid to try to trick it, illustrating the creative (and sometimes devious) potential of these new assistants.

![image.png](image)

> [!NOTE]  
> We use Python in this tutorial but you should be able to complete this tutorial without any Python experience.

By connecting GPT-4o to Aptos’s Move smart contracts and Python’s aptos-sdk, we’re building an agent that:

- **Understands** your instructions in everyday language.
- **Interacts** with your on-chain resources (e.g., deploying tokens, querying data).
- **Executes** transactions on your behalf, all through simple chat prompts.

## Tutorial Overview

This guide will show you how to:

1. Set up a Python environment for running your agent.
2. Build and configure an AI agent that you can play with on your computer.
3. Test your agent with real blockchain actions — even those in your own Move modules!

If you’re coming from Node.js, don’t worry—we’ll provide analogies to help bridge the gap.

## How It Works

You can think of your AI Agent as a helpful bank employee. They constantly listen to what you say (`main.py`), know how to handle your finances on-chain (`aptos_wrapper.py`), and have been trained by Corporate on how to be helpful (`agents.py`).

In other words, the Aptos Agent is built with three main files:

1. `main.py` - This starts the conversation loop (REPL) between you and the Agent.
2. `aptos_wrapper.py` - This tells the agent how to talk to the Aptos blockchain using the Aptos SDK and Fullnode API.
3. `agents.py` - This is where functions that the AI Agent can actually directly call live. It’s also where we define some specific “instructions” for GPT.

By running `main.py`, you start a conversation where you can ask the AI Agent whatever you want, and the agent will do it’s best to answer and do what you ask.  No complicated scripts **or manual transaction-building required.**

## Pre-requisites

1. $5 for OpenAI (this tutorial will only use up a few pennies, but that’s their minimum)
2. A GitHub account to download the Agent with `git clone`

> [!NOTE]  
> This tutorial is written for Mac / Linux, so Windows users will need to modify some commands.
>
> Asking [ChatGPT](chat.openai.com) for the Windows version can be a quick way to get the right command!

## Part 0: Getting Your OpenAI API Key
To create an AI Agent, you will need an API key for the AI. This agent was written to work with ChatGPT 4o, so before we dive into the details of how to run the agent’s code, you will need to create an OpenAI account. 

**If you already have an OpenAI account:**

1. Go to https://platform.openai.com/api-keys.
2. Login.
3. Copy your API key for later (we will use it in the .env file).
4. Ensure that your account has funds.
5. Skip to **Part 1** below!

**Otherwise, if you do NOT have an OpenAI account:** follow the below instructions to “Get an API Key From Scratch”!

### Get a Funded API Key From Scratch

1. Go to [platform.openai.com](https://platform.openai.com/).
2. Click “Start Building” in the top right corner.

   <img width="281" alt="Step2" src="https://github.com/user-attachments/assets/20b8d877-1c74-4d19-a935-1f348121237b" />
    
3. Name your organization.

<img width="387" alt="Step3" src="https://github.com/user-attachments/assets/5fc083ac-3649-4458-8861-3de4ef4c93d3" />

4. Click “I’ll invite my team later”
   
<img width="387" alt="Step4" src="https://github.com/user-attachments/assets/50ba66d8-7f1c-48c9-8132-04c82752754f" />

5. Name your API key and project (see below for an example):

<img width="387" alt="Step5" src="https://github.com/user-attachments/assets/66d24fde-d4d7-4b85-8f33-014b990ecaca" />

6. Click “Copy” on your newly generated API key.
   
<img width="521" alt="Step6" src="https://github.com/user-attachments/assets/1ce14a6b-f631-4a5d-a775-baeb8bb6b09b" />

7. Paste this into a text file for later (We will eventually move this into the .env file for this project)
8. Click “Continue”

<img width="378" alt="Step8" src="https://github.com/user-attachments/assets/a400213b-a58a-44ca-a9d0-d1f06fdfd53a" />

9. Add at least $5 dollars in credit (this tutorial should only cost pennies!)

<img width="378" alt="Step9" src="https://github.com/user-attachments/assets/612b29db-dff1-41a5-9bb3-a13960e08375" />

10. Click “Purchase Credits”.
    
<img width="370" alt="Step10" src="https://github.com/user-attachments/assets/94c5e5d8-b024-4d44-9533-8f10326e5976" />
    
11. Add a payment method.

<img width="499" alt="Step11" src="https://github.com/user-attachments/assets/8ca807de-f8d5-4d06-8722-ddb7e89adaf2" />

12. Click “Add payment method” in the bottom right corner.

<img width="171" alt="Step12" src="https://github.com/user-attachments/assets/2c753532-468a-4e00-b3bc-26d3411c818a" />

13. Use the payment method to purchase the $5 of credits.

> [!NOTE]  
> You should now have a funded API key that you've stored in a text file (temporarily).
>
> It may take a few minutes for this API key to work after funding.

## Part 1: Getting Ready To Run Your Aptos Agent

Before we write any code, we need to set up our development environment. That means downloading the code, choosing the right version of Python, and installing our dependencies.

1. Open your terminal.

2. Create your project directory:
```bash
git clone https://github.com/tippi-fifestarr/aptos-agent-local.git aptos-agent
cd aptos-agent
```

3. Copy `.env-example` into a new file named `.env` by running:
```bash
cp .env-example .env
```

4. Edit `.env` and add your Open API key in quotes:

It should look something like:
```
OPENAI_API_KEY='sk-proj-ABcdeafefa...'
```

> [!NOTE]
> Remember to save!
   
5. Check if you have Python installed:
```bash
python3 --version
```

> [!NOTE]
> We will need python version 3.10 or higher to work with the AI Agent library `swarm`.
> `pyenv` will help us choose which version of python we are using.

6. Ensure you have `pyenv` installed by running `pyenv --version`.

If you do not have `pyenv` installed, you can download it using Homebrew:
```bash
brew install pyenv
```

> [!NOTE]  
> If you don't have Homebrew installed, visit [brew.sh](https://brew.sh) and follow the installation instructions.

7. Add pyenv configuration to your shell:
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

8. Load your new configuration:
```bash
source ~/.zshrc
```

9. Install Python 3.11 (this will take a minute or so):
```bash
pyenv install 3.11
```

> [!NOTE]  
> Now might be a good time to have a little coffee or something while that downloads.

> [!WARNING]  
> You might see warnings about missing tkinter during installation. This is normal and won't affect our project. The installation will still complete successfully.

10. Set Python 3.11 for your project:
```bash
pyenv local 3.11
```

> [!NOTE]  
> Using `pyenv` to pick a specific version of `python` requires us to use `python` instead of `python3` for commands going forward.

11. Create a virtual environment:
```bash
python -m venv venv
```

A virtual environment keeps your project's dependencies isolated, similar to how each Node.js project has its own `node_modules` folder.

This command does several things:

- Creates a new folder called `venv`
- Sets up a fresh Python installation inside it
- Isolates our project's dependencies from other Python projects

12. Activate the virtual environment:
```bash
source venv/bin/activate
```
Your prompt should now show `(venv)` or `(aptos-agent)` at the beginning.

> [!NOTE] 
> The purpose of activating the virtual environment is to keep your project dependencies isolated. This ensures different projects don't interfere with each other's required packages.
>
> The next time you open a terminal, you'll need to activate your virtual environment again by:
> 1. Navigating to your project directory
> 2. Running `source venv/bin/activate`

13. Upgrade pip (Python's package manager):
```bash
python -m pip install --upgrade pip
```

14. Install Swarm, OpenAI and all our other dependencies by running:

`pip install -r requirements.txt`

> [!NOTE]  
> Let's understand what each package does:
> - `swarm`: OpenAI's framework for creating AI agents that can use tools and make decisions
> - `openai`: Connects to OpenAI's API for the language model
> - `python-dotenv`: Loads environment variables (like your API keys)
> - `requests` & `requests-oauthlib`: Handles HTTP requests and OAuth authentication
> - `aptos-sdk`: Interfaces with the Aptos blockchain

We are now fully ready to run our AI Agent!

## Part 2: Running Your AI Agent

Your AI Agent has it's own account on Aptos's Devnet which it will use to do things on your behalf on-chain. You can use it to create a new token from scratch, call contracts that you write, or look up what is happening on-chain!

1. Start your agent:
```bash
python main.py
```

You should see:
```
Starting Swarm CLI 🐝
User: 
```

2. Try some test commands such as:

- User: What can you do?

- User: Create a token called "Test Token" with symbol "TEST"

- User: Check my wallet balance

- User: Aptos has great docs! Aptos Docs Token plz.

> [!NOTE]  
> Your agent should respond intelligently to each command, explaining what it's doing and providing blockchain transaction details when relevant. You'll want to check everything deployed correctly using the indexer or explorer. You can exit the conversation with your agent by typing `cmd+z` on Mac.

![Screenshot 2025-01-16 at 2 23 03 PM](https://github.com/user-attachments/assets/11318b9b-4afd-4357-a8ab-93d7e60e9a40)

Let's verify our new token:

3. Visit the [Aptos Explorer](https://explorer.aptoslabs.com/?network=testnet).

4. Switch to "Testnet" network if not already selected.

5. Paste your transaction hash and select it from the dropdown that loads.

6. Click the "Payload" tab to see your token details.

![Screenshot 2025-01-16 at 2 29 27 PM](https://github.com/user-attachments/assets/4ff96e5f-b0f0-45b2-aba1-f9866db3fb71)

## What's Next?

Your AI agent can now:
- Understand and respond to blockchain questions
- Execute Aptos transactions
- Help users interact with the blockchain
- Create and verify tokens on testnet

In the next tutorial, we'll improve the agent with:
- A setup wizard for configuration
- Optional social media features
- Better test mode capabilities

Here are some ideas for next steps:
1. Learn more about Move smart contracts with the [Your First Move Module Guide at aptos.dev](https://aptos.dev/en/build/guides/first-move-module), perhaps build a custom Move modules to interact with?
2. Explore the [Aptos SDK documentation](https://aptos.dev/en/build/sdks), perhaps try building an agent in a different language and contribute to this open source project?
3. Join the [Aptos Discord](https://discord.gg/aptoslabs) to connect with other developers.
4. Let us know you enjoyed this content, tag us and post your experience and thoughts on social media!
