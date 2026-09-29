/**
 * Deep Question — Client-Side Diagnostic & Scoring Engine
 * 
 * Standalone calculation engine to evaluate questionnaire submissions,
 * calculate a 0-100 risk score, match recommended insurance plans,
 * lookup coverage tiers, and extract the personalized vulnerability gap.
 * 
 * Can be used in:
 * - Browser (vanilla script tag -> window.DeepQuestionScoringEngine)
 * - Node.js / CommonJS (module.exports)
 * - ES Module (export default)
 */

(function (root, factory) {
  'use strict';
  var lib = factory();
  if (typeof define === 'function' && define.amd) {
    define([], function () { return lib; });
  }
  if (typeof module === 'object' && module.exports) {
    module.exports = lib;
  }
  if (typeof root !== 'undefined') {
    root.DeepQuestionScoringEngine = lib;
  }
  if (typeof window !== 'undefined') {
    window.DeepQuestionScoringEngine = lib;
  }
  if (typeof global !== 'undefined') {
    global.DeepQuestionScoringEngine = lib;
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /**
   * Helper: Normalize selected answers to an array of option IDs.
   * Supports:
   *   - Array of strings: ['Q1_A', 'Q2_B']
   *   - Object map: { Q1: 'Q1_A', Q2: 'Q2_B' }
   *   - Array of option objects: [{ option_id: 'Q1_A' }, ...]
   */
  function normalizeSelectedOptionIds(selectedAnswers) {
    if (!selectedAnswers) return [];
    if (Array.isArray(selectedAnswers)) {
      return selectedAnswers.map(item => {
        if (typeof item === 'string') return item;
        if (item && item.option_id) return item.option_id;
        return null;
      }).filter(Boolean);
    }
    if (typeof selectedAnswers === 'object') {
      return Object.values(selectedAnswers).map(val => {
        if (typeof val === 'string') return val;
        if (val && val.option_id) return val.option_id;
        return null;
      }).filter(Boolean);
    }
    return [];
  }

  /**
   * Helper: Map option IDs to their actual Option schema objects from catalog questions.
   */
  function resolveSelectedOptions(catalog, optionIds) {
    const idSet = new Set(optionIds);
    const resolved = [];

    if (!catalog || !Array.isArray(catalog.questions)) {
      return resolved;
    }

    for (const q of catalog.questions) {
      if (Array.isArray(q.options)) {
        for (const opt of q.options) {
          if (idSet.has(opt.option_id)) {
            resolved.push({
              question: q,
              option: opt
            });
          }
        }
      }
    }
    return resolved;
  }

  /**
   * Standard Coverage and Premium Tiers mapped from user's budget answer.
   * Based on source_option in base_questionnaire:
   *   - '<10,000'
   *   - '10,000-20,000'
   *   - '20,000-30,000'
   *   - '>30,000'
   */
  const DEFAULT_BUDGET_TIERS = {
    '<10,000': {
      budget_tier: '<10,000',
      recommended_sum_insured: '฿250,000',
      sum_insured_range: 'วงเงิน ฿100,000–500,000',
      estimated_monthly_premium: '฿360 / เดือน',
      premium_disclaimer: 'ประมาณการ ยังไม่ใช่เบี้ยจริง'
    },
    '10,000-20,000': {
      budget_tier: '10,000-20,000',
      recommended_sum_insured: '฿500,000',
      sum_insured_range: 'วงเงิน ฿500,000–1,000,000',
      estimated_monthly_premium: '฿1,150 / เดือน',
      premium_disclaimer: 'ประมาณการ ยังไม่ใช่เบี้ยจริง'
    },
    '20,000-30,000': {
      budget_tier: '20,000-30,000',
      recommended_sum_insured: '฿1,000,000',
      sum_insured_range: 'วงเงิน ฿1,000,000–2,000,000',
      estimated_monthly_premium: '฿2,100 / เดือน',
      premium_disclaimer: 'ประมาณการ ยังไม่ใช่เบี้ยจริง'
    },
    '>30,000': {
      budget_tier: '>30,000',
      recommended_sum_insured: '฿2,000,000',
      sum_insured_range: 'วงเงิน ฿2,000,000–5,000,000',
      estimated_monthly_premium: '฿2,890 / เดือน',
      premium_disclaimer: 'ประมาณการ ยังไม่ใช่เบี้ยจริง'
    }
  };

  /**
   * Main Evaluation Function
   * 
   * @param {Object} catalog - The segment catalog JSON object
   * @param {Array|Object} selectedAnswers - The option IDs selected by the user
   * @returns {Object} Complete evaluation result formatted for Screen 3 (Result Screen)
   */
  function evaluate(catalog, selectedAnswers) {
    if (!catalog) {
      throw new Error('Catalog is required for evaluation');
    }

    const matrix = catalog.result_matrix || {};
    const optionIds = normalizeSelectedOptionIds(selectedAnswers);
    const resolved = resolveSelectedOptions(catalog, optionIds);

    // 1. Calculate Risk Score (0-100)
    const baseRisk = typeof catalog.base_risk_score === 'number'
      ? catalog.base_risk_score
      : (typeof matrix.base_risk_score === 'number' ? matrix.base_risk_score : 20);
    let scoreTotal = baseRisk;

    for (const item of resolved) {
      const weight = typeof item.option.risk_weight === 'number' ? item.option.risk_weight : 0;
      scoreTotal += weight;
    }

    // Clamp score between 0 and 100
    const finalScore = Math.max(0, Math.min(100, Math.round(scoreTotal)));

    // 2. Determine Risk Tier (Low: 0-35, Medium: 36-65, High: 66-100)
    let riskTierKey = 'medium';
    if (finalScore <= 35) {
      riskTierKey = 'low';
    } else if (finalScore <= 65) {
      riskTierKey = 'medium';
    } else {
      riskTierKey = 'high';
    }

    const riskLevels = matrix.risk_levels || {};
    const levelProfile = riskLevels[riskTierKey] || {
      level_name: riskTierKey === 'low' ? 'ความเสี่ยงต่ำ' : (riskTierKey === 'high' ? 'ความเสี่ยงสูง' : 'ความเสี่ยงปานกลาง'),
      headline: `ระดับความเสี่ยงของคุณ: ${riskTierKey === 'low' ? 'ความเสี่ยงต่ำ' : (riskTierKey === 'high' ? 'ความเสี่ยงสูง' : 'ความเสี่ยงปานกลาง')}`,
      evaluation_basis: 'วิเคราะห์จากคำตอบและพฤติกรรมของคุณ'
    };

    // 3. Coverage Tier & Premium Lookup (Mapped dynamically from budget source_option)
    let matchedTier = null;
    let selectedBudgetOption = null;

    // Look for chosen option in question with key 'budget' or step_phase 'gap'
    for (const item of resolved) {
      const qKey = (item.question.source_question_key || '').toLowerCase();
      const optKey = (item.option.source_question_key || '').toLowerCase();
      if (qKey === 'budget' || optKey === 'budget' || item.question.step_phase === 'gap') {
        const srcOpt = item.option.source_option || '';
        const label = item.option.label || '';
        if (srcOpt || label) {
          selectedBudgetOption = item.option;
          if (qKey === 'budget' || optKey === 'budget') break;
        }
      }
    }

    if (selectedBudgetOption) {
      const src = (selectedBudgetOption.source_option || '').trim();
      const combined = (src + ' ' + (selectedBudgetOption.label || '')).replace(/[\s,]/g, '');

      if (src === '>30,000' || combined.includes('>30000') || combined.includes('มากกว่า30000') || combined.includes('30000ขึ้นไป')) {
        matchedTier = DEFAULT_BUDGET_TIERS['>30,000'];
      } else if (src === '20,000-30,000' || combined.includes('20000-30000')) {
        matchedTier = DEFAULT_BUDGET_TIERS['20,000-30,000'];
      } else if (src === '10,000-20,000' || combined.includes('10000-20000')) {
        matchedTier = DEFAULT_BUDGET_TIERS['10,000-20,000'];
      } else if (src === '<10,000' || combined.includes('<10000') || combined.includes('น้อยกว่า10000')) {
        matchedTier = DEFAULT_BUDGET_TIERS['<10,000'];
      }
    }

    // Custom override if catalog defines explicit coverage_tiers
    const customTiers = Array.isArray(matrix.coverage_tiers) ? matrix.coverage_tiers : [];
    if (customTiers.length > 0 && selectedBudgetOption) {
      const optText = selectedBudgetOption.source_option || selectedBudgetOption.label || '';
      const customMatch = customTiers.find(tier => {
        return optText.includes(tier.budget_option) || (tier.budget_option && tier.budget_option.includes(optText));
      });
      if (customMatch) matchedTier = customMatch;
    }

    // Fallback if no budget answer matched
    if (!matchedTier) {
      matchedTier = DEFAULT_BUDGET_TIERS['10,000-20,000'];
    }

    const coverage = {
      budget_tier: matchedTier.budget_tier || 'standard',
      recommended_sum_insured: matchedTier.recommended_sum_insured,
      sum_insured_range: matchedTier.sum_insured_range,
      estimated_monthly_premium: matchedTier.estimated_monthly_premium,
      premium_disclaimer: matchedTier.premium_disclaimer || 'ประมาณการ ยังไม่ใช่เบี้ยจริง'
    };

    // 5. Vulnerability Gap Extraction
    let vulnerabilityGap = null;

    // Search priority: gap step first, then pain step, then any step with gap_statement
    const priorityPhases = ['gap', 'pain', 'hook', 'profile', 'emotion'];
    for (const phase of priorityPhases) {
      const match = resolved.find(item => item.question.step_phase === phase && item.option.gap_statement);
      if (match) {
        vulnerabilityGap = match.option.gap_statement;
        break;
      }
    }

    if (!vulnerabilityGap) {
      // Any match with gap_statement
      const anyMatch = resolved.find(item => item.option.gap_statement);
      if (anyMatch) {
        vulnerabilityGap = anyMatch.option.gap_statement;
      } else {
        vulnerabilityGap = catalog.default_gap_statement || 
          matrix.default_gap_statement || 
          'มีช่องว่างระหว่างวงเงินที่มีกับค่ารักษาจริง โดยเฉพาะกรณีโรคร้ายแรงที่ต้องรักษาต่อเนื่อง';
      }
    }

    return {
      score: finalScore,
      max_score: 100,
      risk_tier: riskTierKey,
      level_name: levelProfile.level_name,
      headline: levelProfile.headline,
      evaluation_basis: levelProfile.evaluation_basis,
      coverage: coverage,
      applied_budget_option: selectedBudgetOption ? (selectedBudgetOption.source_option || selectedBudgetOption.label) : null,
      vulnerability_gap: vulnerabilityGap,
      applied_options: resolved.map(r => ({
        question_id: r.question.question_id,
        source_question_key: r.question.source_question_key,
        option_id: r.option.option_id,
        source_option: r.option.source_option,
        label: r.option.label,
        risk_weight: r.option.risk_weight || 0,
        gap_statement: r.option.gap_statement || null
      }))
    };
  }

  return {
    evaluate: evaluate,
    normalizeSelectedOptionIds: normalizeSelectedOptionIds,
    resolveSelectedOptions: resolveSelectedOptions,
    DEFAULT_BUDGET_TIERS: DEFAULT_BUDGET_TIERS
  };
}));
