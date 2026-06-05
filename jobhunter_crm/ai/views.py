"""AI management views."""

import json
import re

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from companies.models import Company
from logs_app.models import ActivityLog


def _check_company_with_groq(company_name: str) -> dict:
    """
    Ask Groq to analyze a company and return structured info.

    Returns dict with keys:
      is_real     (bool)   — does this company actually exist?
      company_type (str)   — IT, Fintech, Bank, etc.
      description  (str)   — what does the company do (2-3 sentences)
      is_top       (bool)  — is it a well-known / top company?
    """
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""You are analyzing companies from Uzbekistan's job market. Respond ONLY with valid JSON.

Company name: "{company_name}"

Context: This name came from a job vacancy in Uzbekistan. Many companies are Uzbek, Russian, or international firms operating in Uzbekistan.

Well-known Uzbek/CIS companies (always is_real=true, is_top=true):
Uzum, Payme, Click, Humans, Beeline Uzbekistan, Ucell, MTS Uzbekistan,
Kapitalbank, Hamkorbank, Ipoteka Bank, Agrobank, TBC Bank, Aloqabank,
EPAM, Artel, Goodzone, MyID, UzCard, Humo, Zood, Aliif, Davr Bank,
Yandex, Google, Microsoft, Samsung, LG, Najot Talim, PDP Academy.

Return ONLY this JSON:
{{
  "is_real": true,
  "company_type": "IT Company",
  "description": "2-3 sentences about what this company does.",
  "is_top": false
}}

Rules:
- is_real=false ONLY if: random letters/numbers, clearly a fake name, or a person's full name (e.g. "Иванов Иван Иванович")
- is_real=true for any plausible business/organization name, even if unknown — give benefit of doubt
- company_type: IT Company | Education Center | Fintech | E-commerce | Bank | Telecom | Startup | Outsource | Media | Government | Manufacturing | Retail | Other
- description: in Russian or English (whichever fits), 2-3 sentences about the company's main activities
- is_top=true if the company is in this list OR globally well-known:
  Uzum, Uzum Market, Payme, Click, Humans, Beeline, Ucell, MTS,
  Kapitalbank, TBC, EPAM, Artel, Goodzone, MyID, Yandex, Google,
  Microsoft, Amazon, Meta, Apple, Samsung, PDP, Najot Talim"""

    resp = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a company analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        model=settings.GROQ_MODEL,
        temperature=0.1,
        max_tokens=300,
    )

    raw = resp.choices[0].message.content.strip()

    # Extract JSON from response (remove markdown fences if any)
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group()

    return json.loads(raw)


@login_required(login_url='core:login')
def ai_dashboard(request):
    companies = Company.objects.filter(checked_by_ai=False).order_by('-created_at')[:30]
    checked   = Company.objects.filter(checked_by_ai=True).order_by('-updated_at')[:15]
    fake      = Company.objects.filter(checked_by_ai=True, is_real=False).count()
    top_count = Company.objects.filter(is_top=True).count()

    return render(request, 'ai/index.html', {
        'companies':  companies,
        'checked':    checked,
        'fake_count': fake,
        'top_count':  top_count,
        'ai_enabled': settings.AI_COMPANY_CHECK_ENABLED,
        'groq_key':   bool(settings.GROQ_API_KEY),
        'groq_model': settings.GROQ_MODEL,
    })


@login_required(login_url='core:login')
def check_company(request):
    """Check a single company with Groq AI."""
    company_id = request.POST.get('company_id')
    if not company_id:
        return redirect('ai:index')

    company = Company.objects.filter(id=company_id).first()
    if not company:
        return redirect('ai:index')

    try:
        result = _check_company_with_groq(company.name)

        company.is_real      = result.get('is_real', True)
        company.company_type = result.get('company_type', 'Other')
        company.description  = result.get('description', '')
        company.is_top       = result.get('is_top', False)
        company.checked_by_ai = True
        company.save()

        status = "TOP " if company.is_top else ""
        real   = "" if company.is_real else " [SOXTA]"
        ActivityLog.objects.create(
            level='success', source='ai',
            message=f"AI: {company.name} → {status}{company.company_type}{real}"
        )
        messages.success(request, f"{company.name} — {company.company_type}{real}")

    except json.JSONDecodeError as e:
        ActivityLog.objects.create(
            level='error', source='ai',
            message=f"AI JSON parse error for '{company.name}': {e}"
        )
        messages.error(request, f"AI javobi noto'g'ri formatda: {e}")
    except Exception as e:
        ActivityLog.objects.create(
            level='error', source='ai',
            message=f"AI xatolik '{company.name}': {e}"
        )
        messages.error(request, f"Xatolik: {e}")

    return redirect('ai:index')


@login_required(login_url='core:login')
def check_all_companies(request):
    """Check all unchecked companies in batch."""
    if request.method != 'POST':
        return redirect('ai:index')

    companies = Company.objects.filter(checked_by_ai=False)[:20]
    ok, failed = 0, 0

    for company in companies:
        try:
            result = _check_company_with_groq(company.name)
            company.is_real      = result.get('is_real', True)
            company.company_type = result.get('company_type', 'Other')
            company.description  = result.get('description', '')
            company.is_top       = result.get('is_top', False)
            company.checked_by_ai = True
            company.save()
            ok += 1
        except Exception:
            failed += 1

    ActivityLog.objects.create(
        level='success', source='ai',
        message=f"Batch AI check: {ok} muvaffaqiyatli, {failed} xatolik"
    )
    messages.success(request, f"{ok} ta kompaniya tekshirildi, {failed} xatolik.")
    return redirect('ai:index')
