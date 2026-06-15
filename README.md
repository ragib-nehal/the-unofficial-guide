# The Unofficial Guide

**Video / Demo:** [Watch the demo on Loom](https://www.loom.com/share/ace5c267589044e981bcae4a4e941f11)

> *Note: The audio had issues despite several recording attempts, so the demo has no sound. I use my cursor throughout to point to the important aspects.*

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## How to Run

### Prerequisites

- Python 3.10+
- A free Groq API key from [console.groq.com](https://console.groq.com) (no credit card required)

### Setup

From the project root (`the-unofficial-guide/`):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your key:

```
GROQ_API_KEY=your_key_here
```

### Build the vector store (first time only)

ChromaDB data is not committed to git. On a fresh clone, embed the pre-built chunks in `output/chunks.jsonl`:

```bash
python -m pipeline.run_embed
```

To force a full re-embed:

```bash
python -m pipeline.run_embed --rebuild
```

To regenerate chunks from the source documents first:

```bash
python -m pipeline.run_pipeline --inspect
python -m pipeline.run_embed --rebuild
```

### Start the app

```bash
python app.py
```

Gradio prints a local URL (typically `http://127.0.0.1:7860`). Open it in your browser and ask questions about Brooklyn College CS courses and professors.

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
There are various instructions I used to ensure a grounded response. First I identified the role and the task: The model is a Brooklyn College CS guide that must summarize that the retrieved documents say. I also created a hard rule the states, the system should only base its answer on the provided documents, no outside knowledge. There is also a hard rule that prevents the system from answering if it has nothing to say. Partial context is enough, however, to generate a response. I also turned down the randomness effect with lowering the temperature as much as possible to prevent hallucinations. In terms of the pipeline design, I used the top 5 chunks, used a semantic and keyword retrieval, and prioritized professor or course names when chunks are ranked.

**How source attribution is surfaced in the response:**
Source list is built from the same chunks sent to the model and the labels are easy to read when determining the source name. That said, sources are not included in the answer. In the UI, the retrieved chunks and the sources are both on seperate sections of the output.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Moshe Lach for data structures? | Strong positive reviews, good at explaining, engaging | Students praise him as a knowledgeable Data Structures instructor; attending lectures, doing homework, and studying are key to passing; many give 5.0 quality ratings | Relevant | Accurate |
| 2 | What's the hardest CS class in Brooklyn College? | No single answer in our corpus; student reviews suggest tough courses like CISC 2210 (Kleanthis Psarris, difficulty 5.0) | Points to Psarris's CISC 2210 and 7221 (difficulty 5.0, tough grader) as the hardest-rated classes in the retrieved reviews, but admits that it cannot name one definitive hardest class | Partially relevant | Partially accurate |
| 3 | What do students say about Gabriel Yarmish for CISC 1115? | Mixed, some find the pace slow or lectures unhelpful, but manageable for the material | Mixed reviews: one student praises his kindness and clear explanations (5.0), another finds lectures unenthusiastic and recommends other options (2.0) | Partially relevant | Accurate |
| 4 | What are the prerequisites for CISC 3130? | Must complete CISC 3115 with a C or higher first | CISC 3115, or CISC 3110 and 1170 | Relevant | Accurate |
| 5 | What is the recommended 4-year course schedule for a CS major? | Sem 1: CISC 1115 + MATH; Sem 2: CISC 2210, 3115 + MATH; Sem 3: CISC 2820W, 3130; Sem 4: CISC 3305/3310 + MATH; Sem 5: CISC 3142 + 3220/3230; Sem 6: CISC 3150, 3320 + MATH; Sem 7: CISC 4900/5001 + elective; Sem 8: electives | Full 8-semester sequence (CISC 1115 through electives) pulled from the advising guide and major requirements | Relevant | Accurate |

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

What's the hardest CS class in Brooklyn College?

**What the system returned:**

Points to Psarris's CISC 2210 and 7221 (difficulty 5.0, tough grader) as the hardest-rated classes in the retrieved reviews, but admits that it cannot name one definitive hardest class.

**Root cause (tied to a specific pipeline stage):**

This is primarily a retrieval failure. The question asks for a campus-wide comparison, but difficulty information in my documents is scattered across individual RMP reviews and Coursicle comments and there is no single document that ranks all CS classes. With top-k=5, semantic search returned Psarris RMP chunks and a generic BC CIS course-catalog chunk, but missed other relevant chunks such as the Coursicle review for CISC 3320 that calls it "arguably most difficult CS course." The word "hardest" also does not appear in my documents.

**What you would change to fix it:**

For questions like this, I would likely increase the k value and add an intent layer to the query. I might also be able to add a a difficulty rating as metadata, allowing filtering by rank at retrieval time. It would also be a good practice to summarize the ranges of opinions, if no single answer truly exists. 
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The spec ensured that there was a clear ingestion target, that being the documents I had chosen. I also specified source specific chunking which was essentinal for proper chunking. The evaluation questions were also useful in testing the accuracy of the model and tuning it. 

**One way your implementation diverged from the spec, and why:**
One way the implementation diverged from the spec was the addition of keyword matching which created a hybrid retrieval strategy. I also had to specificaly highlight professor and course names since the retriever was having trouble on some simple queries. I also did not use webscraping and stuck with copying webpages directly, then clearning the raw data. 
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

I gave AI my chunking strategy from the planning doc and one sample cleaned text from three of the main data sources. 

- *What it produced:*

It created the chunk_documents() function that had a source specific logic for each type.

- *What I changed or overrode:*

I kept the different token sizes for each source type and added course-number metadata extraction. 

**Instance 2**

- *What I gave the AI:*

I gave AI my evaluation questions from the planning doc, same query results from ChromaDB, and the Groq API key. 

- *What it produced:*

I produced a basic retrieve() with a grounded answer.

- *What I changed or overrode:*

I added hybrid keyword matching to enrich the retrieved chunks since semantic was not optimal. 
