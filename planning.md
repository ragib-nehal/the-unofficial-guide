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
| 21 | BC CIS Department | BC CISC Undergraduate Course List - All CISC course numbers and titles | https://websql.brooklyn.cuny.edu/courses/acad/courses_list.jsp?div=U&disc=CISC. |
| 22 | BC CIS Department | BC CIS Courses Offered - Full course descriptions and prereqs | https://brooklyncisdept.github.io/brochures/UndergradContent/courses.html |
| 23 | BC CIS Department | BC CS Undergrad Advising Guide (Java Track, 2022) - Degree requirements, concentrations, recommended course sequence | https://www.sci.brooklyn.cuny.edu/~cis/UndergradJava2022.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model - context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 - Embedding and retrieval:**

**Milestone 5 - Generation and interface:**
