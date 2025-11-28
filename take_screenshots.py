"""
Automated screenshot capture for SLOOS Analyzer using Playwright
"""
import asyncio
from playwright.async_api import async_playwright


async def take_screenshots():
    """Take screenshots of the SLOOS Analyzer application"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("📸 Starting screenshot capture...")
        
        # Navigate to application
        print("1. Loading application...")
        await page.goto('http://localhost:7251')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # Screenshot 1: Main Dashboard
        print("2. Capturing dashboard...")
        await page.screenshot(path='screenshots/dashboard.png', full_page=True)
        
        # Click Fetch Data button
        print("3. Fetching SLOOS data...")
        await page.click('button:has-text("Fetch SLOOS Data")')
        await asyncio.sleep(5)  # Wait for data to load
        
        # Screenshot 2: Reports List
        print("4. Capturing reports list...")
        await page.screenshot(path='screenshots/reports-list.png', full_page=True)
        
        # Click on first report
        print("5. Selecting first report...")
        await page.click('.report-item:first-child')
        await asyncio.sleep(1)
        
        # Click Summary button
        print("6. Generating AI analysis...")
        await page.click('button:has-text("Summary")')
        await asyncio.sleep(15)  # Wait for AI analysis
        
        # Screenshot 3: Analysis Result
        print("7. Capturing analysis result...")
        await page.screenshot(path='screenshots/analysis-result.png', full_page=True)
        
        # Type in chat
        print("8. Testing chat interface...")
        chat_input = await page.query_selector('#chatInput')
        if chat_input:
            await chat_input.fill('What are the main trends in recent SLOOS reports?')
            await page.click('button:has-text("Send")')
            await asyncio.sleep(15)  # Wait for AI response
        
        # Screenshot 4: Chat Interface
        print("9. Capturing chat interface...")
        await page.screenshot(path='screenshots/chat-interface.png', full_page=True)
        
        print("✅ All screenshots captured successfully!")
        print("\nScreenshots saved:")
        print("  - screenshots/dashboard.png")
        print("  - screenshots/reports-list.png")
        print("  - screenshots/analysis-result.png")
        print("  - screenshots/chat-interface.png")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(take_screenshots())
