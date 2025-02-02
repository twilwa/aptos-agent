# Building Your AI-Powered Aptos Agent with Python

The Aptos blockchain allows developers to interact with Move modules (smart contracts) through various SDKs. This tutorial, inspired by [Brian Wong's](https://x.com/briannwongg/status/1867716033659965672) Aptos Agent Template ([on Replit](https://replit.com/@brianwww/Aptos-Agent)), will help you create your own AI-powered blockchain assistant.

You'll learn how to:
1. Set up a Python development environment for blockchain development
2. Create a virtual environment for project dependency management
3. Build an AI agent that can interact with the Aptos blockchain using the Aptos Python SDK
4. Test your agent with real blockchain interactions

> [!NOTE]  
> For Node.js Developers: Throughout this tutorial, we'll provide analogies to Node.js/JavaScript concepts to help you understand Python's approach.

Imagine our Aptos Agent as a new employee at a bank. They need two things to do their job: knowledge of banking procedures (that's our AI's instructions) and access to the actual banking systems (that's our blockchain integration). We'll set up both components step by step.

> [!NOTE]  
> This tutorial is written for Mac / Linux, so Windows users will need to modify some commands.
>
> Asking [ChatGPT](chat.openai.com) for the Windows version can be a quick way to get the right command!

## Part 0: Getting Your OpenAI API Key
To create an AI Agent, you will need an API key for the AI. This agent was written to work with ChatGPT 4o, so before we dive into the details of how to run the agent’s code, you will need to create an OpenAI account. 

> [!NOTE]  
> This will require loading at least $5 into your account, but the actual tutorial should cost only a couple pennies to interact with your AI Agent!

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
