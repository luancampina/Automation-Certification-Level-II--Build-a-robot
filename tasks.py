import requests
from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive



@task
def order_robots_from_RobotSpareBin():
    """
    - Orders robots from RobotSpareBin Industries Inc.
    - Saves the order HTML receipt as a PDF file.
    - Saves the screenshot of the ordered robot.
    - Embeds the screenshot of the robot to the PDF receipt.
    - Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
         slowmo=200
    )
    open_robot_order_website("https://robotsparebinindustries.com/#/robot-order")
    download_order_file("https://robotsparebinindustries.com/orders.csv")
    close_annoying_modal()
    orders = get_orders("orders.csv")
    for order in orders:
        fill_the_form(order)
        send_order()
        receipt = store_receipt_as_pdf(order['Order number'])
        screenshot = screenshot_order(str(order['Order number']))
        embed_screenshot_to_receipt(screenshot, receipt)
        new_order()
    archive_receipts("output/receipts", "output/receipts.zip")

def open_robot_order_website(url):
    """ Open order website """
    browser.goto(url)

def get_orders(file):
    """ Get table orders from orders.csv """
    library = Tables()
    return library.read_table_from_csv(file)

def new_order():
    """ Click in button for another order """
    page = browser.page()
    page.click("#order-another")
    close_annoying_modal()

def download_order_file(url):
    """ Download CSV file """
    response = requests.get(url)
    response.raise_for_status()

    with open("orders.csv", 'wb') as file:
        file.write(response.content)

def fill_the_form(row):
    """ Open order website """
    page = browser.page()
    page.select_option('#head', str(row['Head']))
    page.locator(f"#id-body-{str(row['Body'])}").check()
    page.fill("//label[contains(text(), '3. Legs:')]/following-sibling::input",str(row['Legs']))
    page.locator("#address").fill(row['Address'])

def send_order():
    page = browser.page()
    page.click("#order")        
    attempt = 0
    while page.locator("css=div.alert-danger").is_visible():
        page.click("#order")
        attempt += 1
        if attempt > 10:
            break
 
def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def store_receipt_as_pdf(order_number):
     page = browser.page()
     receipt = page.locator("#receipt").inner_html()
     pdf_file = f"./output/receipts/order{order_number}.pdf"
     pdf = PDF()
     pdf.html_to_pdf(receipt, pdf_file, margin=10)
     return pdf_file
    
def screenshot_order(order_number):
     page = browser.page()
     path_image = f"./output/screenshot/order{order_number}.png"
     page.locator("#robot-preview-image").screenshot(path=path_image)
     return path_image

def embed_screenshot_to_receipt(screenshot, pdf_file):
     pdf = PDF()
     pdf.add_watermark_image_to_pdf(image_path=screenshot,source_path=pdf_file,output_path=pdf_file)

def archive_receipts(folder_path, zip_path):
    lib = Archive()
    lib.archive_folder_with_zip(folder_path, zip_path)