const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

async function screenshot(reportPath, outputPath) {
  if (!fs.existsSync(reportPath)) {
    console.error('Report file not found:', reportPath);
    process.exit(1);
  }
  const absPath = path.resolve(reportPath);
  const fileUrl = 'file://' + absPath;

  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle2' });
  await page.setViewport({ width: 1200, height: 1600 });
  await page.screenshot({ path: outputPath, fullPage: true });
  await browser.close();
  console.log('Screenshot saved to', outputPath);
}

const report = process.argv[2] || 'report_html.html';
const out = process.argv[3] || 'zap_report.png';
screenshot(report, out).catch(err => {
  console.error(err);
  process.exit(1);
});
