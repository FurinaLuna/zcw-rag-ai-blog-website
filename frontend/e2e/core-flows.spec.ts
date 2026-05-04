import { test, expect } from "@playwright/test";

test.describe("前台核心流程", () => {
  test("首页加载正常", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("技术内容");
    await expect(page.locator("text=精选文章")).toBeVisible();
    await expect(page.locator("text=知识专题")).toBeVisible();
  });

  test("文章列表页加载正常", async ({ page }) => {
    await page.goto("/articles");
    await expect(page.locator("h1")).toContainText("文章");
    // 即使没数据也应该正常渲染
    await expect(page.locator("select >> nth=0")).toBeVisible();
  });

  test("导航到问答页可以输入问题", async ({ page }) => {
    await page.goto("/ask");
    await expect(page.locator("h1")).toContainText("智能问答");
    const input = page.locator('input[placeholder*="输入"]');
    await expect(input).toBeVisible();
    await input.fill("什么是Nuxt3");
    const btn = page.locator('button:has-text("提问")');
    await expect(btn).toBeVisible();
  });

  test("搜索页可以输入关键词", async ({ page }) => {
    await page.goto("/search");
    const input = page.locator('input[type="search"]');
    await expect(input).toBeVisible();
    await input.fill("Nuxt");
    await page.locator('button:has-text("搜索")').click();
    // 后端起不来会展示空结果，但页面不应崩溃
    await expect(page.locator("text=未找到")).toBeVisible({ timeout: 10000 });
  });

  test("关于页正常展示", async ({ page }) => {
    await page.goto("/about");
    await expect(page.locator("h1")).toContainText("关于");
    await expect(page.locator("text=Nuxt3")).toBeVisible();
  });

  test("专题列表页加载正常", async ({ page }) => {
    await page.goto("/topics");
    await expect(page.locator("h1")).toContainText("专题");
  });
});

test.describe("后台管理流程", () => {
  test("登录页加载正常", async ({ page }) => {
    await page.goto("/admin/login");
    await expect(page.locator("h1")).toContainText("登录");
    const usernameInput = page.locator("#username");
    const passwordInput = page.locator("#password");
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();

    // 空表单不应提交
    const btn = page.locator('button[type="submit"]');
    await expect(btn).toBeDisabled();
  });

  test("未登录访问后台跳转到登录页", async ({ page }) => {
    await page.goto("/admin");
    // CSR页面，等待重定向
    await page.waitForURL("**/admin/login", { timeout: 10000 });
    await expect(page.locator("h1")).toContainText("登录");
  });

  test("登录失败显示错误", async ({ page }) => {
    await page.goto("/admin/login");
    await page.fill("#username", "wrong");
    await page.fill("#password", "wrong");
    await page.locator('button[type="submit"]').click();
    await expect(page.locator("text=失败")).toBeVisible({ timeout: 10000 });
  });
});
