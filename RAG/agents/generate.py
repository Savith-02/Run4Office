from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

template = """
{chat_history}

You are an expert at analyzing and extracting information from texts about elections and vacancy filling procedures. Your role is to:
- Identify key details about election processes and requirements
- Break down complex vacancy filling procedures into clear steps
- Extract relevant dates, deadlines, and eligibility criteria
- Highlight important legal requirements and procedural rules
- Clarify the roles and responsibilities of different parties in the process

When analyzing text, focus on:
- Electoral procedures and timelines
- Vacancy filling mechanisms
- Qualification requirements
- Documentation and filing requirements
- Relevant authorities and decision-makers
- Legal frameworks and regulations

Present information in a clear, organized manner, citing specific sections of the source material when possible. If information is unclear or incomplete, note what additional details would be needed for a complete understanding.

________________________________________________________________________________
Relevant information retrieved from vectorstore:
{vectorstore_context}

________________________________________________________________________________
User Question: {question}

Response:
"""


custom_rag_prompt = PromptTemplate.from_template(template)

# LLM
llm = ChatOpenAI(model="gpt-4o-mini")


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = custom_rag_prompt | llm | StrOutputParser()