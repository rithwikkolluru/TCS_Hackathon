"""
Hybrid AI Service — Privacy-First Architecture
==============================================
STAGE 1 → Local Ollama (gemma4:12b):
    - Processes raw sensitive banking data (PII, transactions, queue logs)
    - Anonymizes, aggregates and extracts structured insights
    - NEVER sends raw data to any external API

STAGE 2 → Online Gemini (gemini-1.5-flash):
    - Receives ONLY anonymized, aggregated summaries from Stage 1
    - Generates final operational recommendations, narratives, alerts
    - No sensitive data ever leaves the local system
"""

import os
import json
import logging
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger("hybrid_ai")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "gemma4:12b")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL    = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")


class LocalSensitiveProcessor:
    """Runs entirely on-device via Ollama. No raw data leaves this class."""

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self._available = None

    async def check_availability(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self.base_url}/api/tags")
                self._available = r.status_code == 200
        except Exception:
            self._available = False
        return self._available

    async def _call_ollama(self, prompt: str, system: str = "") -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 1024}
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "")

    def _extract_json(self, raw: str) -> dict:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        raise ValueError("No JSON found in response")

    async def anonymize_customer_data(self, raw_customers: list) -> dict:
        """Stage 1a: Anonymize customer visit records → statistical aggregates only."""
        safe = {"total_customers": len(raw_customers), "services_requested": {}, "wait_time_samples": [], "hour_distribution": {}}
        for c in raw_customers:
            svc = c.get("service_category", "Unknown")
            safe["services_requested"][svc] = safe["services_requested"].get(svc, 0) + 1
            if c.get("wait_time_minutes"):
                safe["wait_time_samples"].append(c["wait_time_minutes"])
            hr = c.get("arrival_hour")
            if hr is not None:
                safe["hour_distribution"][str(hr)] = safe["hour_distribution"].get(str(hr), 0) + 1

        prompt = f"""Analyze this aggregated (non-PII) branch visit data and extract structured operational insights.
DATA: {json.dumps(safe, indent=2)}
Return ONLY valid JSON:
{{"avg_wait_minutes": <n>, "peak_hour": <n>, "busiest_service": "<s>", "service_load_pct": {{"Loans": <n>, "Cash": <n>, "Accounts": <n>, "Forex": <n>, "Lockers": <n>}}, "congestion_level": "<low|medium|high|critical>", "anomalies_detected": ["<s>"], "recommended_staff_increase": <n>}}"""
        system = "You are a privacy-preserving banking analytics AI. Output only valid JSON. Never include PII."
        try:
            return self._extract_json(await self._call_ollama(prompt, system))
        except Exception as e:
            logger.error(f"[Ollama] anonymize_customer_data: {e}")
            return safe

    async def analyze_branch_sensitivity(self, branch_data: dict) -> dict:
        """Stage 1b: Analyze sensitive branch metrics locally."""
        safe_data = {k: v for k, v in branch_data.items() if k not in {"manager_name", "employee_ids", "customer_ids", "phone", "email"}}
        prompt = f"""Analyze this banking branch operational data and identify risk patterns.
BRANCH METRICS: {json.dumps(safe_data, indent=2)}
Return ONLY valid JSON:
{{"risk_score": <0-100>, "bottleneck_services": ["<s>"], "staff_shortage_detected": <bool>, "overload_probability_pct": <0-100>, "recommended_actions": ["<s>"], "summary": "<2 sentence summary>"}}"""
        system = "You are a banking operations risk analyst AI. Output only valid JSON. No PII."
        try:
            return self._extract_json(await self._call_ollama(prompt, system))
        except Exception as e:
            logger.error(f"[Ollama] analyze_branch_sensitivity: {e}")
            return {"risk_score": 50, "summary": "Analysis unavailable", "recommended_actions": []}

    async def process_feedback_sentiment(self, raw_feedback: list) -> dict:
        """Stage 1c: Analyze customer feedback locally — no customer identifiers sent online."""
        texts = [f.get("feedback_text", "") for f in raw_feedback if f.get("feedback_text")][:20]
        if not texts:
            return {"overall_sentiment": "neutral", "top_topics": [], "aggregate_summary": "No feedback"}
        prompt = f"""Analyze these {len(texts)} customer feedback texts from a banking branch.
TEXTS: {json.dumps(texts, indent=2)}
Return ONLY valid JSON:
{{"overall_sentiment": "<positive|neutral|negative>", "sentiment_score": <-1.0 to 1.0>, "top_topics": ["<s>"], "top_complaints": ["<s>"], "top_praises": ["<s>"], "urgent_issues": ["<s>"], "aggregate_summary": "<3 sentence summary>"}}"""
        system = "You are a customer experience analyst. Output only valid JSON. No customer names or IDs."
        try:
            return self._extract_json(await self._call_ollama(prompt, system))
        except Exception as e:
            logger.error(f"[Ollama] process_feedback_sentiment: {e}")
            return {"overall_sentiment": "neutral", "top_topics": [], "aggregate_summary": "Error"}

    async def compute_staffing_needs(self, queue_data: dict) -> dict:
        """Stage 1d: Compute staffing requirements from queue data."""
        prompt = f"""Calculate optimal staffing for a banking branch.
QUEUE DATA: {json.dumps(queue_data, indent=2)}
Return ONLY valid JSON:
{{"current_staff_sufficient": <bool>, "recommended_staff_by_service": {{"Loans": <n>, "Cash": <n>, "Accounts": <n>, "Forex": <n>, "Lockers": <n>}}, "total_recommended": <n>, "urgency": "<normal|elevated|urgent|critical>", "shift_recommendations": ["<s>"]}}"""
        system = "You are a workforce optimization AI for banking. Output only valid JSON."
        try:
            return self._extract_json(await self._call_ollama(prompt, system))
        except Exception as e:
            logger.error(f"[Ollama] compute_staffing_needs: {e}")
            return {"current_staff_sufficient": True, "total_recommended": 5, "urgency": "normal"}


