"""Browser tests for MES HTML app (30+ tests).

Covers: tab navigation, data input, analysis execution, all 5 tabs,
dark mode, about modal, keyboard accessibility, localStorage.
"""
import pytest
import time
import os
import sys
import io

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="module")
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    d = webdriver.Chrome(options=opts)
    d.set_window_size(1400, 900)
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "mes-app.html"))
    d.get("file:///" + app_path.replace("\\", "/"))
    time.sleep(3)  # Wait for Plotly CDN + init
    yield d
    d.quit()


def wait_for(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


# ========================================================================
# --- Tab Navigation (5 tests) ---
# ========================================================================

def test_tab1_visible_by_default(driver):
    """Tab 1 (Data Input) panel should be visible on load."""
    panel = driver.find_element(By.ID, "inputPanel")
    assert panel.is_displayed()


def test_all_5_tabs_exist(driver):
    """All 5 tab buttons should exist with role='tab'."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    assert len(tabs) == 5


def test_tab_aria_selected(driver):
    """First tab should have aria-selected='true' by default."""
    active = driver.find_element(By.CSS_SELECTOR, "[role='tab'][aria-selected='true']")
    assert active is not None
    assert active.get_attribute("data-tab") == "input"


def test_tab_panels_exist(driver):
    """All 5 tab panels should exist with role='tabpanel'."""
    panels = driver.find_elements(By.CSS_SELECTOR, "[role='tabpanel']")
    assert len(panels) == 5


def test_disabled_tabs_not_clickable(driver):
    """Tabs 2-5 should be disabled before analysis."""
    for tab_id in ["tabAssess", "tabExplore", "tabLandscape", "tabReport"]:
        tab = driver.find_element(By.ID, tab_id)
        assert tab.get_attribute("disabled") is not None


# ========================================================================
# --- Data Input (5 tests) ---
# ========================================================================

def test_built_in_dropdown_exists(driver):
    """Dataset selection dropdown should exist."""
    select = driver.find_element(By.ID, "datasetSelect")
    assert select is not None
    options = select.find_elements(By.TAG_NAME, "option")
    assert len(options) >= 5  # including the placeholder


def test_load_bcg(driver):
    """Loading BCG dataset should populate 13 rows."""
    select = driver.find_element(By.ID, "datasetSelect")
    for opt in select.find_elements(By.TAG_NAME, "option"):
        if "BCG" in opt.text or "bcg" in opt.text.lower():
            opt.click()
            break
    driver.find_element(By.ID, "loadDatasetBtn").click()
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 13


def test_study_count_display(driver):
    """Study count should show 13 after loading BCG."""
    count_el = driver.find_element(By.ID, "studyCount")
    assert count_el.text == "13"


def test_add_row(driver):
    """Adding a row should increment the table size."""
    initial = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    driver.find_element(By.ID, "addRowBtn").click()
    after = len(driver.find_elements(By.CSS_SELECTOR, "#dataBody tr"))
    assert after == initial + 1


def test_clear_table(driver):
    """Clearing the table should remove all rows."""
    driver.find_element(By.ID, "clearAllBtn").click()
    rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
    assert len(rows) == 0
    count_el = driver.find_element(By.ID, "studyCount")
    assert count_el.text == "0"


# ========================================================================
# --- Analysis Execution (5 tests) ---
# ========================================================================

def test_run_analysis_bcg(driver):
    """Load BCG and run analysis -- the most critical test."""
    # Load BCG
    select = driver.find_element(By.ID, "datasetSelect")
    for opt in select.find_elements(By.TAG_NAME, "option"):
        if "BCG" in opt.text:
            opt.click()
            break
    driver.find_element(By.ID, "loadDatasetBtn").click()
    time.sleep(1)

    # Run analysis
    driver.find_element(By.ID, "runBtn").click()
    # Wait for analysis to complete (progress overlay disappears)
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".progress-overlay.show"))
    )
    time.sleep(1)

    # Should switch to Tab 2 (assess) after analysis
    active_tab = driver.find_element(By.CSS_SELECTOR, "[role='tab'][aria-selected='true']")
    assert active_tab.get_attribute("data-tab") == "assess"


def test_no_js_errors_after_analysis(driver):
    """No SEVERE JavaScript errors should appear in browser console."""
    logs = driver.get_log("browser")
    errors = [l for l in logs if l["level"] == "SEVERE"]
    # Filter out known benign errors (e.g., favicon 404)
    real_errors = [e for e in errors if "favicon" not in e.get("message", "").lower()]
    assert len(real_errors) == 0, f"JS errors: {real_errors}"


def test_tabs_enabled_after_analysis(driver):
    """All tabs should be enabled after successful analysis."""
    for tab_id in ["tabAssess", "tabExplore", "tabLandscape", "tabReport"]:
        tab = driver.find_element(By.ID, tab_id)
        assert tab.get_attribute("disabled") is None, f"{tab_id} still disabled"


def test_verdict_appears(driver):
    """A robustness verdict should appear on Tab 4 (Evidence Landscape)."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[3].click()
    time.sleep(1)
    body = driver.find_element(By.TAG_NAME, "body").text
    assert any(w in body for w in ["ROBUST", "MODERATE", "FRAGILE", "UNSTABLE"]), \
        "No verdict class found in page text"
    # Switch back to Tab 2 for subsequent tests
    tabs[1].click()
    time.sleep(0.5)


def test_spec_count_reasonable(driver):
    """Specification count should be mentioned on Tab 3 (Multiverse Explorer)."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[2].click()
    time.sleep(1)
    body = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "specifications" in body or "executed" in body or "feasible" in body
    # Switch back to Tab 2 for subsequent tests
    tabs[1].click()
    time.sleep(0.5)


# ========================================================================
# --- Tab 2: Evidence Assessment (3 tests) ---
# ========================================================================

def test_tab2_rct_design(driver):
    """Tab 2 should mention RCT design type."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[1].click()
    time.sleep(1)
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "RCT" in body


def test_tab2_bias_profile(driver):
    """Tab 2 should show Egger's test result."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Egger" in body


def test_tab2_study_count(driver):
    """Tab 2 should show the study count (13 for BCG)."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "13" in body


# ========================================================================
# --- Tab 3: Multiverse Explorer (3 tests) ---
# ========================================================================

def test_tab3_has_plots(driver):
    """Tab 3 should contain Plotly plots (spec curve + Janus)."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[2].click()
    time.sleep(2)
    plots = driver.find_elements(By.CSS_SELECTOR, ".js-plotly-plot")
    assert len(plots) >= 2, f"Expected >= 2 plots, found {len(plots)}"


def test_tab3_concordance_metrics(driver):
    """Tab 3 should show concordance metrics."""
    body = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "concordance" in body or "feasible" in body


def test_tab3_dimensions_table(driver):
    """Tab 3 should show multiverse dimension info."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Estimator" in body or "estimator" in body


# ========================================================================
# --- Tab 4: Evidence Landscape (3 tests) ---
# ========================================================================

def test_tab4_traffic_light(driver):
    """Tab 4 should show a traffic light verdict."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[3].click()
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    assert any(w in body for w in ["ROBUST", "MODERATE", "FRAGILE", "UNSTABLE"])


def test_tab4_influence_chart(driver):
    """Tab 4 should contain at least one Plotly chart."""
    plots = driver.find_elements(By.CSS_SELECTOR, ".js-plotly-plot")
    assert len(plots) >= 1


def test_tab4_prediction_interval(driver):
    """Tab 4 should mention prediction intervals."""
    body = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "prediction" in body


# ========================================================================
# --- Tab 5: Report & Certify (4 tests) ---
# ========================================================================

def test_tab5_methods_text(driver):
    """Tab 5 should contain auto-generated methods text."""
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[4].click()
    time.sleep(1)
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Multiverse Evidence Synthesis" in body


def test_tab5_r_code(driver):
    """Tab 5 should contain R code with metafor."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "metafor" in body


def test_tab5_grade_mapping(driver):
    """Tab 5 should show GRADE-MES mapping."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "GRADE" in body


def test_tab5_certification_badge(driver):
    """Tab 5 should show a certification badge (PASS/WARN/BLOCK)."""
    body = driver.find_element(By.TAG_NAME, "body").text
    assert any(w in body for w in ["PASS", "WARN", "BLOCK"])


# ========================================================================
# --- Dark Mode (2 tests) ---
# ========================================================================

def test_dark_mode_toggle(driver):
    """Toggling dark mode should add/remove 'dark' class on body."""
    theme_btn = driver.find_element(By.ID, "themeBtn")
    theme_btn.click()
    time.sleep(0.5)
    body_classes = driver.find_element(By.TAG_NAME, "body").get_attribute("class")
    assert "dark" in body_classes
    # Toggle back
    theme_btn.click()
    time.sleep(0.5)
    body_classes = driver.find_element(By.TAG_NAME, "body").get_attribute("class")
    assert "dark" not in body_classes


def test_dark_mode_persists_in_localstorage(driver):
    """Theme preference should be saved to localStorage."""
    theme_btn = driver.find_element(By.ID, "themeBtn")
    theme_btn.click()
    time.sleep(0.3)
    stored = driver.execute_script("return localStorage.getItem('mes_theme');")
    assert stored == "dark"
    # Toggle back
    theme_btn.click()
    time.sleep(0.3)
    stored = driver.execute_script("return localStorage.getItem('mes_theme');")
    assert stored == "light"


# ========================================================================
# --- About Modal (3 tests) ---
# ========================================================================

def test_about_modal_opens(driver):
    """Clicking About button should open the About modal."""
    driver.find_element(By.ID, "aboutBtn").click()
    time.sleep(0.5)
    overlay = driver.find_element(By.ID, "aboutOverlay")
    assert "show" in overlay.get_attribute("class")
    # Check content
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "About MES" in body
    assert "v1.0.0" in body
    assert "AUTHOR_PLACEHOLDER" in body


def test_about_modal_closes_with_button(driver):
    """Clicking the close button should close the About modal."""
    driver.find_element(By.ID, "aboutCloseBtn").click()
    time.sleep(0.5)
    overlay = driver.find_element(By.ID, "aboutOverlay")
    assert "show" not in overlay.get_attribute("class")


def test_about_modal_closes_with_escape(driver):
    """Pressing Escape should close the About modal."""
    driver.find_element(By.ID, "aboutBtn").click()
    time.sleep(0.5)
    overlay = driver.find_element(By.ID, "aboutOverlay")
    assert "show" in overlay.get_attribute("class")
    # Press Escape
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    time.sleep(0.5)
    assert "show" not in overlay.get_attribute("class")


# ========================================================================
# --- Keyboard Accessibility (2 tests) ---
# ========================================================================

def test_tab_keyboard_arrow_navigation(driver):
    """Arrow keys should navigate between tabs."""
    # Focus on the current active tab (Tab 5 from previous tests)
    # First switch to Tab 1
    tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
    tabs[0].click()
    time.sleep(0.5)

    # Tab 1 should be active
    assert driver.find_element(By.ID, "tabInput").get_attribute("aria-selected") == "true"

    # Press ArrowRight -- should go to Tab 2 (which is enabled after analysis)
    tabs[0].send_keys(Keys.ARROW_RIGHT)
    time.sleep(0.5)
    active = driver.find_element(By.CSS_SELECTOR, "[role='tab'][aria-selected='true']")
    assert active.get_attribute("data-tab") == "assess"


def test_tab_keyboard_arrow_left(driver):
    """ArrowLeft should go to the previous tab."""
    active = driver.find_element(By.CSS_SELECTOR, "[role='tab'][aria-selected='true']")
    active.send_keys(Keys.ARROW_LEFT)
    time.sleep(0.5)
    new_active = driver.find_element(By.CSS_SELECTOR, "[role='tab'][aria-selected='true']")
    assert new_active.get_attribute("data-tab") == "input"


# ========================================================================
# --- All Datasets Load (1 test) ---
# ========================================================================

def test_all_datasets_load(driver):
    """All 4 built-in datasets should load without errors."""
    select = driver.find_element(By.ID, "datasetSelect")
    options = select.find_elements(By.TAG_NAME, "option")
    # Should have at least 5 options (1 placeholder + 4 datasets)
    assert len(options) >= 5

    expected = {
        "bcg": 13,
        "robust": 61,
        "fragile": 14,
        "unstable": 5,
    }
    for val, expected_count in expected.items():
        for opt in options:
            if opt.get_attribute("value") == val:
                opt.click()
                break
        driver.find_element(By.ID, "loadDatasetBtn").click()
        time.sleep(0.5)
        rows = driver.find_elements(By.CSS_SELECTOR, "#dataBody tr")
        assert len(rows) == expected_count, \
            f"Dataset '{val}': expected {expected_count} rows, got {len(rows)}"


# ========================================================================
# --- ARIA Attributes (2 tests) ---
# ========================================================================

def test_tab_panels_have_aria_labelledby(driver):
    """Each tabpanel should have aria-labelledby pointing to its tab."""
    panel_ids = ["inputPanel", "assessPanel", "explorePanel", "landscapePanel", "reportPanel"]
    tab_ids = ["tabInput", "tabAssess", "tabExplore", "tabLandscape", "tabReport"]
    for panel_id, tab_id in zip(panel_ids, tab_ids):
        panel = driver.find_element(By.ID, panel_id)
        assert panel.get_attribute("aria-labelledby") == tab_id, \
            f"{panel_id} missing aria-labelledby={tab_id}"


def test_buttons_have_aria_labels(driver):
    """Key buttons should have aria-label attributes."""
    buttons_with_labels = ["aboutBtn", "themeBtn", "loadDatasetBtn",
                           "addRowBtn", "clearAllBtn", "runBtn", "importCsvBtn"]
    for btn_id in buttons_with_labels:
        btn = driver.find_element(By.ID, btn_id)
        label = btn.get_attribute("aria-label")
        assert label and len(label) > 0, f"Button {btn_id} missing aria-label"
