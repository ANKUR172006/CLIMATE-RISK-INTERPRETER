from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path
from typing import Any
from urllib import error, request


def _is_placeholder(value: str) -> bool:
    upper = value.strip().upper()
    return (not upper) or ("PASTE_" in upper) or ("YOUR_" in upper)


def _template_brief(context: dict[str, Any]) -> str:
    model = context.get("best_model", "Unknown")
    rmse = context.get("rmse", None)
    regime = context.get("regime", "Unknown")
    proj_2035 = context.get("p50_2035", None)
    proj_2050 = context.get("p50_2050", None)

    rmse_txt = f"{float(rmse):.3f} C" if rmse is not None else "NA"
    p35_txt = f"{float(proj_2035):.2f} C" if proj_2035 is not None else "NA"
    p50_txt = f"{float(proj_2050):.2f} C" if proj_2050 is not None else "NA"

    urgency = "High" if regime == "High" else ("Elevated" if regime == "Elevated" else "Moderate")

    return (
        f"Fallback brief: Best model is {model} (holdout RMSE {rmse_txt}). "
        f"Final archive regime is {regime}. Illustrative anomaly extrapolation is about {p35_txt} by 2035 "
        f"and {p50_txt} by 2050 versus 1850-1900 baseline. "
        f"Interpret urgency as {urgency}; prioritize heat-health protection, resilient infrastructure, "
        f"and local adaptation planning with uncertainty-aware monitoring."
    )


def _extract_text(resp_json: dict[str, Any]) -> str:
    # Responses API commonly returns output_text; keep fallbacks for schema differences.
    if isinstance(resp_json.get("output_text"), str) and resp_json["output_text"].strip():
        return resp_json["output_text"].strip()

    out = resp_json.get("output", [])
    if isinstance(out, list):
        parts: list[str] = []
        for item in out:
            for content in item.get("content", []):
                txt = content.get("text")
                if isinstance(txt, str) and txt.strip():
                    parts.append(txt.strip())
        if parts:
            return "\n\n".join(parts)

    return ""


def _resolve_api_config() -> tuple[str, str]:
    # Priority: env vars, then Streamlit secrets.
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()

    if not _is_placeholder(api_key) and model:
        return api_key, model
    if not _is_placeholder(api_key) and not model:
        return api_key, "gpt-4o-mini"

    try:
        import streamlit as st

        secret_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
        secret_model = str(st.secrets.get("OPENAI_MODEL", "")).strip()

        # Optional nested format:
        # [openai]
        # api_key = "..."
        # model = "..."
        if not secret_key and "openai" in st.secrets:
            secret_key = str(st.secrets["openai"].get("api_key", "")).strip()
            secret_model = str(st.secrets["openai"].get("model", "")).strip()

        if not _is_placeholder(secret_key):
            return secret_key, secret_model or "gpt-4o-mini"
    except Exception:
        pass

    # Direct file fallback for reliability across runtimes.
    candidate_paths = [
        Path(".streamlit/secrets.toml"),
        Path.home() / ".streamlit" / "secrets.toml",
    ]
    for p in candidate_paths:
        try:
            if not p.exists():
                continue
            raw = p.read_text(encoding="utf-8")
            parsed = tomllib.loads(raw.lstrip("\ufeff"))
            file_key = str(parsed.get("OPENAI_API_KEY", "")).strip()
            file_model = str(parsed.get("OPENAI_MODEL", "")).strip()
            if not file_key and isinstance(parsed.get("openai"), dict):
                openai_obj = parsed["openai"]
                file_key = str(openai_obj.get("api_key", "")).strip()
                file_model = str(openai_obj.get("model", "")).strip()
            if not _is_placeholder(file_key):
                return file_key, file_model or "gpt-4o-mini"
        except Exception:
            continue

    return "", model or "gpt-4o-mini"


def _resolve_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider:
        return provider

    try:
        import streamlit as st

        provider = str(st.secrets.get("LLM_PROVIDER", "")).strip().lower()
        if provider:
            return provider
        if "llm" in st.secrets and isinstance(st.secrets["llm"], dict):
            provider = str(st.secrets["llm"].get("provider", "")).strip().lower()
            if provider:
                return provider
    except Exception:
        pass

    for p in [Path(".streamlit/secrets.toml"), Path.home() / ".streamlit" / "secrets.toml"]:
        try:
            if not p.exists():
                continue
            raw = p.read_text(encoding="utf-8")
            parsed = tomllib.loads(raw.lstrip("\ufeff"))
            provider = str(parsed.get("LLM_PROVIDER", "")).strip().lower()
            if provider:
                return provider
            if isinstance(parsed.get("llm"), dict):
                provider = str(parsed["llm"].get("provider", "")).strip().lower()
                if provider:
                    return provider
        except Exception:
            continue

    return "auto"


