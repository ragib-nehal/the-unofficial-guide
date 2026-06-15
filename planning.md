# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation - the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain I chose for this RAG system is CS course and professor reviews at Brooklyn College. There are a number of factors that make this domain rather niche and harder to locate. The targeted audience for this system would be a new CS student at Brooklyn College who is unfamilar with the department and wants to get accurate information from trusted sources. Oftentimes, new students aren't aware of these platforms and it can also be a tedious task to research your particular query. This system takes a holistic approach as it can answer a wide variety of queries regarding CS at Brooklyn College. Additionally, Brooklyn College's CS program is rather small compared to other big names, which may show better results when searching for information. 

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
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

> **Removed source:** The BC CISC Undergraduate Course List (`https://websql.brooklyn.cuny.edu/courses/acad/courses_list.jsp?div=U&disc=CISC.`) was dropped during implementation — the URL is invalid and no longer serves usable course content. Course titles and prerequisites are covered by source 21 (BC CIS Courses Offered) instead. **Total sources: 22.**

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

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

**Reasoning:**

Because my sources mixes short user reviews, structured course pages, and a long degree-plan like the PDF, chunking is source-specific rather than one standardized length. RMP reviews are already structured units of student opinion, so each review becomes its own chunk with only light overlap to preserve the context at boundaries when a review is long. Coursicle pages are split by section (course description, reviews, schedule info) with moderate 250-token windows and small overlap so related sentences stay together without merging unrelated course details. The PDF advising guide is long and hierarchical, so recursive splitting with larger 1000–1500 token chunks and 150–250 token overlap keeps degree requirements and degree prerequisite sections intact across chunk boundarie and any images or diagrams get dropped. 

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model - context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:** There are various production tradeoffs that I made by using MiniLM and choosing a k value of 5. For a personal project, on a narrow domain like CS professor and course reviews at Brooklyn College, this model can run fast on a local setup. It may, however, struggle with long form documents like pdfs and text may get cut off. MiniLM keeps data local, while managed services or APIs may omit that security and add cost and dependency. A k values of 5 seems like a good starting number to test. A higher value will result in better chunk retrieval for broad questions like degree planning.  
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer | Source(s) |
|---|----------|-----------------|-------------|
| 1 | What are the prerequisites for CISC 3130 (Data Structures)? | Must complete CISC 3115 with a C or higher first | BC CIS courses offered (source 21) |
| 2 | What do students say about Moshe Lach for Data Structures? | Strong positive reviews — good at explaining, engaging | RMP source 1 |
| 3 | Is CISC 3115 or CISC 3130 more reviewed on Coursicle? | CISC 3130 has more (106 vs 101 reviews) | Coursicle sources 10, 11 |
| 4 | What courses are required for the CS major that involve hardware or systems? | CISC 3305 or 3310 (Architecture), CISC 3320 (OS) | BC CS major requirements |
| 5 | What do students say about Gabriel Yarmish for CISC 1115? | Mixed — some find the pace slow or lectures unhelpful, but manageable for the material | RMP source 3 |
| 6 | What is the recommended 4-year course schedule for a CS major? | Sem 1: CISC 1115 + MATH 1011/1201; Sem 2: CISC 2210, 3115 + MATH; Sem 3: CISC 2820W, 3130; Sem 4: CISC 3305/3310 + MATH; Sem 5: CISC 3142 + 3220/3230; Sem 6: CISC 3150, 3320 + MATH; Sem 7: CISC 4900/5001 + elective; Sem 8: electives | BC advising PDF (source 22), p. 11 |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. One of the challenges I will face is in chunking the large PDF file that contains official advice and pathways for CS undergrads from Brooklyn College. There is a plethora of structured content in that document like prerequisites, course sequences, degree requirements, suggested schedules, and diagrams. For instance, if a chunk ends in the middle of a schedule sequence, it will be stored as an incomplete context, that the retriever might use. This may lead to incomplete or inaccurate answers regarding CS courses. 

2. While Rate My Professor is a great source for professor reviews and student feedback, it can sometimes be vague, inconsistant, and informal. Often times, a professors name might not even be mentioned. The retriever might have difficulty understanding the intent behind the chunk and create false context, which ultimately affects the output the LLM gives us.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

![RAG pipeline: Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation](assets/Document%20Ingestion%20to-2026-06-15-023036.png)

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 - Ingestion and chunking:**

Document Ingestion:
I'll give Claude the source table from this planning doc which includes all 22 sources with URLs and descriptions and ask it to generate scraping scripts per source type. One for RMP pages using BeautifulSoup, one for Coursicle pages, one for the BC CIS department's HTML pages, and one using PyMuPDF for the advising PDF. I'll review each script and test against a single source before running running the rest.

Chunking:
I'll prompt Claude with example raw output from each scraper such as a sample RMP review, a Coursicle entry, a PDF page and ask it to implement a chunk_documents() function that handles each source type. I'll include the token ranges from the architecture diagram so it knows my target sizes for each type of source. 

**Milestone 4 - Embedding and retrieval:**

Embedding:
I'll ask Claude to write the ChromaDB setup which includes creating the collection, embedding chunks with all-MiniLM-L6-v2's sentence-transformers, and storing them with metadata like source type, professor name, course number. I'll provide my chunked output format as input context.

Retrieval:
I'll give Claude the evaluation questions from this document and ask it to implement the retrieve() function that queries ChromaDB using cosine similarity and top-k=5. I'll also ask it to add logging so I can see which chunks get retrieved per question during eval.

**Milestone 5 - Generation and interface:**

I'll prompt Claude with the Groq API setup and a sample retrieval result, and ask it to build the prompt template that feeds retrieved chunks and the user question to llama-3.3-70b-versatile. I'll include the expected answers from my eval table so it can help me tune the system prompt.