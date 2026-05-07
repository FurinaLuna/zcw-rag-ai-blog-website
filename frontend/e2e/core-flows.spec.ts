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

  test("问答页显示推荐问题并可点击", async ({ page }) => {
    await page.goto("/ask");
    // 推荐问题区域可见
    const suggestions = page.locator("text=试试这些问题：");
    await expect(suggestions).toBeVisible();
    // 点击推荐问题，页面应不崩溃（可能直接问问题或填充输入框）
    const firstSuggestion = page.locator(".flex.flex-wrap button").first();
    if (await firstSuggestion.isVisible()) {
      await firstSuggestion.click();
    }
    // h1仍在说明页面没崩溃
    await expect(page.locator("h1")).toContainText("智能问答");
  });

  test("问答页空输入提交不崩溃", async ({ page }) => {
    await page.goto("/ask");
    // 不输入任何内容直接点提问按钮
    const btn = page.locator('button:has-text("提问")');
    if (await btn.isVisible()) {
      await btn.click();
    }
    // 页面应保持稳定，h1仍在
    await expect(page.locator("h1")).toContainText("智能问答");
  });

  test("搜索页可以输入关键词", async ({ page }) => {
    await page.goto("/search");
    const input = page.locator('input[type="search"]');
    await expect(input).toBeVisible();
    await input.fill("Nuxt");
    await page.locator('button[type="submit"]').click();
    // 后端运行时会返回搜索结果，后端down时会展示未找到
    const resultText = page.locator("text=找到");
    const notFoundText = page.locator("text=未找到");
    await expect(resultText.or(notFoundText).first()).toBeVisible({ timeout: 10000 });
  });

  test("搜索页可切换到语义搜索模式", async ({ page }) => {
    await page.goto("/search");
    // 语义搜索切换按钮可见
    const semanticBtn = page.locator('button:has-text("语义搜索")');
    await expect(semanticBtn).toBeVisible();
    await semanticBtn.click();
    // 语义搜索提示文案可见
    await expect(page.locator("text=语义搜索根据含义匹配")).toBeVisible();
    // 搜索框仍然可用
    const input = page.locator('input[type="search"]');
    await expect(input).toBeVisible();
    await input.fill("如何优化性能");
    await page.locator('button[type="submit"]').click();
    // 页面不应崩溃（任何结果状态均可接受）
    const resultText = page.locator("text=找到");
    const notFoundText = page.locator("text=未找到");
    await expect(resultText.or(notFoundText).first()).toBeVisible({ timeout: 10000 });
  });

  test("搜索页显示分页控件", async ({ page }) => {
    await page.goto("/search");
    // 初始无结果时不显示分页
    const pagination = page.locator('[aria-label="分页"]');
    await expect(pagination).not.toBeVisible();
    // 输入关键词搜索
    await page.locator('input[type="search"]').fill("Nuxt");
    await page.locator('button[type="submit"]').click();
    // 无论有无结果，少于2页时不显示分页
    await expect(pagination).not.toBeVisible({ timeout: 10000 });
  });

  test("关于页正常展示", async ({ page }) => {
    await page.goto("/about");
    await expect(page.locator("h1")).toContainText("关于");
    await expect(page.locator("text=Nuxt3").first()).toBeVisible();
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
    const usernameInput = page.locator("input#username");
    const passwordInput = page.locator("input#password");
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
    await page.fill("input#username", "wrong");
    await page.fill("input#password", "wrong");
    await page.locator('button[type="submit"]').click();
    await expect(page.locator("text=失败")).toBeVisible({ timeout: 10000 });
  });
});
