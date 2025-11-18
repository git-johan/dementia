Sure thing — here’s the nuanced conclusion in clean markdown.

⸻

🎯 Nuanced Conclusion for Your Dementia Caregiver Assistant

1. Core conversations → Frontier LLMs (OpenAI) are the right choice for now

For a dementia caregiver assistant that must be empathetic, trustworthy, and stable, today’s frontier commercial models (like OpenAI’s) are the best option.
	•	They handle messy, emotional, real-world conversations much better than open models.
	•	They are more consistent in tone and less likely to hallucinate dangerously.
	•	No self-hosted / open-source model you can realistically run as a solo dev in 2025 comes close for this specific use case.

✅ Conclusion: Use OpenAI (or similar frontier model) as the core conversational brain.

⸻

2. Self-hosted LLMs don’t make sense yet at your scale

You’re aiming for up to 10 000 users with a price cap of 200 kr/month per user.

Self-hosting the main LLM would mean:
	•	Managing GPUs, uptime, scaling, security, monitoring
	•	Doing your own fine-tuning, safety, and alignment
	•	Taking on MLOps work that distracts from building the product

And even after all that, you’d still have worse conversation quality than a good commercial API.

✅ Conclusion: At your scale and timeline, self-hosting the main LLM is not worth it.

⸻

3. Open-source models are useful — just not as the main “soul” of the assistant (yet)

Open-source models (Llama, Mistral, Qwen, NB-llama, etc.) are:
	•	Improving quickly
	•	Great for classification, tagging, embeddings, utilities
	•	Potentially good enough for narrow tasks or internal tools

But as the primary conversational partner for exhausted, stressed caregivers in Norwegian:
	•	They’re still less empathetic, less stable, and more error-prone than frontier models.

✅ Conclusion: Use open-source models around the edges, not as the main companion.

⸻

4. On-device models are not ready to be the main assistant

On-device models (tiny, quantized, 1–3B parameter models):
	•	Are fine for simple offline tasks
	•	But cannot yet reliably deliver:
	•	deep, emotionally aware conversation
	•	long context
	•	nuanced Norwegian caregiver support

✅ Conclusion: On-device models can be optional helpers, but not the core brain.

⸻

5. Privacy & GDPR → Cloud LLM + local pre/post-processing is the sweet spot

You can get a strong privacy story by combining:
	•	Cloud LLM (OpenAI / similar):
	•	EU region
	•	DPA in place
	•	No training on your data
	•	Minimal, pseudonymised text only

with:
	•	Local or controlled processing for sensitive media:
	•	ASR (e.g. nb-whisper, if/when you self-host)
	•	TTS (local or EU-only provider)
	•	OCR (local or EU-only provider)
	•	Your own storage, encryption, deletion policies

✅ Conclusion: Let the LLM do text-only reasoning, and keep voice, images, and raw documents mostly under your control.

⸻

6. Short-term vs long-term strategy

Now / MVP / first 100–1 000 users:
	•	Use OpenAI (or similar) for all core conversations.
	•	Use simple APIs for ASR/TTS/OCR (OpenAI Whisper, Google TTS, Google/AWS OCR, etc.).
	•	Wrap each external service behind a clean interface so they are easy to swap later.

Later / when you scale or partners demand stricter controls:
	•	Gradually replace:
	•	ASR → self-hosted nb-whisper
	•	TTS → self-hosted Piper/Coqui
	•	OCR → self-hosted Tesseract/PaddleOCR
	•	Re-evaluate open-source LLMs:
	•	Maybe use them for certain flows or as a cheaper fallback
	•	Keep OpenAI (or equivalent) for the most sensitive and complex conversations, until/if open models truly catch up.

⸻

🧵 One-sentence summary

For a Norwegian dementia caregiver assistant in 2025, the pragmatic choice is to use a frontier commercial LLM (like OpenAI) as the core conversational brain for empathy and safety, keep audio/images and other high-sensitivity processing as local or controlled as is reasonable, and design the system so you can gradually replace external APIs with self-hosted components as your scale, regulations, or partners’ requirements evolve.
