from playwright.sync_api import sync_playwright

def test_smoke_playwright():
    with sync_playwright() as p:
        # Lanza el navegador de forma visible (--headed)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Entra a una web de prueba
        page.goto("https://example.com")
        
        # Verifica que el título sea el correcto
        assert "Example Domain" in page.title()
        print("¡Playwright funciona correctamente en tu proyecto!")
        
        browser.close()