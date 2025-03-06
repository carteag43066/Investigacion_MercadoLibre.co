from playwright.sync_api import sync_playwright, Playwright
from rich import print
import json
import time
import random
import os

# Falta trabajr el tema de la paginacion. 

def run(playwright: Playwright):
    start_url = "https://www.bhphotovideo.com/c/buy/SLR-Camera-Lenses/ci/274/N/4288584247"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    # Archivo donde guardaremos los datos
    output_file = "productos.json"

    # Si el archivo no existe, crearlo con una lista vacía
    if not os.path.exists(output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    browser = playwright.chromium.launch(headless=False)  # Ejecutar en modo visible
    page = browser.new_page()
    
    # Simular navegador real
    page.set_extra_http_headers({"User-Agent": user_agent})

    page.goto(start_url, wait_until="domcontentloaded")  # Cargar rápido

    # Simular scroll y movimiento de mouse para parecer humano
    page.mouse.move(random.randint(100, 500), random.randint(100, 500))
    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
    time.sleep(random.uniform(2, 5))

    # Esperar a que los productos se carguen en la página
    page.wait_for_selector('a[data-selenium="miniProductPageProductNameLink"]', timeout=5000)

    max_links = 2  # Límite de productos a visitar
    links_visited = 0

    for link in page.locator('a[data-selenium="miniProductPageProductNameLink"]').all():
        if links_visited >= max_links:
            break  # Detiene el scraping después de visitar 5 productos

        url = link.get_attribute('href')

        if url:
            p = browser.new_page()  # Crear una nueva pestaña solo si `url` es válido
            p.set_extra_http_headers({"User-Agent": user_agent})  # Aplicar User-Agent en cada pestaña
            p.goto(f"https://www.bhphotovideo.com{url}", wait_until="domcontentloaded")

            # Esperar si hay CAPTCHA
            if "Verifying you are human" in p.content():
                input("⚠️ Completa el CAPTCHA y luego presiona Enter para continuar...")

            try:
                p.wait_for_load_state("networkidle")  # Asegurar que la página está completamente cargada
                scripts = p.locator("script[type='application/ld+json']").all()

                product_data = None  # Variable para almacenar el JSON correcto

                for script in scripts:
                    data = script.text_content()

                    # Verificar si el JSON contiene información de producto
                    if data and '"@type":"Product"' in data:
                        product_data = json.loads(data)
                        break  # Salir del bucle al encontrar el JSON correcto

                if product_data:
                    print(f"✅ Producto encontrado en {url}:")
                    print(json.dumps(product_data, indent=2))  # Mostrar el JSON formateado

                    # Guardar los datos en un archivo JSON
                    try:
                        with open(output_file, "r", encoding="utf-8") as f:
                            productos = json.load(f)

                        # Agregar el nuevo producto extraído
                        productos.append(product_data)

                        # Guardar nuevamente en el archivo JSON
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(productos, f, ensure_ascii=False, indent=2)

                        print(f"📁 Datos guardados en {output_file}")

                    except Exception as e:
                        print(f"⚠️ Error guardando el JSON: {e}")

                else:
                    print(f"⚠️ No se encontró JSON de producto en {url}")

            except Exception as e:
                print(f"⚠️ Error al extraer datos de {url}: {e}")

            finally:
                p.close()  # Ahora cerramos la pestaña después de extraer los datos

        links_visited += 1  # Contador de productos visitados

    print("✅ Finalizado, cerrando navegador.")
    browser.close()  # Cierra el navegador al final

# Ejecutar Playwright
with sync_playwright() as playwright:
    run(playwright)