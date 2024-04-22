from time import sleep
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    open_robot_order_website()
    download_orders_files()

    orders = get_orders()
    for order in orders:
        fill_the_form(order)
        submit_order()
        order_number = order["Order number"]
        pdf_file = store_receipt_as_pdf(order_number)
        screenshot = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
        order_another_bot()
        close_annoying_modal()
    
    archive_receipts()


def open_robot_order_website():
    """open browser"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def download_orders_files():
    """download csv"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """fill form with csv files"""
    csv_file = Tables()
    robot_order = csv_file.read_table_from_csv("orders.csv")
    return list(robot_order)
   
def close_annoying_modal():
    """modal ok"""
    page = browser.page()
    page.click("text=OK")

def order_another_bot():
    """Clicks on order another button to order another bot"""
    page = browser.page()
    page.click("#order-another")

def fill_the_form(order):

    page = browser.page()
    page.select_option("#head" , str(order["Head"]))
    page.click(f"#id-body-{order['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address" , str(order["Address"]))
 

def submit_order():
    page = browser.page()
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            break
        else:
            attempts += 1
            sleep(2) 
        


def store_receipt_as_pdf(order_number):
    """takes pdf"""
    page = browser.page()
    order_receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """Takes screenshot"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """embeded to zip"""
    pdf = PDF()
    pdf.close_all_pdfs()
    pdf.add_files_to_pdf(files=[screenshot_path], target_document=pdf_path, append=True)



def archive_receipts():
    """ """
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")