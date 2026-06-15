# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

The domain I chose for this RAG system is CS course and professor reviews at Brooklyn College. There are a number of factors that make this domain rather niche and harder to locate. The targeted audience for this system would be a new CS student at Brooklyn College who is unfamilar with the department and wants to get accurate information from trusted sources. Oftentimes, new students aren't aware of these platforms and it can also be a tedious task to research your particular query. This system takes a holistic approach as it can answer a wide variety of queries regarding CS at Brooklyn College. Additionally, Brooklyn College's CS program is rather small compared to other big names, which may show better results when searching for information.

---

## Document Sources

| # | Source | Description | URL or file path |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Moshe Lach - Highly rated CS professor, strong reviews for Data Structures | https://www.ratemyprofessors.com/professor/2538695 |
| 2 | Rate My Professors | Basak Taylan - Well-regarded for CISC 3115 (Java/OOP) | https://www.ratemyprofessors.com/professor/2363018 |
| 3 | Rate My Professors | Gabriel Yarmish - Teaches intro Java (CISC 1115), mixed reviews | https://www.ratemyprofessors.com/professor/404370 |
| 4 | Rate My Professors | Noson Yanofsky - Theory courses, polarizing reviews | https://www.ratemyprofessors.com/professor/78366 |
| 5 | Rate My Professors | Kleanthis Psarris - Tough grader, theory/architecture track | https://www.ratemyprofessors.com/professor/2939406 |
| 6 | Rate My Professors | Hui Chen - Software engineering, mobile apps, dept contact for CISC 1170 | https://www.ratemyprofessors.com/professor/2429486 |
| 7 | Rate My Professors | Matthew McNeill - Teaches Python (CISC 1215), positive reviews | https://www.ratemyprofessors.com/professor/2760709 |
| 8 | Rate My Professors | Robert Zwick - Teaches CISC 2820W (Ethics), manageable workload | https://www.ratemyprofessors.com/professor/1750106 |
| 9 | Coursicle | CISC 1115 - Intro to Java, first required CS course for most majors | https://www.coursicle.com/brooklyncuny/courses/CISC/1115/ |
| 10 | Coursicle | CISC 3115 - Modern Programming Techniques (OOP, Java), 101 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/3115/ |
| 11 | Coursicle | CISC 3130 - Data Structures, most-reviewed CS course (106 reviews) | https://www.coursicle.com/brooklyncuny/courses/CISC/3130/ |
| 12 | Coursicle | CISC 3110 - Advanced Programming Techniques, 49 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/3110/ |
| 13 | Coursicle | CISC 3310 - Computer Architecture, 43 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/3310/ |
| 14 | Coursicle | CISC 3320 - Operating Systems, 28 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/3320/ |
| 15 | Coursicle | CISC 2820W - Computers and Ethics (writing intensive), 76 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/2820W/ |
| 16 | Coursicle | CISC 3410 - Artificial Intelligence, 13 reviews | https://www.coursicle.com/brooklyncuny/courses/CISC/3410/ |
| 17 | Coursicle | CISC 3440 - Machine Learning | https://www.coursicle.com/brooklyncuny/courses/CISC/3440/ |
| 18 | Coursicle | CISC 3810 - Database Systems | https://www.coursicle.com/brooklyncuny/courses/CISC/3810/ |
| 19 | BC CIS Department | BC CIS Department Homepage - Faculty contacts, deputy chairs, dept info | http://www.sci.brooklyn.cuny.edu/cis/ |
| 20 | BC CIS Department | BC CS Major Requirements - Full 4-year course sequence and degree plan | https://brooklyncisdept.github.io/brochures/UndergradContent/CSmajor.html |
| 21 | BC CIS Department | BC CIS Courses Offered - Full course descriptions and prereqs | https://brooklyncisdept.github.io/brochures/UndergradContent/courses.html |
| 22 | BC CIS Department | BC CS Undergrad Advising Guide (Java Track, 2022) - Degree requirements, concentrations, recommended course sequence | https://www.sci.brooklyn.cuny.edu/~cis/UndergradJava2022.pdf |

> **Removed source:** The BC CISC Undergraduate Course List (`https://websql.brooklyn.cuny.edu/courses/acad/courses_list.jsp?div=U&disc=CISC.`) was dropped — the URL is invalid. Course inventory is covered by source 21 instead. **Total sources: 22.**

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

| Source type | Strategy | Chunk size |
|-------------|----------|------------|
| Rate My Professors | One review = one chunk | ~100–200 tokens per review |
| Coursicle | Semantic / section-based | 250 tokens |
| PDF (advising guide) | Recursive splitting | 1000–1500 tokens |

**Overlap:**

| Source type | Overlap |
|-------------|---------|
| Rate My Professors | ~20 tokens (minimal; reviews are self-contained) |
| Coursicle | 25 tokens |
| PDF (advising guide) | 150–250 tokens |

**Why these choices fit your documents:**

Because my sources mix short user reviews, structured course pages, and a long degree-plan PDF, chunking is source-specific rather than one standardized length. RMP reviews are already structured units of student opinion, so each review becomes its own chunk with only light overlap to preserve context at boundaries when a review is long. Coursicle pages are split by section (course description, reviews, schedule info) with moderate 250-token windows and small overlap so related sentences stay together without merging unrelated course details. The PDF advising guide is long and hierarchical, so recursive splitting with larger 1000–1500 token chunks and 150–250 token overlap keeps degree requirements and prerequisite sections intact across chunk boundaries; images and diagrams in the PDF are dropped during ingestion.

**Final chunk count:**

173 chunks total across 22 documents.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:**

There are various production tradeoffs that I made by using MiniLM and choosing a k value of 5. For a personal project on a narrow domain like CS professor and course reviews at Brooklyn College, this model can run fast on a local setup. It may, however, struggle with long-form documents like PDFs and text may get cut off. MiniLM keeps data local, while managed services or APIs may omit that security and add cost and dependency. A k value of 5 seems like a good starting number to test; a higher value will result in better chunk retrieval for broad questions like degree planning.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
