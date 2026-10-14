"""
Multi-provider LLM client for BharatKart AI Concierge
Supports Groq, OpenRouter, Google Gemini, and template fallback
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client with automatic fallback across providers"""
    
    def __init__(self):
        self.provider = getattr(settings, 'AI_PROVIDER', 'groq')
        self.groq_key = getattr(settings, 'GROQ_API_KEY', '')
        self.openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        self.gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
        
        self.groq_client = None
        self.openrouter_client = None
        self.gemini_model = None
        
        self._init_clients()
    
    def _init_clients(self):
        """Initialize available LLM clients based on available keys"""
        # Groq
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                logger.info("✅ Groq client initialized")
            except ImportError:
                logger.warning("Groq SDK not installed. Run: pip install groq")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}")
        
        # OpenRouter (uses OpenAI SDK compatible endpoint)
        if self.openrouter_key:
            try:
                from openai import OpenAI
                self.openrouter_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_key,
                )
                logger.info("✅ OpenRouter client initialized")
            except ImportError:
                logger.warning("OpenAI SDK not installed. Run: pip install openai")
            except Exception as e:
                logger.warning(f"OpenRouter init failed: {e}")
        
        # Google Gemini
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini client initialized")
            except ImportError:
                logger.warning("Google SDK not installed. Run: pip install google-generativeai")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")
    
    def is_available(self):
        """Check if any LLM provider is available"""
        return bool(self.groq_client or self.openrouter_client or self.gemini_model)
    
    def generate(self, system_prompt, user_message, context='', max_tokens=500):
        """
        Generate a response using the best available provider.
        Returns response text, or None if all providers fail.
        """
        full_prompt = self._build_prompt(system_prompt, context, user_message)
        
        providers = self._get_provider_order()
        
        for provider in providers:
            try:
                if provider == 'groq' and self.groq_client:
                    return self._groq_generate(full_prompt, max_tokens)
                elif provider == 'openrouter' and self.openrouter_client:
                    return self._openrouter_generate(full_prompt, max_tokens)
                elif provider == 'gemini' and self.gemini_model:
                    return self._gemini_generate(full_prompt)
            except Exception as e:
                logger.warning(f"{provider} generation failed: {e}")
                continue
        
        return None
    
    def _get_provider_order(self):
        """Get providers in fallback order"""
        fallback_order = getattr(
            settings, 'AI_FALLBACK_ORDER',
            ['groq', 'openrouter', 'gemini', 'template']
        )
        
        if self.provider not in fallback_order:
            fallback_order = [self.provider] + fallback_order
        
        fallback_order = [self.provider] + [p for p in fallback_order if p != self.provider]
        
        return [p for p in fallback_order if p != 'template']
    
    def _build_prompt(self, system_prompt, context, user_message):
        """Build the full prompt"""
        parts = [system_prompt]
        
        if context:
            parts.append(f"\n\n## RELEVANT CONTEXT:\n{context}")
        
        parts.append(f"\n\n## CUSTOMER QUESTION:\n{user_message}")
        parts.append("\n\n## YOUR RESPONSE:")
        
        return "\n".join(parts)
    
    def _groq_generate(self, prompt, max_tokens):
        """Generate using Groq (Llama models)"""
        response = self.groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are BharatKart's luxury AI concierge. Be warm, helpful, "
                        "and concise. Use markdown for formatting (bold with **text**). "
                        "Keep responses under 150 words unless asked for details."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    
    def _openrouter_generate(self, prompt, max_tokens):
        """Generate using OpenRouter (free models)"""
        response = self.openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are BharatKart's luxury AI concierge. Be warm, helpful, "
                        "and concise. Use markdown for formatting."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    
    def _gemini_generate(self, prompt):
        """Generate using Google Gemini"""
        response = self.gemini_model.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': 500,
                'temperature': 0.7,
            }
        )
        return response.text.strip()


# ============================================================
# SINGLETON
# ============================================================
_llm_client = None


def get_llm_client():
    """Get or create the LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