def _resolve_gemini_config() -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "").strip() or "gemini-1.5-flash"

    if not _is_placeholder(api_key):
        return api_key, model

    try:
        import streamlit as st

        api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        model = str(st.secrets.get("GEMINI_MODEL", "")).strip() or model
        if not api_key and "gemini" in st.secrets and isinstance(st.secrets["gemini"], dict):
            api_key = str(st.secrets["gemini"].get("api_key", "")).strip()
            model = str(st.secrets["gemini"].get("model", "")).strip() or model
        if not _is_placeholder(api_key):
            return api_key, model
    except Exception:
        pass

    for p in [Path(".streamlit/secrets.toml"), Path.home() / ".streamlit" / "secrets.toml"]:
        try:
            if not p.exists():
                continue
            raw = p.read_text(encoding="utf-8")
            parsed = tomllib.loads(raw.lstrip("\ufeff"))
            api_key = str(parsed.get("GEMINI_API_KEY", "")).strip()
            model = str(parsed.get("GEMINI_MODEL", "")).strip() or model
            if not api_key and isinstance(parsed.get("gemini"), dict):
                api_key = str(parsed["gemini"].get("api_key", "")).strip()
                model = str(parsed["gemini"].get("model", "")).strip() or model
            if not _is_placeholder(api_key):
                return api_key, model
        except Exception:
            continue

    return "", model


def _resolve_openrouter_config() -> tuple[str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip() or "openai/gpt-4o-mini"
    if not _is_placeholder(api_key):
        return api_key, model

    try:
        import streamlit as st

        api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
        model = str(st.secrets.get("OPENROUTER_MODEL", "")).strip() or model
        if not api_key and "openrouter" in st.secrets and isinstance(st.secrets["openrouter"], dict):
            api_key = str(st.secrets["openrouter"].get("api_key", "")).strip()
            model = str(st.secrets["openrouter"].get("model", "")).strip() or model
        if not _is_placeholder(api_key):
            return api_key, model
    except Exception:
        pass

    for p in [Path(".streamlit/secrets.toml"), Path.home() / ".streamlit" / "secrets.toml"]:
        try:
            if not p.exists():
                continue
            raw = p.read_text(encoding="utf-8")
            parsed = tomllib.loads(raw.lstrip("\ufeff"))
            api_key = str(parsed.get("OPENROUTER_API_KEY", "")).strip()
            model = str(parsed.get("OPENROUTER_MODEL", "")).strip() or model
            if not api_key and isinstance(parsed.get("openrouter"), dict):
                api_key = str(parsed["openrouter"].get("api_key", "")).strip()
                model = str(parsed["openrouter"].get("model", "")).strip() or model
            if not _is_placeholder(api_key):
                return api_key, model
        except Exception:
            continue

    return "", model


def _call_openai(system_msg: str, user_payload: dict[str, Any], context: dict[str, Any]) -> tuple[str, str, str]:
    api_key, model = _resolve_api_config()
    if not api_key:
        return _template_brief(context), "fallback", "OPENAI_API_KEY not set (env or Streamlit secrets)"

    body = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_msg}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(user_payload)}],
            },
        ],
        "max_output_tokens": 320,
    }

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=25) as r:
        resp = json.loads(r.read().decode("utf-8"))
    text = _extract_text(resp)
    if text:
        return text, "llm", f"Generated with OpenAI ({model})"
    return _template_brief(context), "fallback", "OpenAI response was empty"


