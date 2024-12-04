def process_documentation(doc_text, tags):
    """
    Split a documentation file into chunks and add metadata
    """
    sections = []
    
    # Example processing logic
    if "Overview" in doc_text:
        sections.append({
            "content": extract_overview(doc_text),
            "metadata": json.dumps({
                "type": "voip",
                "category": "overview",
                "tags": tags
            })
        })
    
    if "Steps" in doc_text:
        steps = extract_steps(doc_text)
        for step in steps:
            sections.append({
                "content": step,
                "metadata": json.dumps({
                    "type": "voip",
                    "category": "procedure",
                    "tags": tags
                })
            })
    
    return sections 