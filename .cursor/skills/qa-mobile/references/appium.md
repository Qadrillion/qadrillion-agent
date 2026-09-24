# Appium and hybrid adaptation

Use the project's installed driver/client pair. Appium server version alone does
not establish driver compatibility. The reference machine has Appium 2.5.4 and
UiAutomator2 2.42.0; their installation was probed, but this task's reference
execution selects Maestro. Do not describe this adaptation as an Appium pass.

Inspect `appium --version`, `appium driver list --installed`, the client lockfile,
SDK/JDK and the selected driver's requirements. Bind a task-owned server to
localhost (`appium --address 127.0.0.1 --port 4723 --log "$EVIDENCE/appium.log"`
when that port is free). Do not enable relaxed security or automatic arbitrary
driver downloads to repair a session without understanding the missing feature.
Allocate separate driver ports for concurrent Android/iOS sessions.

For an installed Python client exposing `UiAutomator2Options`, the session shape
is below; values come from the target manifest, not guessed names:

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

options = UiAutomator2Options().load_capabilities({
    "platformName": "Android", "appium:automationName": "UiAutomator2",
    "appium:udid": serial, "appium:appPackage": package,
    "appium:appActivity": activity, "appium:noReset": True,
})
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
try:
    result = WebDriverWait(driver, 10).until(
        lambda session: session.find_element(AppiumBy.ID, observed_result_id))
    WebDriverWait(driver, 10).until(lambda _: result.text == expected_business_text)
finally:
    driver.quit()
```

The snippet only illustrates a session and assertion; author actual feature
actions and independent expected results. Set up data explicitly when using
`noReset`; do not silently carry prior test data. Re-query within waits for views
that can be replaced. Save screenshot/page source/logs **before** quitting after
a failure. A present element is weaker than correct resulting business state.

For iOS use the project's XCUITest driver/options and an exact simulator/device
UDID. Verify WebDriverAgent provisioning/signing on physical devices, selected
Xcode/runtime, bundle ID and the driver's supported iOS version. Appium's Android
driver does not supply iOS capabilities. Avoid blanket alert acceptance.

For embedded WebViews, record `driver.contexts`, wait for the intended observed
WebView context, switch with `driver.switch_to.context(context_name)`, then prove
DOM locators in that document. Verify WebView debugging availability and the
Chromedriver/WebView version pair. Return to the observed native context for OS
dialogs and native chrome. Context names and the presence of a WebView are not
stable identifiers; inspect on each transition. Never label browser-only tests
as native coverage. React Native/Flutter semantics and actual renderers determine
the usable locator path, not the framework name alone.

Sources inspected 2026-09-24: [Python client/session](https://appium.io/docs/en/2.19/quickstart/test-py/),
[UiAutomator2 2.42.0](https://github.com/appium/appium-uiautomator2-driver/blob/v2.42.0/README.md),
[context semantics](https://appium.io/docs/en/2.19/guides/context/).
