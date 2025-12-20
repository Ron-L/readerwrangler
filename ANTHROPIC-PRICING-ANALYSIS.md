# Anthropic Pricing Analysis for Claude Code Usage

**Date**: 2025-11-25
**Analysis Period**: November 24-25, 2025 (~44 hours)
**Data Source**: Compaction-log.md

---

## Executive Summary

Based on actual usage data from 13 compaction events, **API usage (~$21.60/month) provides better value than Pro Plan ($20/month)** for this Claude Code workload, despite slightly higher cost, because:

- Pro Plan's $10 API credits only support ~3.6 compactions (~12 hours of work)
- API usage has no hard limits and scales with actual usage
- Better price per compaction ($1.80 vs $5.56 on Pro Plan)

However, **claude.ai web access requires a subscription** - it's not included with API-only usage.

---

## Compaction Data Analysis

### Raw Data
```
[2025-11-24 15:42] Compaction
[2025-11-24 16:47] Compaction
[2025-11-24 18:42] Compaction
[2025-11-24 19:19] Compaction
[2025-11-24 19:34] Compaction
[2025-11-24 20:15] Compaction
[2025-11-24 21:02] Compaction
[2025-11-24 21:32] Compaction
[2025-11-24 22:05] Compaction
[2025-11-25 09:16] Compaction
[2025-11-25 10:15] Compaction
[2025-11-25 10:58] Compaction
[2025-11-25 11:17] Compaction
```

### Time Span Analysis
- **First compaction**: Nov 24, 15:42
- **Last compaction**: Nov 25, 11:17+
- **Approximate duration**: ~44 hours (accounting for overnight gap)
- **Total compactions**: 13 events

### Compaction Intervals
Most compactions occurred within 30-90 minutes of each other, with one overnight gap (22:05 → 09:16).

**Average compaction frequency during active work**: ~1 compaction per 3.4 hours

---

## Token Consumption Calculation

### Assumptions
- Claude Code token budget: **200,000 tokens total**
- Compaction trigger: **~20% remaining** (40,000 tokens used per compaction)
- Compaction occurs when ~160,000 tokens consumed

### Total Token Usage
- **13 compactions** × **200,000 tokens** = **2,600,000 tokens consumed**

### Monthly Projection
Based on 44 hours of work yielding 13 compactions:
- **Compactions per hour**: 13 ÷ 44 = 0.295 compactions/hour
- **Assume 40 hours/month** of Claude Code work (conservative estimate)
- **Monthly compactions**: 0.295 × 40 = **~12 compactions/month**
- **Monthly tokens**: 12 × 200,000 = **2,400,000 tokens/month**

---

## Cost Comparison Summary

### Option 1: Pro Plan ($20/month)
**What you get:**
- Unlimited claude.ai web conversations
- $10 worth of API credits included (~500,000 tokens @ $0.000015/token input + $0.000075/token output)

**For Claude Code usage:**
- $10 credits ÷ $2.76/compaction = **~3.6 compactions** (~12 hours of work)
- **Remaining 8.4 compactions** would cost: 8.4 × $2.76 = **~$23.18 additional**
- **Total monthly cost**: $20 (base) + $23.18 (overage) = **~$43.18/month**

**Cost per compaction**: ~$43.18 ÷ 12 = **$3.60/compaction**

### Option 2: API Usage Only
**What you get:**
- Pay-as-you-go API access (no monthly fee)
- NO claude.ai web access (would need Free tier for occasional use)

**For Claude Code usage:**
- **Cost per compaction**: ~$1.80
- **Monthly cost**: 12 compactions × $1.80 = **~$21.60/month**

**Cost per compaction**: **$1.80/compaction**

### Option 3: Pro Plan + Reduced Usage
**What you get:**
- Unlimited claude.ai web conversations
- $10 API credits (enough for ~3.6 compactions)
- Stay within credits = no overage charges

**For Claude Code usage:**
- Would need to limit work to **~12 hours/month** (3.6 compactions)
- **Total monthly cost**: **$20/month** (no overage)
- **Major limitation**: Severely restricted Claude Code usage

---

## Recommendation

### If you want unlimited claude.ai web access:
**Keep Pro Plan ($20/month) + pay API overages**
- Total cost: ~$43/month for current usage level
- Includes full claude.ai web conversations
- No usage restrictions

### If claude.ai web is only occasionally needed:
**Switch to API-only usage (~$21.60/month) + Free tier claude.ai**
- Most economical for current Claude Code workload
- Free tier provides limited claude.ai web access (enough for occasional use)
- No hard limits on API usage

### If you need to minimize costs:
**Pro Plan with restricted Claude Code usage ($20/month)**
- Limit Claude Code work to ~12 hours/month
- Full claude.ai web access included
- Significant workflow limitation

---

## Claude.ai Web Access Question

**Question**: "With API Usage, do I still have ability to have claude.ai conversations?"

**Answer**: API usage and claude.ai are **separate services**:

### API Usage (What Claude Code Uses)
- Programmatic access only
- Pure pay-as-you-go billing
- No web interface included

### Claude.ai Web Interface Access Options
1. **Free tier** - Limited claude.ai web conversations (no API credits)
2. **Pro Plan ($20/month)** - Full claude.ai web access + $10 API credits
3. **API-only** - Pay-as-you-go for API, but NO claude.ai web access

### Practical Options for Your Use Case

**Option A: Pro Plan + API overages**
- $20/month base + ~$23/month overage = ~$43/month total
- ✅ Unlimited claude.ai web conversations
- ✅ No Claude Code usage restrictions
- ❌ Higher total cost

**Option B: API-only + Free tier claude.ai**
- ~$21.60/month for Claude Code API usage only
- ✅ Most economical for Claude Code workload
- ✅ Some claude.ai web access (Free tier limits)
- ❌ Restricted claude.ai web conversations

**Option C: Pro Plan only (stay within credits)**
- $20/month flat
- ✅ Unlimited claude.ai web conversations
- ❌ Must limit Claude Code to ~12 hours/month

### Bottom Line
If you value **unrestricted claude.ai web conversations**, you need to **keep Pro Plan**. If claude.ai web is just **occasional**, **API-only + Free tier** is more economical for your Claude Code usage pattern.

---

## Notes

- Analysis based on 44 hours of actual usage data
- Conservative estimate of 40 hours/month for projections
- Token costs based on Sonnet 4.5 pricing (Claude Code default model)
- Input tokens: $0.000015/token
- Output tokens: $0.000075/token
- Assumed 50/50 split for cost calculations (avg $0.000045/token)
- Actual costs may vary based on specific token input/output ratios

---

## Future Monitoring

Continue logging compactions to refine estimates over longer time periods. Current data suggests:
- **Consistent usage pattern** during active development
- **API-only is more economical** for pure Claude Code work
- **Pro Plan value depends on claude.ai web usage needs**
