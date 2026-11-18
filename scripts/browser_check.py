"""Check the built UI in a real Chromium session."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=os.getenv("CHROMIUM_PATH"),
                                          args=["--no-sandbox"])
    page = browser.new_page(viewport={"width":1440,"height":1050}, accept_downloads=True)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("http://127.0.0.1:8000/")
    expect(page.get_by_role("heading",name="Financial summary")).to_be_visible()
    expect(page.locator(".kpi strong").first).to_contain_text("$")
    expect(page.locator(".recharts-area-area")).to_be_visible()
    capture = os.getenv("DATAFLOW_SCREENSHOT")
    if capture:
        Path(capture).parent.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=capture,full_page=True)
    navigation = page.get_by_role("navigation")
    for title in ("Sales Analytics","Customer Intelligence","Retention & Cohorts","Marketing Analytics",
                  "Product Analytics","Experimentation","Data Quality","Pipeline Monitoring"):
        navigation.get_by_role("button",name=title).click()
        expect(page.get_by_role("heading",name=title+" details")).to_be_visible()
        expect(page.get_by_role("table").first).to_be_visible()
    navigation.get_by_role("button",name="Sales Analytics").click()
    page.get_by_label("From",exact=True).fill("2025-12-01")
    page.get_by_role("button",name="Apply").click()
    expect(page.get_by_role("cell",name="2025-12-01",exact=True)).to_be_visible()
    expect(page.get_by_role("cell",name="2025-11-01",exact=True)).to_have_count(0)
    navigation.get_by_role("button",name="Reports & Exports").click()
    with page.expect_download() as download:
        page.get_by_role("link",name="Download Excel workbook").click()
    assert download.value.suggested_filename == "NovaCart_Business_Analysis.xlsx"
    page.set_viewport_size({"width":390,"height":844})
    navigation.get_by_role("button",name="Overview").click()
    expect(page.get_by_role("heading",name="Financial summary")).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth === innerWidth")
    assert not errors, errors
    browser.close()
    print("PASS: 10 dashboard screens, date applied, Excel download, mobile width and no browser errors")