def _call_gemini(system_msg: str, user_payload: dict[str, Any], context: dict[str, Any]) -> tuple[str, str, str]:
    api_key, model = _resolve_gemini_config()
    if not api_key:
        return _template_brief(context), "fallback", "GEMINI_API_KEY not set (env or Streamlit secrets)"

    model = model.strip()
    if model.startswith("models/"):
        model = model.split("/", 1)[1]
    models_to_try = []
    for m in [
        model,
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
    ]:
        if m and m not in models_to_try:
            models_to_try.append(m)

    prompt = (
        f"{system_msg}\n\n"
        f"Input JSON:\n{json.dumps(user_payload)}\n\n"
        "Return only the final brief text."
    )
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 320, "temperature": 0.4},
    }
    last_exc: Exception | None = None
    for model_name in models_to_try:
        endpoints = [
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={api_key}",
        ]
        for url in endpoints:
            try:
                req = request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(req, timeout=25) as r:
                    resp = json.loads(r.read().decode("utf-8"))

                candidates = resp.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    texts = [p.get("text", "").strip() for p in parts if isinstance(p.get("text"), str)]
                    text = "\n\n".join([t for t in texts if t])
                    if text:
                        return text, "llm", f"Generated with Gemini ({model_name})"
            except error.HTTPError as exc:
                last_exc = exc
                if exc.code == 404:
                    continue
                raise
            except Exception as exc:
                last_exc = exc
                continue

    if last_exc is not None:
        raise last_exc
    return _template_brief(context), "fallback", "Gemini response was empty"


def _call_openrouter(system_msg: str, user_payload: dict[str, Any], context: dict[str, Any]) -> tuple[str, str, str]:
    api_key, model = _resolve_openrouter_config()
    if not api_key:
        return _template_brief(context), "fallback", "OPENROUTER_API_KEY not set (env or Streamlit secrets)"

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0.4,
        "max_tokens": 320,
    }

    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=25) as r:
        resp = json.loads(r.read().decode("utf-8"))

    choices = resp.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip(), "llm", f"Generated with OpenRouter ({model})"
        if isinstance(content, list):
            text_parts = [c.get("text", "").strip() for c in content if isinstance(c, dict) and isinstance(c.get("text"), str)]
            merged = "\n\n".join([t for t in text_parts if t])
            if merged:
                return merged, "llm", f"Generated with OpenRouter ({model})"

    return _template_brief(context), "fallback", "OpenRouter response was empty"


def _dispatch_llm(system_msg: str, user_payload: dict[str, Any], context: dict[str, Any]) -> tuple[str, str, str]:
    provider = _resolve_provider()
    try:
        if provider == "gemini":
            return _call_gemini(system_msg, user_payload, context)
        if provider == "openrouter":
            return _call_openrouter(system_msg, user_payload, context)
        if provider == "openai":
            return _call_openai(system_msg, user_payload, context)

        # auto mode: try all configured providers in sequence.
        tried: list[str] = []
        for name, fn in [
            ("openai", _call_openai),
            ("gemini", _call_gemini),
            ("openrouter", _call_openrouter),
        ]:
            tried.append(name)
            try:
                text, mode, note = fn(system_msg, user_payload, context)
                if mode == "llm":
                    return text, mode, note
                # If key missing for that provider, keep trying next one.
                if "not set" in note.lower():
                    continue
                # If provider returned non-empty fallback for other reason, keep it but still try next.
                last_fallback = (text, mode, note)
            except (error.HTTPError, error.URLError, TimeoutError, ValueError):
                continue

        if "last_fallback" in locals():
            return last_fallback
        return _template_brief(context), "fallback", f"LLM unavailable (auto): tried {', '.join(tried)}"
    except (error.HTTPError, error.URLError, TimeoutError, ValueError) as exc:
        return _template_brief(context), "fallback", f"LLM unavailable ({provider}): {exc}"


def generate_genai_brief(
    section_title: str,
    objective: str,
    context: dict[str, Any],
    min_words: int = 90,
    max_words: int = 170,
) -> tuple[str, str, str]:
    system_msg = (
        "You are a climate policy analyst. Write concise, practical outputs for non-technical stakeholders. "
        "Be explicit about uncertainty and avoid deterministic claims."
    )
    user_payload = {
        "task": section_title,
        "objective": objective,
        "context": context,
        "output_constraints": {
            "word_range": f"{min_words}-{max_words}",
            "style": "plain English, 1 short paragraph + 3 action bullets",
        },
    }
    return _dispatch_llm(system_msg, user_payload, context)


def generate_policy_brief(context: dict[str, Any]) -> tuple[str, str, str]:
    system_msg = (
        "You are a climate policy analyst. Produce a concise, plain-English policy brief "
        "for non-technical city/government stakeholders. Be explicit about uncertainty and "
        "avoid deterministic claims. Keep to 120-180 words."
    )

    user_payload = {
        "task": "Generate a policy brief from model outputs",
        "context": context,
        "required_sections": [
            "Archive signal",
            "Near-term risk",
            "Action priorities",
            "Uncertainty note",
        ],
    }
    return _dispatch_llm(system_msg, user_payload, context)

