from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import weaviate
import os
from typing import List, Dict

app = FastAPI(title="Support Docs Search")

# ... your existing setup code ...

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support Documentation Search</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            .search-container {
                margin: 20px 0;
            }
            input[type="text"] {
                width: 70%;
                padding: 10px;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #007bff;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            #results {
                margin-top: 20px;
            }
            .result-item {
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .metadata {
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <h1>Support Documentation Search</h1>
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Enter your search query...">
            <button onclick="search()">Search</button>
        </div>
        <div id="results"></div>

        <script>
        async function search() {
            const query = document.getElementById('searchInput').value;
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = 'Searching...';
            
            try {
                const response = await fetch(`/search/?query=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    resultsDiv.innerHTML = data.results.map((result, index) => `
                        <div class="result-item">
                            <div class="metadata">Source: ${result.metadata}</div>
                            <p>${result.content}</p>
                        </div>
                    `).join('');
                } else {
                    resultsDiv.innerHTML = '<p>No results found.</p>';
                }
            } catch (error) {
                resultsDiv.innerHTML = '<p>Error performing search. Please try again.</p>';
                console.error('Error:', error);
            }
        }

        // Allow pressing Enter to search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                search();
            }
        });
        </script>
    </body>
    </html>
    """

# ... your existing search endpoint ... 