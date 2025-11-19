[x] How do we manage privacy in the world of AI?
  * Important because data privacy in health care is a very hot topic and we are required to have good answers
  * Answer: We are adopting a pragmatic GDPR compliance approach that accepts US-based technology companies with EU hosting and Data Processing Agreements (DPAs) as sufficient for our dementia care assistant. If these solutions are good enough for the Norwegian government and public sector, they are good enough for our product. The alternative would be to self host AI models. This would significantly reduce the quality of the service while also slowing down development and/or increasing costs early on substantially.
  * Detailed report in 2025-11-18-pragmatic-gdpr-compliance.md
[x] How can we get audio into the assistant context?
  * Important because a lot of care happens in dialogue, and writing that into the assistant memory manually isn't feasible
  * Answer:
    * We can use either self-hosted `nb-whisperer` which has great norwegian support, or `openai-whisper` for speech to text (STT).
    * We haven't done any sound quality analysis of how to record audio. The assumption is that the microphone on modern smartphones are sufficient.
    * The `nb-whisperer` medium model seems to be the best quality/size trade-off
    * But `nb-whisperer` isnt available through cloud services so we should probably test `openai-whisper` properly since it will save us a lot of time and development costs if that is good enough.
[ ] How good is `openai-whisper` compared to `nb-whisperer`?
  [ ] Does open-ai offer GDPR compliant services for STT?
    * Important because if they don't we cant use open-ai anyway.
  * Important because nb-whisperer requires us to host the AI model. It would be a lot cheaper to use open-ai for this
[ ] Can modern smartphones record audio with high enough quality for accurate transcriptions?
  * Important because if they can't offering audio recordings becomes exponentially harder.
[ ] How do we make sure the AI-assistant references only trusted sources when patients ask questions that require safe and trusted sources?
  * Important because its the essence of what we're making. If we're not able to deliver on that, our core idea is challenged fundamentally
[ ] How do we build long term memory and short term memory?
  * Important because without it we'll run out of context, it will be expensive and really bad
[ ] What does it take to support BankID authentication?
  * Important because we need to ensure secure and reliable authentication for our users.