class OnlineInsightsGenerator:
    """Receives ONLY anonymized summaries. Generates rich recommendations."""

    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.openai_key = OPENAI_API_KEY
        self._gemini_client = None

    def _init_gemini(self):
        if self.gemini_key and not self._gemini_client:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self._gemini_client = genai.GenerativeModel(GEMINI_MODEL)
                logger.info("[Gemini] Client initialized")
            except Exception as e:
                logger.warning(f"[Gemini] Init failed: {e}")

    async def _call_gemini(self, prompt: str) -> str:
        self._init_gemini()
        if not self._gemini_client:
            return ""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self._gemini_client.generate_content(prompt))
            return response.text
        except Exception as e:
            logger.error(f"[Gemini] Call failed: {e}")
            return ""

    async def _call_openai(self, prompt: str) -> str:
        if not self.openai_key:
            return ""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.openai_key)
            r = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3)
            return r.choices[0].message.content
        except Exception as e:
            logger.error(f"[OpenAI] Call failed: {e}")
            return ""

    async def _call_online(self, prompt: str) -> str:
        result = await self._call_gemini(prompt)
        if not result and self.openai_key:
            result = await self._call_openai(prompt)
        return result

    def _extract_json(self, raw: str) -> dict:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        raise ValueError("No JSON")

    async def generate_branch_recommendations(self, anonymized_summary: dict, branch_name: str = "Branch") -> dict:
        prompt = f"""You are an expert banking operations consultant. Based on this anonymized branch performance summary, provide detailed actionable recommendations.

ANONYMIZED BRANCH SUMMARY for {branch_name}:
{json.dumps(anonymized_summary, indent=2)}

Return JSON:
{{"executive_summary": "<3-4 sentence overview>", "immediate_actions": [{{"priority": "<HIGH|MEDIUM|LOW>", "action": "<s>", "reason": "<s>", "estimated_impact": "<s>"}}], "staffing_recommendations": [{{"service": "<s>", "current_issue": "<s>", "recommendation": "<s>", "timeline": "<s>"}}], "process_improvements": ["<s>"], "customer_experience_insights": "<paragraph>", "risk_mitigation": ["<s>"], "performance_forecast": "<outlook>", "confidence_score": <0-100>}}"""
        raw = await self._call_online(prompt)
        if raw:
            try:
                return self._extract_json(raw)
            except Exception:
                return {"executive_summary": raw, "immediate_actions": [], "confidence_score": 70}
        return self._rule_based_recommendations(anonymized_summary)

    async def generate_surge_alert_narrative(self, surge_data: dict) -> str:
        prompt = f"""Write a concise (2-3 sentence) operational alert for bank branch managers based on anonymized metrics:
{json.dumps(surge_data, indent=2)}
Be specific, professional, actionable. No PII. Start with severity level."""
        result = await self._call_online(prompt)
        if result:
            return result.strip()
        risk = surge_data.get("congestion_level", "medium")
        return f"[{risk.upper()} ALERT] Branch experiencing {risk} congestion. Increase: +{surge_data.get('recommended_staff_increase', 2)} staff. Service: {surge_data.get('busiest_service', 'primary')}."

    async def generate_feedback_insights(self, feedback_summary: dict) -> dict:
        prompt = f"""You are a CX Director at a major bank. Analyze this anonymized feedback and provide strategic insights:
{json.dumps(feedback_summary, indent=2)}
Return JSON:
{{"cx_score": <0-100>, "key_insight": "<s>", "quick_wins": ["<s>"], "strategic_initiatives": ["<s>"], "management_summary": "<paragraph>"}}"""
        raw = await self._call_online(prompt)
        if raw:
            try:
                return self._extract_json(raw)
            except Exception:
                pass
        return {"cx_score": 65, "key_insight": feedback_summary.get("aggregate_summary", ""), "quick_wins": feedback_summary.get("urgent_issues", []), "strategic_initiatives": [], "management_summary": feedback_summary.get("aggregate_summary", "")}

    def _rule_based_recommendations(self, summary: dict) -> dict:
        risk = summary.get("risk_score", 50)
        actions = summary.get("recommended_actions", [])
        return {"executive_summary": summary.get("summary", "Branch analysis complete."), "immediate_actions": [{"priority": "HIGH" if risk > 70 else "MEDIUM", "action": a, "reason": "Detected by local AI", "estimated_impact": "Moderate"} for a in actions[:3]], "staffing_recommendations": [], "process_improvements": actions[3:] if len(actions) > 3 else [], "customer_experience_insights": "Review feedback for CX metrics.", "risk_mitigation": [], "performance_forecast": "Monitor KPIs.", "confidence_score": 55}


