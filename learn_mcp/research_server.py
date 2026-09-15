import arxiv
import json
import os
from datetime import date
from typing import Dict, List
from pydantic import BaseModel, TypeAdapter, ValidationError
from mcp.server.fastmcp import FastMCP


PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research", port=8080)


class PaperInfo(BaseModel):
    title: str
    authors: List[str]
    summary: str
    pdf_url: str
    published: date


PapersInfo = Dict[str, PaperInfo]
_papers_adapter = TypeAdapter(PapersInfo)


def _load_papers_info(file_path: str) -> PapersInfo:
    """Load and validate a topic's papers_info.json into typed PaperInfo objects."""
    try:
        with open(file_path, "rb") as json_file:
            return _papers_adapter.validate_json(json_file.read())
    except FileNotFoundError:
        return {}
    except (ValidationError, json.JSONDecodeError) as e:
        print(f"Error reading {file_path}: {str(e)}")
        return {}


def _save_papers_info(file_path: str, papers_info: PapersInfo) -> None:
    with open(file_path, "wb") as json_file:
        json_file.write(_papers_adapter.dump_json(papers_info, indent=2))


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv to find the papers
    # page_size caps how many results are requested per HTTP page; without it,
    # arxiv.Client defaults to 100 regardless of max_results below.
    client = arxiv.Client(page_size=min(max_results, 100))

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = topic,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
    
    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    papers_info = _load_papers_info(file_path)

    # Process each paper and add to papers_info
    paper_ids = []
    for paper in papers:
        paper_id = paper.get_short_id()
        paper_ids.append(paper_id)
        papers_info[paper_id] = PaperInfo(
            title=paper.title,
            authors=[author.name for author in paper.authors],
            summary=paper.summary,
            pdf_url=paper.pdf_url,
            published=paper.published.date(),
        )

    # Save updated papers_info to json file
    _save_papers_info(file_path, papers_info)

    print(f"Results are saved in: {file_path}")
    
    return paper_ids

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
 
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                papers_info = _load_papers_info(file_path)
                if paper_id in papers_info:
                    return papers_info[paper_id].model_dump_json(indent=2)
    
    return f"There's no saved information related to paper {paper_id}."

@mcp.resource("papers://folders")
def get_available_folders()->str:
    """
    List all available topic folders in the papers directory.

    This resource provides a simple list of all available topic folders.
    """
    folders = []

    # get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)

    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"
    
    return content
@mcp.resource("papers://{topic}")
def get_topic_papers(topic:str)->str:
    """
    Get detailed information about papers on a specific topic.
    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")
    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."

    papers_data = _load_papers_info(papers_file)

    # Create markdown content with paper details
    content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
    content += f"Total papers: {len(papers_data)}\n\n"

    for paper_id, paper_info in papers_data.items():
        content += f"## {paper_info.title}\n"
        content += f"- **Paper ID**: {paper_id}\n"
        content += f"- **Authors**: {', '.join(paper_info.authors)}\n"
        content += f"- **Published**: {paper_info.published}\n"
        content += f"- **PDF URL**: [{paper_info.pdf_url}]({paper_info.pdf_url})\n\n"
        content += f"### Summary\n{paper_info.summary[:500]}...\n\n"
        content += "---\n\n"

    return content

@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool. Follow these instructions:
    1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
    2. For each paper found, extract and organize the following information:
       - Paper title
       - Authors
       - Publication date
       - Brief summary of the key findings
       - Main contributions or innovations
       - Methodologies used
       - Relevance to the topic '{topic}'
    
    3. Provide a comprehensive summary that includes:
       - Overview of the current state of research in '{topic}'
       - Common themes and trends across the papers
       - Key research gaps or areas for future investigation
       - Most impactful or influential papers in this area
    
    4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.
    
    Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""

## helper methods
def _get_filename_from_url(url: str) -> str:
    """Get the filename from the url."""
    if url.startswith("https://"):
        url = url.replace("https://", "", 1)
    elif url.startswith("http://"):
        url = url.replace("http://", "", 1)

    if url.startswith("www."):
        url = url.replace("www.", "", 1)

    first_phase = url.split(".")[0]

    return f"{first_phase}_summary.md "


@mcp.prompt()
def generate_fetch_summary_store_file_prompt(url: str) -> str:
    """Generate a prompt for Claude to fetch content, summarize it and store it in a file."""
    return f"""You are a precise automation assistant. You must use your natively available tools to download, summarize, and save webpage content.

    URL to process: {url}
    Target Filename: {_get_filename_from_url(url)}

    Instructions:
    1. Call the fetch tool to extract the raw page content from the URL.
    2. Draft a structured markdown summary of that content (including an overview, core concepts, and key highlights using headings and bullet points).
    3. Call your filesystem file-writing tool to save the drafted summary. Pass the entire summary string directly into the tool's text/content argument, and use '{_get_filename_from_url(url)}' as the file path.

    CRITICAL TOOL RULES:
    - Do NOT output a bash block (like ```bash echo...```) or write code to simulate saving the file. 
    - You must physically execute the file-writing tool call. 
    - The text content inside the file must contain ONLY your drafted markdown summary—no conversational intros, outros, or explanations.
    """
if __name__ == "__main__":
    mcp.run(transport='streamable-http')

