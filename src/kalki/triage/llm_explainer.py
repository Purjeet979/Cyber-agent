import os
import json
import urllib.request
import urllib.error
import time
import logging
import ssl
import certifi
from typing import Optional

logger = logging.getLogger(__name__)

class LLMExplainer:
    _last_call_time = 0.0
    _min_interval = 2.0  # 30 requests per minute to stay under 8000 TPM limit

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.enabled = bool(self.api_key)

    def _wait_for_rate_limit(self):
        now = time.time()
        elapsed = now - self.__class__._last_call_time
        if elapsed < self.__class__._min_interval:
            time.sleep(self.__class__._min_interval - elapsed)
        self.__class__._last_call_time = time.time()

    def explain(self, alert_text: str, rule_based_reason: str, mitre_technique: str) -> str:
        if not self.enabled:
            logger.debug("LLM call failed: disabled (no API key)")
            return rule_based_reason
            
        prompt = f"Log: {alert_text}\nDetected technique: {mitre_technique}\nRule match: {rule_based_reason}\nExplain this security event in 2-3 sentences for a SOC analyst."
        
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({
                "model": "qwen/qwen3.8-27b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150
            }).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Kalki/1.0"
            }
        )
        
        ctx = ssl.create_default_context(cafile=certifi.where())
        
        for attempt in range(2):
            self._wait_for_rate_limit()
            try:
                with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                    res = json.loads(response.read().decode())
                    logger.debug("LLM call succeeded")
                    return res["choices"][0]["message"]["content"].strip()
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt == 0:
                    logger.warning("LLM call got 429 Too Many Requests. Retrying...")
                    time.sleep(2.0)  # Backoff before retry
                    continue
                logger.error(f"LLM call failed: {e}")
                break
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                break
                
        return rule_based_reason