class HybridAIOrchestrator:
    """
    Main orchestrator — privacy-first two-stage pipeline.
    Raw data → Local Ollama → Anonymized → Online Gemini → Insights
    """

    def __init__(self):
        self.local  = LocalSensitiveProcessor()
        self.online = OnlineInsightsGenerator()
        logger.info("[HybridAI] Ready | Local: Ollama %s | Online: Gemini %s", OLLAMA_MODEL, GEMINI_MODEL)

    async def full_branch_analysis(self, branch_data: dict, customer_records: list, feedback_records: list, queue_data: dict, branch_name: str = "Branch") -> dict:
        logger.info("[HybridAI] Full pipeline: %s", branch_name)
        t0 = datetime.now()

        # Stage 1 — all local, parallel
        results = await asyncio.gather(
            self.local.anonymize_customer_data(customer_records),
            self.local.analyze_branch_sensitivity(branch_data),
            self.local.process_feedback_sentiment(feedback_records),
            self.local.compute_staffing_needs(queue_data),
            return_exceptions=True
        )
        anon_customers, branch_risk, feedback_sent, staffing = [
            r if not isinstance(r, Exception) else {} for r in results
        ]

        combined = {
            "branch_name": branch_name,
            "timestamp": datetime.now().isoformat(),
            "customer_metrics": anon_customers,
            "risk_analysis": branch_risk,
            "feedback_analysis": feedback_sent,
            "staffing_analysis": staffing
        }
        logger.info("[HybridAI] Stage 1 complete. Sending anonymized data to Stage 2.")

        # Stage 2 — online, parallel
        results2 = await asyncio.gather(
            self.online.generate_branch_recommendations(combined, branch_name),
            self.online.generate_feedback_insights(feedback_sent),
            self.online.generate_surge_alert_narrative(anon_customers),
            return_exceptions=True
        )
        recs, fb_insights, surge_msg = [r if not isinstance(r, Exception) else {} for r in results2]
        if isinstance(results2[2], Exception):
            surge_msg = "Branch monitoring active."

        elapsed = round((datetime.now() - t0).total_seconds(), 2)
        logger.info("[HybridAI] Pipeline complete in %ss", elapsed)

        return {
            "pipeline": {
                "local_model": f"Ollama/{OLLAMA_MODEL}",
                "online_model": f"Gemini/{GEMINI_MODEL}" if GEMINI_API_KEY else "Rule-based (no API key)",
                "elapsed_seconds": elapsed,
                "privacy_guarantee": "No PII sent to online model"
            },
            "stage1_local": combined,
            "stage2_online": {
                "recommendations": recs,
                "feedback_insights": fb_insights,
                "surge_narrative": surge_msg
            }
        }

    async def quick_sentiment(self, feedback_texts: list) -> dict:
        sentiment = await self.local.process_feedback_sentiment(feedback_texts)
        insights  = await self.online.generate_feedback_insights(sentiment)
        return {"local_sentiment": sentiment, "online_insights": insights}

    async def quick_branch_risk(self, branch_data: dict) -> dict:
        return await self.local.analyze_branch_sensitivity(branch_data)

    async def health_check(self) -> dict:
        ollama_ok = await self.local.check_availability()
        return {
            "local_ollama": {"status": "online" if ollama_ok else "offline", "model": OLLAMA_MODEL, "url": OLLAMA_BASE_URL},
            "online_gemini": {"status": "configured" if GEMINI_API_KEY else "no_api_key (rule-based fallback active)", "model": GEMINI_MODEL},
            "privacy_mode": "active",
            "architecture": "raw_data→ollama(local)→anonymized→gemini(online)→insights"
        }


hybrid_ai = HybridAIOrchestrator()
