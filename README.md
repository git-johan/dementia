# Learning to Live with Dementia
We are building an AI assistant helping Norwegian families navigate dementia care with confidence.

## Development challenges
* We're starting off with zero "real developers". We are both learning to code in the world of AI. 
* We hope to validate our idea before bringing in "real developers".
* However we both have been working with digital product development, and been farily close to code for 10-15 years
* But we are using AI to write all code
* We have limited code review practices or code review processes in place
* None of us has been responsible for a production environment before
* We want to address these challenges by having a thought through process and implementing best practices for code review and production environments.

## AI first
AI is at the center of our research and development practices. This folder is trying to organize documents and code in a way that allows humans and AI to collaborate efficiently together. Because AI is bad at complex mental models, our idea is to organize the folder structure in a way that makes it easy for AI to understand and navigate small chunks at a time. And for humans to fail fast, learn, get rid off bad ideas (and crap code) and keep only the stuff we need. 

## Project structure
- **company** - Company wide documents, policies, and procedures
- **research** - Research related code projects. This is where the mess lives.
- **development** - Development code. Here we try to keep it clean and organized. We might push pretty far towards our MVP before we start productionizing the code.
- **production** - Production code. Don't know when or how to start productionizing the code. In a perfect world this is done by "real developers" (not fresh developersusing AI), but it may also be required that non-developers contribute to production code. We'll see.

## Company
- Company wide documents, policies, and procedures
- Its main purpose is to keep the team (and AI) focused on the core mission

- **[VISION.md](VISION.md)** - Why we exist and what we're achieving
- **[PRODUCT.md](PRODUCT.md)** - What we're currently building
- **[Research](research/)** - Technical foundation and findings

## Research
- Each project should answer a core question
- Each project should have a README.md file with a brief description and links to relevant resources
- Research code/services is deployed to Railway via separate research branches
- You can (and should) use the development/production APIs as you wish

## Development
- Code should be modular, reusable, and testable
- APIs should be designed to be easily used by research projects
- Development code can be used to prototype new features and test ideas before moving them to production, but code should be reviewed and tested before being merged into the main branch.
- TBD: Git strategy. One repo for development? One repo per service? 

## Production
- TBA. We are using development for the time being.




Services
- Chat
- Memory
- Record
- Transcribe
-
