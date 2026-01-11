# LLM HALLUCINATION EXPERIMENT - ANALYSIS REPORT

## 1. Summary Statistics

| Metric            |    Condition A |   Condition B |           Condition C |
|                   |   (No Context) |    (Evidence) |   (Evidence + Verify) |
|:------------------|---------------:|--------------:|----------------------:|
| Correctness (%)   |             23 |            81 |                    86 |
| Hallucination (%) |             77 |             4 |                     0 |
| Abstention (%)    |              0 |            42 |                    39 |

## 2. Hypothesis Testing

### H1: Evidence-grounding reduces hallucination (B < A)
**Result:** ✓ SUPPORTED
- Condition A: 77.0%
- Condition B: 4.0%
- Reduction: 73.0 percentage points

### H2: Self-verification further reduces hallucination (C < B)
**Result:** ✓ SUPPORTED
- Condition B: 4.0%
- Condition C: 0.0%
- Reduction: 4.0 percentage points

### H3: Self-verification increases abstention rate (C > A)
**Result:** ✓ SUPPORTED
- Condition A: 0.0%
- Condition C: 39.0%
- Increase: 39.0 percentage points


## 3. Key Findings

1. **Correctness:** Condition C achieved the highest correctness rate (86.0%)
2. **Hallucination:** Condition C had the lowest hallucination rate (0.0%)
3. **Abstention:** Condition C showed 39.0% abstention rate
4. **Citation Quality:** 100.0% of citations in Condition C were faithful


## 4. Case Studies

### Case 1: Evidence Fixed Hallucination

**Question:** Who was the governor of California in 1895?

**Gold Answer:** UNANSWERABLE

**Answer A:** The governor of California in 1895 was James H. Budd. He served as the 19th Governor of California from 1895 to 1899.

**Answer B:** Not enough information

---

### Case 2: Evidence Fixed Hallucination

**Question:** Something that is considered a non fundamental error is the belief that a force is required to maintain what?

**Gold Answer:** UNANSWERABLE

**Answer A:** A non-fundamental error is the belief that a force is required to maintain an object's velocity (or motion). In other words, many people mistakenly think that an object will slow down or come to rest unless a constant force is applied to it. However, according to Newton's First Law of Motion (the Law of Inertia), an object will maintain its velocity unless acted upon by an external force. This means that no force is required to maintain an object's motion; in fact, it is the absence of external forces that allows an object to continue moving at a constant velocity.

**Answer B:** motion at a constant velocity, but more specifically,  a constant velocity, the passage implies that this belief is a fundamental error, therefore the answer would be "Not enough information" since the passage doesn't explicitly state a non-fundamental error.

---

### Case 3: Evidence Fixed Hallucination

**Question:** What did the US abandon? 

**Gold Answer:** UNANSWERABLE

**Answer A:** The US has abandoned several things throughout its history. Without more specific information, it's difficult to pinpoint exactly what you're referring to. However, here are a few examples:

1. **The Gold Standard**: The United States abandoned the gold standard in 1971, moving to a fiat currency system.
2. **The Articles of Confederation**: The US abandoned the Articles of Confederation in favor of the US Constitution in 1789.
3. **Isolationism**: The US initially abandoned its policy of isolationism during World War I and later during World War II, embracing a more interventionist foreign policy.
4. **Certain military bases or territories**: The US has abandoned various military bases or territories around the world, such as the Philippines (1992), Vietnam (1975), and more recently, some bases in Afghanistan (2021).
5. **The draft**: The US abandoned the military draft in 1973, switching to an all-volunteer force.

If you could provide more context or specify which abandonment you're referring to, I'd be happy to provide a more precise answer.

**Answer B:** The US abandoned the Gold Exchange Standard whereby the value of the dollar had been pegged to the price of gold.

---

### Case 4: Evidence Fixed Hallucination

**Question:** What did Joseph Haas say in his email?

**Gold Answer:** "Wise up or die."

**Answer A:** I don't have any information about Joseph Haas or an email he may have sent. This conversation just started. If you'd like to provide more context, I'll do my best to help.

**Answer B:** Joseph Haas allegedly said "Wise up or die" in his email to the Lebanon, New Hampshire city councilors.

---

### Case 5: Evidence Fixed Hallucination

**Question:** What must the adoption of laws which will have legal effect in the EU have?

**Gold Answer:** a proper legal basis

**Answer A:** The adoption of laws which will have legal effect in the EU must be in accordance with the EU's legislative procedures and have a legal basis in the EU Treaties. 

Specifically, the adoption of such laws typically requires:

1. A proposal from the European Commission, which has the sole right to initiate legislative proposals in most areas.
2. Approval from the European Parliament, which represents the citizens of the EU and has co-decision powers with the Council of the European Union in most areas.
3. Approval from the Council of the European Union, which represents the governments of the EU member states.
4. Compliance with the principles of subsidiarity and proportionality, which ensure that EU action is necessary and proportionate to the problem being addressed.
5. A legal basis in the EU Treaties, such as Article 288 of the Treaty on the Functioning of the European Union (TFEU), which sets out the different types of EU legal acts, including regulations, directives, and decisions.

Once these requirements are met, the adopted laws can take the form of regulations, directives, or decisions, which will have legal effect in the EU.

**Answer B:** A proper legal basis.

---


## 5. Conclusion

This experiment demonstrates that:
1. Evidence-grounding significantly reduces hallucination
2. Self-verification provides additional protection against hallucination
3. The trade-off is a moderate increase in abstention rates
4. Overall, Condition C (Evidence + Self-verification) provides the best balance

Recommendations: For factual QA tasks, implementing both evidence-grounding and 
self-verification mechanisms can substantially improve reliability.
