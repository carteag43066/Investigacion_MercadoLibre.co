from playwright.sync_api import sync_playwright
import time
import json

def click_reviews_button_and_scroll(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Modo visible para depuración
        page = browser.new_page()

        # Agregar un User-Agent para evitar bloqueos
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        page.set_extra_http_headers({"User-Agent": user_agent})

        print("🔗 Abriendo la página del producto...")
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(3)

        # Hacer clic en el botón "Mostrar todas las opiniones"
        print("📝 Buscando el botón 'Mostrar todas las opiniones'...")
        try:
            button = page.locator("button[data-testid='see-more']")
            button.wait_for(timeout=5000)
            button.click()
            print("✅ Se hizo clic en el botón correctamente.")
            time.sleep(3)
        except:
            print("⚠️ No se encontró el botón de opiniones.")
            browser.close()
            return

        # Esperar a que el modal cargue los comentarios
        try:
            page.wait_for_selector("div.ui-review-capability-comments", timeout=5000)
            print("✅ Sección de comentarios encontrada. Procediendo a hacer scroll...")
        except:
            print("⚠️ No se encontró la sección de comentarios.")
            browser.close()
            return

        # Hacer scroll en la sección de comentarios
        print("🔽 Haciendo scroll en la sección de opiniones...")
        last_height = 0
        max_scrolls = 20  # Límite de scrolls
        scroll_attempts = 0

        while scroll_attempts < max_scrolls:
            page.mouse.wheel(0, 500)  # Simula un scroll con la rueda del mouse
            time.sleep(3)  # Espera a que los comentarios se carguen
            
            # Verificar si la altura cambió
            new_height = page.evaluate("document.querySelector('div.ui-review-capability-comments')?.scrollHeight")
            print(f"🧐 Altura antes: {last_height} | Nueva altura después del scroll: {new_height}")

            if new_height is None or new_height == last_height:
                break  # Si la altura no cambia, no hay más contenido para cargar
            
            last_height = new_height
            scroll_attempts += 1

        print("✅ Scroll completado. Todas las opiniones han sido cargadas.")
        time.sleep(3)  # Esperar a que los comentarios se rendericen completamente

        # Extraer comentarios
        print("📝 Extrayendo comentarios...")
        comments = []
        comment_elements = page.locator("article[data-testid='comment-component']").all()

        if not comment_elements:
            print("⚠️ No se encontraron comentarios.")
        else:
            for comment in comment_elements:
                try:
                    text = comment.locator("p.ui-review-capability-comments__comment__content").text_content()
                    if text:
                        comments.append(text.strip())
                except:
                    print("⚠️ No se pudo extraer texto de un comentario.")

            print(f"✅ Se encontraron {len(comments)} comentarios.")
            print(comments)

            # Guardar en un archivo JSON
            with open("comentarios.json", "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=4)
            print("💾 Comentarios guardados en 'comentarios.json'")

        print("⏳ Espera finalizada. Cerrando el navegador...")
        browser.close()

# URL del producto en Mercado Libre
url = "https://articulo.mercadolibre.com.co/MCO-582360754-babuchas-y-pantuflas-hermosas-para-toda-la-familia-_JM?searchVariation=174132931574#reviews"
click_reviews_button_and_scroll(url)
