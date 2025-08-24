#!/usr/bin/env python3
"""Test browser functionality with Playwright"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def test_browser():
    """Test the HTML file in browser"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda error: print(f"PAGE ERROR: {error}"))
        
        # Navigate to HTML file
        html_path = Path("C:/Users/yoshitaka/new-ai-news-site/docs/index.html").as_uri()
        print(f"Loading: {html_path}")
        
        await page.goto(html_path)
        
        # Wait for page to load
        await page.wait_for_timeout(2000)
        
        # Check if articles-data element exists
        articles_data = await page.query_selector('#articles-data')
        print(f"Articles data element found: {articles_data is not None}")
        
        if articles_data:
            # Get the JSON content
            json_content = await articles_data.inner_text()
            print(f"JSON content length: {len(json_content)}")
            print(f"JSON preview: {json_content[:100]}...")
        
        # Check if articles are displayed
        article_cards = await page.query_selector_all('.article-card')
        print(f"Article cards found: {len(article_cards)}")
        
        # Check statistics
        stat_total = await page.query_selector('#stat-total')
        if stat_total:
            total_text = await stat_total.inner_text()
            print(f"Total articles stat: {total_text}")
        
        stat_tier1 = await page.query_selector('#stat-tier1')
        if stat_tier1:
            tier1_text = await stat_tier1.inner_text()
            print(f"Tier1 articles stat: {tier1_text}")
        
        # Check if JavaScript is running
        await page.evaluate("console.log('JavaScript evaluation test')")
        
        # Try to manually trigger the dashboard
        try:
            result = await page.evaluate("""
                const data = document.querySelector('#articles-data');
                if (data) {
                    const articles = JSON.parse(data.textContent);
                    return {
                        dataFound: true,
                        articlesCount: articles.length,
                        firstArticle: articles[0]?.title || 'no title'
                    };
                } else {
                    return { dataFound: false };
                }
            """)
            print(f"Manual JS test result: {result}")
        except Exception as e:
            print(f"JavaScript evaluation error: {e}")
        
        # Take a screenshot
        await page.screenshot(path="C:/Users/yoshitaka/new-ai-news-site/browser_test.png")
        print("Screenshot saved: browser_test.png")
        
        # Keep browser open for 10 seconds to see the page
        print("Keeping browser open for inspection...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_browser())