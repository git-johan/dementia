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

- **[VISION.md](company/VISION.md)** - Why we exist and what we're achieving
- **[PRODUCT.md](company/PRODUCT.md)** - What we're currently building
- **[Research](research/)** - Technical foundation and findings

## Research
- Each project should answer a core question
- Each project should have a README.md file with a brief description and links to relevant resources
- **Git workflow**: Create research branches (`research/project-name-YYYYMMDD`) for experiments
- **Railway deployment**: Research branches automatically deploy to temporary environments
- **Graduation**: Copy learnings to development folder, rewrite clean code
- You can (and should) use the development/production APIs as you wish

## Development
- Code should be modular, reusable, and testable
- APIs should be designed to be easily used by research projects
- Development code can be used to prototype new features and test ideas before moving them to production, but code should be reviewed and tested before being merged into the main branch.
- **Git strategy**: One repo with clean main branch, copy & rewrite approach from research to development 

## Production
- TBA. We are using development for the time being.

## Git Workflow (AI-Friendly)

### Simple Branch Strategy
- **One main branch**: All clean, working code
- **Research branches**: `research/experiment-name-YYYYMMDD` for AI experiments
- **Feature branches**: `feature/feature-name` for development work

### Research Workflow
1. **Start experiment**: `git checkout -b research/voice-ui-20241120`
2. **AI development**: Work in `research/` folder, crap code allowed
3. **Railway deployment**: Push branch → automatic temporary deployment
4. **Copy & rewrite**: Move learnings to `development/` folder with clean code
5. **Cleanup**: Delete research branch when done

### Quality Gates
- **Research → Development**: Physical folder move requires conscious rewriting
- **Development → Main**: Code review and testing required
- **Main → Production**: Manual deployment when ready

### Railway Integration
- Research branches deploy to temporary environments
- Main branch deploys to development environment
- Automatic cleanup when research branches are deleted
- Environment variables managed through Railway dashboard




Services
- Chat
- Memory
- Record
- Transcribe
-
